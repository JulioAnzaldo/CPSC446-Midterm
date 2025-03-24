from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, jsonify, request
import mysql.connector, re, datetime, secrets, os
from werkzeug.utils import secure_filename

app = Flask(
    __name__,
    template_folder = "../front_end/templates",
    static_folder = "../front_end/static"
)

# Generate a secure secret key, would not be hardcoded in production
app.config['SECRET_KEY'] = secrets.token_hex(32)  # 32-byte hex key

# Set the upload folder path
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Maximum allowed payload to 2MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB

jwt = JWTManager(app)

# Get database connection
def get_db_connection():
    # Connect to the database
    db = mysql.connector.connect(
    host = "localhost", # Hostname
    user = "root", # Username
    password = "Anzaldo1", # Password
    database = "CPSC446" # Database name
    )
    return db

# Allowed filenames
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("use CPSC446")

    return render_template("index.html")

@app.route('/register', methods = ['POST'])
def register():

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # Validate username (only letters, numbers, and underscores, 3-20 chars)
    if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
        return jsonify({"error": "Invalid username. Use 3-20 characters (letters, numbers, underscores only)."}), 400

    # Hash password before storing
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user[1], password):  # Verify stored hash
        access_token = create_access_token(identity = str(user[0]), expires_delta = datetime.timedelta(hours = 1))
        return jsonify({"access_token": access_token})
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/protected', methods = ['GET'])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({"message": f"Welcome, user {user_id}. This is a protected route."})

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    # Ensure the file part is present in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Ensure a file is selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Validate the file type
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Secure the filename and define the file path
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the file
    file.save(file_path)

    # Determine if the file should be public; default is private if not provided
    # (Using form data: e.g., is_public = "true" or "false")
    is_public = request.form.get('is_public', 'false').lower() == 'true'

    # Get the file size
    file_size = os.path.getsize(file_path)

    # Insert file metadata into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO files (user_id, file_name, file_path, file_size, file_type, is_public) VALUES (%s, %s, %s, %s, %s, %s)",
            (get_jwt_identity(), filename, file_path, file_size, 'pdf', is_public)
        )
        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "File uploaded successfully", "is_public": is_public}), 201


@app.route('/public_files', methods = ['GET'])
def public_files():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT file_name, file_path, file_size, uploaded_at FROM files WHERE is_public = 1")
        files = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify(files)


if __name__ == "__main__":
    app.run(debug = True)