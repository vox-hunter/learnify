import os
import pymongo
from pymongo import errors as pymongo_errors
import bcrypt  # For password hashing
from datetime import datetime  # For timestamps
from dotenv import load_dotenv

# Try to import streamlit, but make it optional
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Load environment variables from multiple possible locations
api_env_path = os.path.join(os.path.dirname(__file__), '..', 'api', '.env')
if os.path.exists(api_env_path):
    load_dotenv(api_env_path)
else:
    load_dotenv()

def _log_error(message):
    """Log error using Streamlit if available, otherwise use print/logging"""
    if STREAMLIT_AVAILABLE:
        st.error(message)
    else:
        print(f"ERROR: {message}")

# It's good practice to load secrets at the beginning and provide clear error messages if they are missing.
MONGODB_URI = None
DB_NAME = "learnify_auth"  # Or get from secrets if it varies
USER_COLLECTION = "users"

# Try Streamlit secrets first
if STREAMLIT_AVAILABLE:
    try:
        MONGODB_URI = st.secrets["MONGODB_URI"]
        DB_NAME = st.secrets.get("DB_NAME", "learnify_auth")
    except (KeyError, FileNotFoundError, AttributeError, Exception):
        pass  # Fall through to environment variables

# Fallback to environment variables
if not MONGODB_URI:
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("DB_NAME", "learnify_auth")

if not MONGODB_URI:
    error_msg = "Missing MONGODB_URI. Please ensure MONGODB_URI is set in your environment variables or Streamlit secrets."
    if STREAMLIT_AVAILABLE:
        _log_error(error_msg)
        st.stop()
    else:
        raise ValueError(error_msg)

