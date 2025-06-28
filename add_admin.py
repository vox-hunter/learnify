import pymongo
from mongo_auth import get_database

def add_admin(username, email):
    """Adds a new admin user to the database."""
    db = get_database()
    users_collection = db["users"]

    # Check if the user already exists
    if users_collection.find_one({"username": username}):
        print(f"User '{username}' already exists.")
        return

    # Add the new admin user
    users_collection.insert_one({
        "username": username,
        "email": email,
        "role": "admin"
    })
    print(f"Admin user '{username}' added successfully.")

if __name__ == "__main__":
    # Replace with the desired admin username and email
    add_admin("vox", "vidyutsanthosh4@gmail.com")
