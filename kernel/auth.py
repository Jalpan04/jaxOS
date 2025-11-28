import hashlib
import secrets
from fs.db import Database

class AuthManager:
    def __init__(self, db: Database):
        self.db = db
        self.current_user = None

    def hash_password(self, password: str) -> str:
        """Returns SHA-256 hash of the password."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> str | None:
        """Registers a new user. Returns recovery key on success, None on failure."""
        if self.db.get_user(username):
            return None # User exists
        
        pw_hash = self.hash_password(password)
        # Generate a dummy recovery key for now (Phase 4.3 will implement real recovery)
        recovery_key = secrets.token_hex(8) 
        recovery_hash = self.hash_password(recovery_key)
        
        if self.db.create_user(username, pw_hash, recovery_hash):
            return recovery_key
        return None

    def login(self, username: str, password: str) -> bool:
        """Attempts to log in. Returns True on success."""
        user = self.db.get_user(username)
        if not user:
            return False
            
        # user = (id, username, password_hash, recovery_key_hash)
        stored_hash = user[2]
        if self.hash_password(password) == stored_hash:
            self.current_user = username
            return True
        return False

    def logout(self):
        self.current_user = None

    def has_users(self) -> bool:
        """Checks if any users exist in the system."""
        return self.db.count_users() > 0

    def verify_recovery_key(self, username: str, recovery_key: str) -> bool:
        """Verifies the recovery key."""
        user = self.db.get_user(username)
        if not user:
            return False
            
        stored_hash = user[3] # recovery_key_hash
        # Normalize input: strip whitespace and convert to lowercase
        normalized_key = recovery_key.strip().lower()
        return self.hash_password(normalized_key) == stored_hash

    def reset_password(self, username: str, new_password: str) -> bool:
        """Resets the password for a user."""
        pw_hash = self.hash_password(new_password)
        return self.db.update_password(username, pw_hash)
