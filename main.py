from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import urllib.parse
import os
from bson import ObjectId 

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# MongoDB connection setup with URL-encoded username and password
username = "testuser"
password = "test"
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)
mongo_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@clusterkichu.p8zqdyu.mongodb.net/"

client = MongoClient(mongo_uri)
db = client["logindata"]
users_collection = db["users"]

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        session["authenticated"] = True
        return "Login successful. Welcome to the dashboard!"
    else:
        flash("Login failed. Invalid credentials.", "error")
        return redirect("/")

@app.route("/register", methods=["POST"])
def register():
    new_username = request.form.get("new_username")
    new_password = request.form.get("new_password")
    
    # Check if the username already exists
    existing_user = users_collection.find_one({"username": new_username})
    
    if existing_user:
        return "Registration failed. Username already exists."
    else:
        # Create a new user document and insert it into the MongoDB collection
        new_user = {"username": new_username, "password": new_password}
        users_collection.insert_one(new_user)
        return "Registration successful. You can now log in."

# Admin Section

@app.route("/admin")
def admin():
    # Check if the user is authenticated as admin
    if not session.get("admin_authenticated"):
        flash("Access denied. Please log in as admin.", "error")
        return redirect("/admin/login")

    # Retrieve user data from the MongoDB collection
    users_data = list(users_collection.find({}, {"_id": 1, "username": 1, "password": 1}))
    return render_template("admin.html", users=users_data)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    # Check if the user is authenticated as admin
    if not session.get("admin_authenticated"):
        flash("Access denied. Please log in as admin.", "error")
        return redirect("/admin/login")

    # Retrieve new user data from the form
    new_username = request.form.get("new_username")
    new_password = request.form.get("new_password")

    # Create a new user document and insert it into the MongoDB collection
    new_user = {"username": new_username, "password": new_password}
    users_collection.insert_one(new_user)

    return redirect("/admin")

@app.route("/admin/delete/<user_id>", methods=["POST"])
def admin_delete(user_id):
    # Check if the user is authenticated as admin
    if not session.get("admin_authenticated"):
        flash("Access denied. Please log in as admin.", "error")
        return redirect("/admin/login")

    # Delete the user based on the provided user_id
    users_collection.delete_one({"_id": ObjectId(user_id)})
    
    return redirect("/admin")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_username = request.form.get("admin_username")
        admin_password = request.form.get("admin_password")

        # Add logic to validate admin credentials here
        # For example, you can hardcode admin credentials for simplicity
        if admin_username == "admin" and admin_password == "admin":
            session["admin_authenticated"] = True
            return redirect("/admin")
        else:
            flash("Invalid admin credentials. Please try again.", "error")

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    # Log out the admin user
    session.pop("admin_authenticated", None)
    return redirect("/admin/login")

if __name__ == "__main__":
    app.run(debug=True)
