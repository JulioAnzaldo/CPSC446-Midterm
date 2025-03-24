# CPSC 446 Midterm Project - Julio Anzaldo

A **Flask RESTful API** demonstrating authentication, file handling, and public/private routes. Users can register, log in, upload PDF files, and mark them as public or private. Public files are viewable through a dedicated endpoint without authentication.

---

## 1. Project Overview

This project was created for **CPSC 446** to demonstrate:
- **Error Handling:** Custom error handlers for common HTTP status codes.  
- **JWT Authentication:** Users can log in to receive a JWT token, which is required for protected routes.  
- **File Handling:** Upload PDF files with file size limits and type checks.  
- **Public vs. Private Files:** Users can mark files as public, which are then listed on a public route.

---

## 2. Features

1. **User Registration**  
   - Validates usernames (3-20 characters, alphanumeric + underscore).  
   - Hashes passwords before storing in the database.

2. **User Login**  
   - Returns a JWT access token upon successful authentication.  
   - Token must be included in the `Authorization` header (Bearer token) for protected endpoints.

3. **Error Handling**  
   - Custom JSON responses for 400, 401, 404, and 500 errors.

4. **File Upload**  
   - Only PDF files are allowed.  
   - File size limited to 2 MB (configurable).  
   - Can be marked as public or private.

5. **Public Route**  
   - Lists all files marked as public.  
   - Does not require authentication.

---

## 3. Technologies Used

- **Python 3.10+**  
- **Flask** (web framework)  
- **mysql-connector-python** (database connector)  
- **Flask-JWT-Extended** (JWT authentication)  
- **Werkzeug** (password hashing & secure filename)  
- **MySQL** (database)

---

## 4. File Structure

```
my_project/ 
    ├── back_end/
        ├── uploads/ # Folder that holds user uploads (PDF's)
        └── app.py # Main Flask app (routes, config, etc.) 
    ├── requirements.txt # Python dependencies │ 
    ├── venv/ # Virtual environment (not tracked in Git) 
    └── README.md # This readme file
```

## 5. Installation and Setup

Follow these steps to set up the project on your local machine.

### Prerequisites
Make sure you have the following installed:
- **Python 3.x** (Check with `python --version` or `python3 --version`)
- **pip** (Check with `pip --version`)
- **virtualenv** (Optional but recommended)

### Setup Instructions

1. **Clone the Repository**
   ```sh
   git clone https://github.com/JulioAnzaldo/CPSC446-Midterm
   cd CPSC446-Midterm
   ```
2. **Create a Virtual Environment**
   ```sh
   python -m venv venv
   ```
3. **Activate the Virtual Environment**
   
      Windows (Command Prompt or PowerShell)
      ```
      venv\Scripts\activate
      ```
      
      Mac/Linux
      ```
      source venv/bin/activate
      ```

5. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

6. **Run the Application**
   ```sh
   python app.py
   ```

## 6. API Routes

### **Authentication Routes**
| Method | Endpoint       | Description |
|--------|--------------|-------------|
| **POST** | `/register` | Registers a new user. Accepts `username`, `email` and `password` in JSON. |
| **POST** | `/login` | Logs in a user and returns a JWT token. Requires `username` and `password`. |

---

### **Protected Routes (Require JWT)**
| Method | Endpoint       | Description |
|--------|--------------|-------------|
| **POST** | `/upload` | Allows an authenticated user to upload a PDF file. Accepts `file` (PDF only) and `is_public` (`true` or `false`). |
| **GET** | `/protected` | A protected route that requires a valid JWT token to access. Returns a message confirming the authenticated user. |

---

### **Public Routes (No Authentication Required)**
| Method | Endpoint       | Description |
|--------|--------------|-------------|
| **GET** | `/` | Serves the front-end homepage (if applicable, but not sure at this point). |
| **GET** | `/public_files` | Returns a list of all publicly available files. |

---

### **Usage Notes**
- **JWT Authentication:**  
  - Routes marked as **protected** require the `Authorization` header with a Bearer token:  
    ```
    Authorization: Bearer YOUR_JWT_TOKEN
    ```
- **File Upload Requirements:**  
  - Only **PDF** files are allowed.
  - Maximum file size: **2MB**.
  - The `is_public` field determines if the file is visible in `/public_files`.

## Secret Key Setup
By default, this project uses a demo secret key in app.py. In a production environment, we would load this key from an environment variable or a .env file. For the purposes of this assignment, you can leave the demo key as-is.