class MongoAuthManager:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGODB_URI)
            self.db = self.client[DB_NAME]
            self.users_collection = self.db[USER_COLLECTION]
            # Test connection
            self.client.admin.command('ping')
        except pymongo_errors.ConfigurationError as e:
            error_msg = f"MongoDB Configuration Error: {e}. Please check your MONGODB_URI."
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.users_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)
        except pymongo_errors.ConnectionFailure as e:
            error_msg = f"Failed to connect to MongoDB: {e}"
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.users_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred during MongoDB initialization: {e}"
            _log_error(error_msg)
            self.client = None
            self.db = None
            self.users_collection = None
            if STREAMLIT_AVAILABLE:
                st.stop()
            else:
                raise RuntimeError(error_msg)


    def _ensure_connection(self):
        if self.client is None or self.db is None or self.users_collection is None:
            _log_error("MongoDB connection is not available.")
            return False
        try:
            # Ping the database to ensure the connection is active
            self.client.admin.command('ping')
            return True
        except pymongo_errors.ConnectionFailure:
            _log_error("MongoDB connection lost. Please try again later.")
            # Optionally, try to reconnect here
            return False

    def hash_password(self, password):
        # Hash a password for storing.
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8') # Store as string

    def verify_password(self, plain_password, hashed_password):
        # Check hashed password. Using .encode('utf-8') for both.
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ValueError:
            # Invalid salt/hash format (corrupted or not bcrypt)
            return False

    def add_user(self, username, password, email, name, marketing_consent=False, google_id=None, google_linked=False):
        if not self._ensure_connection():
            return None, "Database connection error."
        if self.users_collection.find_one({"username": username}):
            return None, "Username already exists."
        if self.users_collection.find_one({"email": email}):
            return None, "Email already registered."
        
        # If password is provided, hash it. For Google OAuth users, password might be None initially
        hashed_pw = self.hash_password(password) if password else None
        
        try:
            user_data = {
                "username": username,
                "password": hashed_pw,
                "email": email,
                "name": name,
                "email_verified": google_linked,  # Google accounts are pre-verified
                "marketing_consent": marketing_consent,
                "created_at": datetime.utcnow().isoformat(),
                "google_id": google_id,  # Store Google ID for linking
                "google_linked": google_linked,  # Flag to indicate if account is linked to Google
                "gemini_oauth": None  # Placeholder for Gemini OAuth credentials (to be set separately)
            }
            result = self.users_collection.insert_one(user_data)
            return result.inserted_id, None
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error adding user: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error adding user: {e}")
            return None, f"An unexpected error occurred: {e}"

    def find_user_by_username(self, username):
        """Find user by username OR email (for flexible login)"""
        if not self._ensure_connection():
            return None
        try:
            # Try to find by username first, then by email
            user = self.users_collection.find_one({"username": username})
            if not user:
                # If not found by username, try email
                user = self.users_collection.find_one({"email": username})
            return user
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error finding user by username/email: {e}")
            return None
        except Exception as e:
            _log_error(f"Unexpected error finding user: {e}")
            return None
            
    def find_user_by_email(self, email):
        if not self._ensure_connection():
            return None
        try:
            return self.users_collection.find_one({"email": email})
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error finding user by email: {e}")
            return None
        except Exception as e:
            _log_error(f"Unexpected error finding user by email: {e}")
            return None

    def find_user_by_google_id(self, google_id):
        """Find user by Google ID."""
        if not self._ensure_connection():
            return None
        try:
            return self.users_collection.find_one({"google_id": google_id})
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error finding user by Google ID: {e}")
            return None
        except Exception as e:
            _log_error(f"Unexpected error finding user by Google ID: {e}")
            return None

    def link_google_account(self, username, google_id):
        """Link a Google account to an existing user."""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        # Check if Google ID is already linked to another account
        existing_google_user = self.find_user_by_google_id(google_id)
        if existing_google_user and existing_google_user['username'] != username:
            return False, "This Google account is already linked to another user."
        
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "google_id": google_id,
                        "google_linked": True,
                        "email_verified": True  # Google accounts are verified
                    }
                }
            )
            if result.modified_count > 0:
                return True, None
            else:
                return False, "User not found or account already linked."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error linking Google account: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error linking Google account: {e}")
            return False, f"An unexpected error occurred: {e}"

    def unlink_google_account(self, username):
        """Unlink Google account from user."""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {
                    "$unset": {"google_id": 1},
                    "$set": {"google_linked": False}
                }
            )
            if result.modified_count > 0:
                return True, None
            else:
                return False, "User not found or Google account not linked."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error unlinking Google account: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error unlinking Google account: {e}")
            return False, f"An unexpected error occurred: {e}"

    def create_google_user(self, google_user_info, base_username, marketing_consent=False):
        """
        Create a new user from Google OAuth information.
        
        Args:
            google_user_info: Dictionary containing Google user data
            base_username: Base username to use (will be made unique if needed)
            marketing_consent: Whether user consented to marketing emails
            
        Returns:
            tuple: (user_id, error_message, final_username)
        """
        if not self._ensure_connection():
            return None, "Database connection error.", None
        
        email = google_user_info.get('email')
        name = google_user_info.get('name')
        google_id = google_user_info.get('google_id')
        
        if not email or not google_id:
            return None, "Invalid Google user information.", None
        
        # Check if email already exists
        if self.users_collection.find_one({"email": email}):
            return None, "Email already registered.", None
        
        # Make username unique if needed
        final_username = self._generate_unique_username(base_username)
        
        try:
            user_data = {
                "username": final_username,
                "password": None,  # No password for Google OAuth users initially
                "email": email,
                "name": name,
                "email_verified": True,  # Google accounts are pre-verified
                "marketing_consent": marketing_consent,
                "created_at": datetime.utcnow().isoformat(),
                "google_id": google_id,
                "google_linked": True
            }
            result = self.users_collection.insert_one(user_data)
            return result.inserted_id, None, final_username
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error creating Google user: {e}")
            return None, f"Database error: {e}", None
        except Exception as e:
            _log_error(f"Unexpected error creating Google user: {e}")
            return None, f"An unexpected error occurred: {e}", None

    def _generate_unique_username(self, base_username):
        """Generate a unique username by appending numbers if needed."""
        if not self._ensure_connection():
            return base_username
        
        original_username = base_username
        counter = 1
        
        while self.users_collection.find_one({"username": base_username}):
            base_username = f"{original_username}{counter}"
            counter += 1
        
        return base_username

    def update_user_password(self, username, new_password):
        if not self._ensure_connection():
            return False, "Database connection error."
        hashed_pw = self.hash_password(new_password)
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {"$set": {"password": hashed_pw}}
            )
            if result.modified_count > 0:
                return True, None
            else:
                return False, "User not found or password not updated."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error updating password: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error updating password: {e}")
            return False, f"An unexpected error occurred: {e}"

    def update_user_password_by_email(self, email, new_password):
        """Update user password by email address (for password reset)"""
        if not self._ensure_connection():
            return False, "Database connection error."
        hashed_pw = self.hash_password(new_password)
        try:
            result = self.users_collection.update_one(
                {"email": email},
                {"$set": {"password": hashed_pw}}
            )
            if result.modified_count > 0:
                return True, None
            else:
                return False, "User not found or password not updated."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error updating password: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error updating password: {e}")
            return False, f"An unexpected error occurred: {e}"

    def update_user_details(self, username, updates):
        # Updates should be a dict of fields to update, e.g., {"name": "New Name", "email": "new@example.com"}
        if not self._ensure_connection():
            return False, "Database connection error."
        
        # Prevent password updates through this method; use update_user_password for that.
        if "password" in updates:
            return False, "Password updates should be done via update_user_password."
        
        # If username is being updated, check if the new username already exists
        if "username" in updates:
            existing_user = self.users_collection.find_one({"username": updates["username"]})
            if existing_user and existing_user["username"] != username:
                return False, "Username already taken, Please choose another one"
        
        # If email is being updated, check if the new email already exists for another user
        if "email" in updates:
            existing_user = self.users_collection.find_one({"email": updates["email"]})
            if existing_user and existing_user["username"] != username:
                return False, "Email already registered by another user."

        try:
            result = self.users_collection.update_one(
                {"username": username},
                {"$set": updates}
            )
            if result.modified_count > 0:
                return True, None
            elif result.matched_count > 0: # Matched but no changes made
                return True, "No changes detected." 
            else:
                return False, "User not found."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error updating user details: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error updating user details: {e}")
            return False, f"An unexpected error occurred: {e}"

    # --- Config loading/saving methods (adapted from original 2_🔐_Login.py) ---
    # These methods were originally in 2_🔐_Login.py and are related to 'authenticate.yaml'
    # If you intend to fully replace YAML config with MongoDB for auth, these might need rethinking.
    # For now, I'm including them as they were, assuming they might still be used for other configs
    # or if the 'credentials' part of the config is now managed directly via user documents.

    def load_config(self):
        """Load authentication config from MongoDB (e.g., for settings beyond user credentials).
           This function might need to be adapted based on what 'config' means in your new system.
           If it's purely user credentials, this might become simpler or be replaced by direct user lookups.
        """
        if not self._ensure_connection():
            return None
        try:
            # Assuming you have a 'config' collection and a specific document for auth settings
            # This is a placeholder; adjust to your actual config storage strategy in MongoDB
            config_doc = self.db.config_collection.find_one({"name": "authenticator_config"})
            if config_doc:
                # Remove MongoDB's _id field if you don't want it in the config dict
                config_doc.pop('_id', None)
                return config_doc
            return None # Or return a default config dict
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error loading config: {e}")
            return None
        except Exception as e:
            _log_error(f"Unexpected error loading config from MongoDB: {e}")
            return None

    def save_config(self, config_data):
        """Save config to MongoDB.
           Similar to load_config, adapt based on your needs.
        """
        if not self._ensure_connection():
            return False
        try:
            # Upsert the config document
            self.db.config_collection.update_one(
                {"name": "authenticator_config"},
                {"$set": config_data},
                upsert=True
            )
            return True
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error saving config: {e}")
            return False
        except Exception as e:
            _log_error(f"Unexpected error saving config to MongoDB: {e}")
            return False

    # --- Email Verification Methods ---
    def store_verification_code(self, email, code, purpose="registration", expires_in_minutes=10):
        """
        Store verification code in database
        
        Args:
            email: User email
            code: Verification code
            purpose: 'registration' or 'password_reset'
            expires_in_minutes: Code expiration time
          Returns:
            tuple: (success: bool, error_message: str)
        """
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            from datetime import timedelta
            expiry_time = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
            verification_data = {
                "email": email,
                "code": code,
                "purpose": purpose,
                "created_at": datetime.utcnow(),
                "expires_at": expiry_time,
                "used": False
            }
            
            # Remove any existing verification codes for this email and purpose
            self.db.verification_codes.delete_many({
                "email": email,
                "purpose": purpose
            })
            
            # Insert new verification code
            result = self.db.verification_codes.insert_one(verification_data)
            return True, None
            
        except Exception as e:
            _log_error(f"Error storing verification code: {e}")
            return False, f"Database error: {e}"
    
    def verify_code(self, email, entered_code, purpose="registration"):
        """
        Verify the entered code against stored code
        
        Args:
            email: User email
            entered_code: Code entered by user
            purpose: 'registration' or 'password_reset'
          Returns:
            tuple: (success: bool, error_message: str)
        """
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            # Find the verification code
            verification_doc = self.db.verification_codes.find_one({
                "email": email,
                "purpose": purpose,
                "used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not verification_doc:
                return False, "Invalid or expired verification code."
            
            # Check if codes match
            if verification_doc["code"] != int(entered_code):
                return False, "Incorrect verification code."
            
            # Mark code as used
            self.db.verification_codes.update_one(
                {"_id": verification_doc["_id"]},
                {"$set": {"used": True}}
            )
            
            return True, None
        except ValueError:
            return False, "Invalid code format."
        except Exception as e:
            _log_error(f"Error verifying code: {e}")
            return False, f"Database error: {e}"

    def mark_email_verified(self, email):
        """Mark user's email as verified"""
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            result = self.users_collection.update_one(
                {"email": email},
                {"$set": {"email_verified": True}}
            )
            return result.modified_count > 0, None
        except Exception as e:
            _log_error(f"Error marking email as verified: {e}")
            return False, f"Database error: {e}"
    
    def cleanup_expired_codes(self):
        """Remove expired verification codes"""
        if not self._ensure_connection():
            return
        
        try:
            self.db.verification_codes.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
        except Exception as e:
            _log_error(f"Error cleaning up expired codes: {e}")

    def delete_user_account(self, username, confirm_username):
        """
        Delete a user account and all associated data after confirmation
        
        Args:
            username: Username of the account to delete
            confirm_username: Confirmation username (must match username)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self._ensure_connection():
            return False, "Database connection error."
        
        # Verify confirmation
        if username != confirm_username:
            return False, "Username confirmation does not match. Account deletion cancelled."
        
        # Check if user exists
        user_doc = self.find_user_by_username(username)
        if not user_doc:
            return False, "User not found."
        
        try:
            # Start a transaction to ensure data consistency
            with self.client.start_session() as session:
                with session.start_transaction():
                    # Delete user from users collection
                    user_result = self.users_collection.delete_one(
                        {"username": username}, 
                        session=session
                    )
                    
                    if user_result.deleted_count == 0:
                        session.abort_transaction()
                        return False, "Failed to delete user account."
                    
                    # Delete associated courses from courses database
                    # We need to access the courses database
                    courses_db = self.client["learnify_courses"]  # Course database name
                    courses_collection = courses_db["courses"]
                    user_courses_collection = courses_db["user_courses"]
                    
                    # Delete all courses created by this user
                    courses_result = courses_collection.delete_many(
                        {"creator": username, "is_guest": False}, 
                        session=session
                    )
                    
                    # Delete user course associations
                    user_courses_result = user_courses_collection.delete_many(
                        {"user_identifier": username}, 
                        session=session
                    )
                    
                    # Delete verification codes (if any) - cleanup orphaned verification entries
                    self.users_collection.delete_many(
                        {"username": username, "verification_code": {"$exists": True}}, 
                        session=session
                    )
                    
                    # Commit the transaction
                    session.commit_transaction()
                    
                    return True, f"Account deleted successfully. Removed {courses_result.deleted_count} courses and {user_courses_result.deleted_count} course associations."
                    
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error deleting account: {e}")
            return False, f"Database error: {e}"
        except (ValueError, TypeError, AttributeError) as e:
            _log_error(f"Error deleting account: {e}")
            return False, f"Error during account deletion: {e}"
        except Exception as e:  # pylint: disable=broad-except
            _log_error(f"Unexpected error deleting account: {e}")
            return False, f"An unexpected error occurred: {e}"

    # --- Gemini OAuth Methods ---
    def store_gemini_oauth(self, username, oauth_data):
        """
        Store Gemini OAuth credentials for a user.
        
        Args:
            username: Username to store credentials for
            oauth_data: Dictionary containing:
                - access_token: OAuth access token
                - refresh_token: OAuth refresh token
                - token_uri: Token endpoint URI
                - client_id: OAuth client ID
                - client_secret: OAuth client secret
                - expiry: Token expiration (ISO format string)
                - quota_project_id: Project ID for quota billing
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {"$set": {"gemini_oauth": oauth_data}}
            )
            if result.modified_count > 0 or result.matched_count > 0:
                return True, None
            else:
                return False, "User not found."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error storing Gemini OAuth: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error storing Gemini OAuth: {e}")
            return False, f"An unexpected error occurred: {e}"
    
    def get_gemini_oauth(self, username):
        """
        Retrieve Gemini OAuth credentials for a user.
        
        Args:
            username: Username to retrieve credentials for
        
        Returns:
            dict: OAuth credentials or None if not found
        """
        if not self._ensure_connection():
            return None
        
        try:
            user = self.users_collection.find_one({"username": username})
            if user:
                return user.get("gemini_oauth")
            return None
        except Exception as e:
            _log_error(f"Error retrieving Gemini OAuth: {e}")
            return None
    
    def update_gemini_oauth_tokens(self, username, access_token, expiry, refresh_token=None):
        """
        Update Gemini OAuth access token after refresh.
        
        Args:
            username: Username to update
            access_token: New access token
            expiry: New expiry timestamp (ISO format string)
            refresh_token: New refresh token (if rotated)
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            update_data = {
                "gemini_oauth.access_token": access_token,
                "gemini_oauth.expiry": expiry
            }
            
            if refresh_token:
                update_data["gemini_oauth.refresh_token"] = refresh_token
            
            result = self.users_collection.update_one(
                {"username": username},
                {"$set": update_data}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                return True, None
            else:
                return False, "User not found."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error updating Gemini OAuth tokens: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error updating Gemini OAuth tokens: {e}")
            return False, f"An unexpected error occurred: {e}"

    def remove_gemini_oauth(self, username):
        """
        Remove Gemini OAuth credentials from a user.
        
        Args:
            username: Username to remove credentials from
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        if not self._ensure_connection():
            return False, "Database connection error."
        
        try:
            result = self.users_collection.update_one(
                {"username": username},
                {"$unset": {"gemini_oauth": ""}}
            )
            if result.modified_count > 0:
                return True, None
            elif result.matched_count > 0:
                return True, "No Gemini OAuth credentials were set."
            else:
                return False, "User not found."
        except pymongo_errors.PyMongoError as e:
            _log_error(f"MongoDB error removing Gemini OAuth: {e}")
            return False, f"Database error: {e}"
        except Exception as e:
            _log_error(f"Unexpected error removing Gemini OAuth: {e}")
            return False, f"An unexpected error occurred: {e}"

# Example usage (optional, for testing this file directly)
if __name__ == '__main__':
    # This part will only run when the script is executed directly
    # It requires Streamlit secrets to be available in a context where st.secrets can access them.
    # For direct script execution, you might need to mock st.secrets or load .env manually.
    
    # Mock st.secrets for direct script execution if not running via streamlit run
    class MockSecrets(dict):
        def __init__(self, *args, **kwargs):
            super(MockSecrets, self).__init__(*args, **kwargs)
            self.__dict__ = self

    if not hasattr(st, 'secrets'):
        st.secrets = MockSecrets(MONGODB_URI="mongodb+srv://vox:tZm0fZA2BQT5sDf9@learnifydb.h4kxpad.mongodb.net/learnify_auth?retryWrites=true&w=majority") # Replace with your actual URI for testing

    st.title("MongoAuthManager Test")

    manager = MongoAuthManager()

    if manager.client: # Check if connection was successful
        st.header("User Management")
        
        # Test Add User
        with st.form("add_user_form"):
            st.subheader("Add New User")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_email = st.text_input("Email")
            new_name = st.text_input("Name")
            submitted_add = st.form_submit_button("Add User")

            if submitted_add:
                if not all([new_username, new_password, new_email, new_name]):
                    _log_error("All fields are required.")
                else:
                    user_id, error = manager.add_user(new_username, new_password, new_email, new_name)
                    if error:
                        _log_error(f"Failed to add user: {error}")
                    else:
                        st.success(f"User added successfully with ID: {user_id}")

        # Test Find User
        st.subheader("Find User")
        find_username = st.text_input("Enter username to find")
        if st.button("Find User by Username"):
            if find_username:
                user = manager.find_user_by_username(find_username)
                if user:
                    st.json(user) # Display user data as JSON (excluding password for security)
                else:
                    st.warning("User not found.")
            else:
                st.warning("Please enter a username.")

        # Test Verify Password
        st.subheader("Verify Password")
        verify_username = st.text_input("Username for password verification")
        verify_password = st.text_input("Password to verify", type="password")
        if st.button("Verify Password"):
            if verify_username and verify_password:
                user = manager.find_user_by_username(verify_username)
                if user:
                    if manager.verify_password(verify_password, user.get("password")):
                        st.success("Password verified!")
                    else:
                        _log_error("Incorrect password.")
                else:
                    st.warning("User not found.")
            else:
                st.warning("Please enter both username and password.")
        
        # Test Update Password
        with st.form("update_password_form"):
            st.subheader("Update Password")
            update_pass_username = st.text_input("Username to update password for")
            update_new_pass = st.text_input("New Password", type="password")
            submitted_update_pass = st.form_submit_button("Update Password")

            if submitted_update_pass:
                if update_pass_username and update_new_pass:
                    success, error = manager.update_user_password(update_pass_username, update_new_pass)
                    if success:
                        st.success("Password updated successfully.")
                    else:
                        _log_error(f"Failed to update password: {error}")
                else:
                    _log_error("Username and new password are required.")
                    
        # Test Update User Details
        with st.form("update_details_form"):
            st.subheader("Update User Details")
            update_details_username = st.text_input("Username to update details for")
            update_name = st.text_input("New Name (optional)")
            update_email = st.text_input("New Email (optional)")
            submitted_update_details = st.form_submit_button("Update Details")

            if submitted_update_details:
                if update_details_username:
                    updates = {}
                    if update_name:
                        updates["name"] = update_name
                    if update_email:
                        updates["email"] = update_email
                    
                    if updates:
                        success, error = manager.update_user_details(update_details_username, updates)
                        if success:
                            st.success(f"User details updated. {error if error else ''}")
                        else:
                            _log_error(f"Failed to update details: {error}")
                    else:
                        st.info("No details provided to update.")
                else:
                    _log_error("Username is required to update details.")
        
        # Test Delete User Account
        with st.form("delete_account_form"):
            st.subheader("Delete User Account")
            delete_username = st.text_input("Username to delete")
            confirm_username = st.text_input("Confirm Username", placeholder="Type your username to confirm")
            submitted_delete = st.form_submit_button("Delete Account")

            if submitted_delete:
                if delete_username and confirm_username:
                    success, message = manager.delete_user_account(delete_username, confirm_username)
                    if success:
                        st.success(message)
                    else:
                        _log_error(message)
                else:
                    _log_error("Username and confirmation are required.")
    else:
        _log_error("Failed to initialize MongoAuthManager. Cannot run tests.")

