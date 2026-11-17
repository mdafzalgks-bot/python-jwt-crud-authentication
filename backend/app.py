from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
import os
from dotenv import load_dotenv
import datetime
import jwt
import mysql.connector
from flask_cors import CORS
from flask import Flask, request, jsonify
from functools import wraps


load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# JWT Authentication
def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Token is missing!"}), 401

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"message": "Invalid token format!"}), 401

        token = parts[1]

        try:
            data = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user_id = data["user_id"]

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated


# Home API
@app.route("/")
def home():

    return jsonify({
        "message": "JWT CRUD Backend Running Successfully"
    })


# Register API (Create)
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "username, email and password are required"}), 400

    hashed_password = generate_password_hash(password)

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()

        return jsonify({"message": "User registered successfully!"}), 201

    except mysql.connector.IntegrityError:
        return jsonify({"message": "Username or email already exists"}), 409

    except Exception as e:
        print("Register error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Login API
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

    except Exception as e:
        print("Login error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if user and check_password_hash(user["password"], password):

        token = jwt.encode(
            {
                "user_id": user["id"],
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=48)
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        return jsonify({
            "message": "Login successful!",
            "username": user["username"],
            "token": token
        })

    return jsonify({"message": "Invalid email or password"}), 401


# Protected Profile API (Read)
@app.route("/profile", methods=["GET"])
@token_required
def profile(current_user_id):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (current_user_id,)
        )
        user = cursor.fetchone()

    except Exception as e:
        print("Profile error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    if not user:
        return jsonify({"message": "User not found!"}), 404

    return jsonify({
        "message": "Access granted!",
        "user": user
    })


# Update Profile API (Update)
@app.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    username = data.get("username")
    email = data.get("email")

    if not username or not email:
        return jsonify({"message": "username and email are required"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET username = %s, email = %s WHERE id = %s",
            (username, email, current_user_id)
        )
        conn.commit()

        return jsonify({"message": "Profile updated successfully!"})

    except mysql.connector.IntegrityError:
        return jsonify({"message": "Username or email already exists"}), 409

    except Exception as e:
        print("Update error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Delete Account API (Delete)
@app.route("/profile", methods=["DELETE"])
@token_required
def delete_profile(current_user_id):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id = %s", (current_user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "User not found!"}), 404

        return jsonify({"message": "Account deleted successfully!"})

    except Exception as e:
        print("Delete error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Get all customers of logged-in user (Read)
@app.route("/customers", methods=["GET"])
@token_required
def get_customers(current_user_id):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, email, age FROM customers WHERE user_id = %s ORDER BY id",
            (current_user_id,)
        )
        customers = cursor.fetchall()

        return jsonify(customers)

    except Exception as e:
        print("Get customers error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Add customer (Create)
@app.route("/customers", methods=["POST"])
@token_required
def add_customer(current_user_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")

    if not name or not email or age is None:
        return jsonify({"message": "name, email and age are required"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO customers (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
            (current_user_id, name, email, age)
        )
        conn.commit()

        return jsonify({"message": "Customer added successfully!"}), 201

    except Exception as e:
        print("Add customer error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Update customer (Update)
@app.route("/customers/<int:customer_id>", methods=["PUT"])
@token_required
def update_customer(current_user_id, customer_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")

    if not name or not email or age is None:
        return jsonify({"message": "name, email and age are required"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM customers WHERE id = %s AND user_id = %s",
            (customer_id, current_user_id)
        )

        if not cursor.fetchone():
            return jsonify({"message": "Customer not found!"}), 404

        cursor.execute(
            "UPDATE customers SET name = %s, email = %s, age = %s WHERE id = %s AND user_id = %s",
            (name, email, age, customer_id, current_user_id)
        )
        conn.commit()

        return jsonify({"message": "Customer updated successfully!"})

    except Exception as e:
        print("Update customer error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Delete customer (Delete)
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
@token_required
def delete_customer(current_user_id, customer_id):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM customers WHERE id = %s AND user_id = %s",
            (customer_id, current_user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Customer not found!"}), 404

        return jsonify({"message": "Customer deleted successfully!"})

    except Exception as e:
        print("Delete customer error:", e)
        return jsonify({"message": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Run Flask
if __name__ == "__main__":
    app.run(debug=True)
