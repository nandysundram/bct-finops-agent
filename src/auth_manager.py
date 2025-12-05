"""
Authentication Manager
Simple authentication system for BCT FinOps Tool
"""

import hashlib
import json
import os
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, users_file: str = 'users.json'):
        """Initialize authentication manager"""
        self.users_file = users_file
        self.load_users()
    
    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Default admin user
            self.users = {
                'admin': {
                    'password': self.hash_password('admin123'),
                    'role': 'admin',
                    'email': 'admin@bct.com',
                    'created': datetime.now().isoformat()
                }
            }
            self.save_users()
    
    def save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user"""
        if username in self.users:
            hashed_password = self.hash_password(password)
            return self.users[username]['password'] == hashed_password
        return False
    
    def add_user(self, username: str, password: str, email: str, role: str = 'user'):
        """Add new user"""
        if username in self.users:
            return False
        
        self.users[username] = {
            'password': self.hash_password(password),
            'role': role,
            'email': email,
            'created': datetime.now().isoformat()
        }
        self.save_users()
        return True
    
    def get_user_info(self, username: str):
        """Get user information"""
        if username in self.users:
            user_info = self.users[username].copy()
            user_info.pop('password')  # Don't return password
            return user_info
        return None
