"""
Supabase Authentication Manager
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseAuth:
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def sign_in(self, email: str, password: str) -> dict:
        """
        Sign in with email and password
        Returns user data if successful, raises exception if failed
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                'success': True,
                'user': response.user,
                'session': response.session
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sign_up(self, email: str, password: str, metadata: dict = None) -> dict:
        """
        Sign up a new user
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            return {
                'success': True,
                'user': response.user,
                'session': response.session
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sign_out(self) -> dict:
        """Sign out current user"""
        try:
            self.supabase.auth.sign_out()
            return {'success': True}
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user(self) -> dict:
        """Get current user"""
        try:
            user = self.supabase.auth.get_user()
            return {
                'success': True,
                'user': user
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
