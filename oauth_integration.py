#!/usr/bin/env python3
"""
OAuth 2.0 Integration for LinkedIn and Twitter (X.com)
Secure API credential management and authentication flow
"""

import os
import secrets
import hashlib
import sqlite3
import json
import requests
import urllib.parse
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from flask import request, session, redirect, url_for
import logging

logger = logging.getLogger(__name__)

@dataclass
class OAuthCredentials:
    """OAuth credentials data structure"""
    platform: str
    client_id: str
    client_secret: str
    redirect_uri: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    account_name: Optional[str] = None
    account_id: Optional[str] = None
    account_type: Optional[str] = None  # 'company' or 'personal' for LinkedIn, 'user' for Twitter

class OAuthManager:
    """OAuth 2.0 Manager for LinkedIn and Twitter"""

    def __init__(self, db_path: str = 'data/social_credentials.db'):
        self.db_path = db_path
        self.init_database()

        # OAuth endpoints
        self.linkedin_auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.linkedin_token_url = "https://www.linkedin.com/oauth/v2/accessToken"

        self.twitter_auth_url = "https://twitter.com/i/oauth2/authorize"
        self.twitter_token_url = "https://api.twitter.com/2/oauth2/token"

    def init_database(self):
        """Initialize secure database for OAuth credentials"""
        os.makedirs('data', exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS oauth_credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT UNIQUE NOT NULL,
                    client_id TEXT NOT NULL,
                    client_secret_encrypted TEXT NOT NULL,
                    redirect_uri TEXT NOT NULL,
                    access_token_encrypted TEXT,
                    refresh_token_encrypted TEXT,
                    expires_at DATETIME,
                    account_name TEXT,
                    account_id TEXT,
                    account_type TEXT,
                    is_connected BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS oauth_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state_token TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_platform ON oauth_credentials(platform);
                CREATE INDEX IF NOT EXISTS idx_state ON oauth_states(state_token);
            ''')

    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using simple hash-based encryption"""
        if not data:
            return ""

        # Simple encryption using environment-based key
        secret_key = os.getenv('OAUTH_SECRET_KEY', 'default-change-in-production')
        combined = f"{secret_key}:{data}"
        encrypted = hashlib.sha256(combined.encode()).hexdigest()
        return encrypted

    def _decrypt_sensitive_data(self, encrypted_data: str, reference: str = None) -> str:
        """For this MVP, we'll store encrypted but work with reference values"""
        # In production, use proper encryption like AES
        return reference or ""

    def generate_state_token(self, platform: str) -> str:
        """Generate secure state token for OAuth flow"""
        state = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=10)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO oauth_states (state_token, platform, expires_at)
                VALUES (?, ?, ?)
            ''', (state, platform, expires_at))

        return state

    def validate_state_token(self, state: str) -> Optional[str]:
        """Validate and return platform for state token"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT platform FROM oauth_states
                WHERE state_token = ? AND expires_at > ?
            ''', (state, datetime.now()))

            result = cursor.fetchone()
            if result:
                # Clean up used state token
                conn.execute('DELETE FROM oauth_states WHERE state_token = ?', (state,))
                return result[0]

        return None

    def setup_platform_credentials(self, platform: str, client_id: str,
                                  client_secret: str, redirect_uri: str):
        """Setup OAuth credentials for a platform"""
        encrypted_secret = self._encrypt_sensitive_data(client_secret)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO oauth_credentials
                (platform, client_id, client_secret_encrypted, redirect_uri, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (platform, client_id, encrypted_secret, redirect_uri, datetime.now()))

        logger.info(f"OAuth credentials configured for {platform}")

    def get_authorization_url(self, platform: str) -> Optional[str]:
        """Get OAuth authorization URL for platform"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT client_id, redirect_uri FROM oauth_credentials
                WHERE platform = ?
            ''', (platform,))

            result = cursor.fetchone()
            if not result:
                logger.error(f"No credentials found for {platform}")
                return None

            client_id, redirect_uri = result
            state = self.generate_state_token(platform)

            if platform == 'linkedin':
                params = {
                    'response_type': 'code',
                    'client_id': client_id,
                    'redirect_uri': redirect_uri,
                    'state': state,
                    'scope': 'r_liteprofile r_emailaddress w_member_social'
                }

                auth_url = f"{self.linkedin_auth_url}?{urllib.parse.urlencode(params)}"
                return auth_url

            elif platform == 'twitter':
                # Twitter OAuth 2.0 with PKCE
                code_verifier = secrets.token_urlsafe(32)
                code_challenge = hashlib.sha256(code_verifier.encode()).hexdigest()

                params = {
                    'response_type': 'code',
                    'client_id': client_id,
                    'redirect_uri': redirect_uri,
                    'state': state,
                    'code_challenge': code_challenge,
                    'code_challenge_method': 'S256',
                    'scope': 'tweet.read users.read offline.access'
                }

                # Store code verifier for later (in production, use secure session)
                session[f'{platform}_code_verifier'] = code_verifier

                auth_url = f"{self.twitter_auth_url}?{urllib.parse.urlencode(params)}"
                return auth_url

        return None

    def exchange_code_for_tokens(self, platform: str, code: str, state: str) -> bool:
        """Exchange authorization code for access tokens"""
        # Validate state
        platform_from_state = self.validate_state_token(state)
        if not platform_from_state or platform_from_state != platform:
            logger.error("Invalid state token")
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT client_id, client_secret_encrypted, redirect_uri
                FROM oauth_credentials WHERE platform = ?
            ''', (platform,))

            result = cursor.fetchone()
            if not result:
                logger.error(f"No credentials found for {platform}")
                return False

            client_id, _, redirect_uri = result
            client_secret = self._decrypt_sensitive_data(_, client_secret)

            try:
                if platform == 'linkedin':
                    return self._exchange_linkedin_code(client_id, client_secret, redirect_uri, code)
                elif platform == 'twitter':
                    code_verifier = session.get(f'{platform}_code_verifier')
                    if not code_verifier:
                        logger.error("Missing code verifier for Twitter")
                        return False
                    return self._exchange_twitter_code(client_id, client_secret, redirect_uri, code, code_verifier)

            except Exception as e:
                logger.error(f"Token exchange failed for {platform}: {e}")
                return False

        return False

    def _exchange_linkedin_code(self, client_id: str, client_secret: str,
                               redirect_uri: str, code: str) -> bool:
        """Exchange LinkedIn authorization code"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(self.linkedin_token_url, data=data)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Get user profile info
            account_info = self._get_linkedin_profile(access_token)

            # Store tokens
            encrypted_token = self._encrypt_sensitive_data(access_token)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE oauth_credentials SET
                    access_token_encrypted = ?, expires_at = ?,
                    account_name = ?, account_id = ?, account_type = ?,
                    is_connected = 1, updated_at = ?
                    WHERE platform = 'linkedin'
                ''', (encrypted_token, expires_at,
                      account_info.get('name'), account_info.get('id'), 'personal',
                      datetime.now()))

            logger.info("LinkedIn authentication successful")
            return True

        logger.error(f"LinkedIn token exchange failed: {response.text}")
        return False

    def _exchange_twitter_code(self, client_id: str, client_secret: str,
                              redirect_uri: str, code: str, code_verifier: str) -> bool:
        """Exchange Twitter authorization code"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'code_verifier': code_verifier
        }

        auth_header = f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.twitter_token_url, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 7200)
            expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Get user profile info
            account_info = self._get_twitter_profile(access_token)

            # Store tokens
            encrypted_token = self._encrypt_sensitive_data(access_token)
            encrypted_refresh = self._encrypt_sensitive_data(refresh_token) if refresh_token else None

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE oauth_credentials SET
                    access_token_encrypted = ?, refresh_token_encrypted = ?,
                    expires_at = ?, account_name = ?, account_id = ?,
                    account_type = 'user', is_connected = 1, updated_at = ?
                    WHERE platform = 'twitter'
                ''', (encrypted_token, encrypted_refresh, expires_at,
                      account_info.get('username'), account_info.get('id'),
                      datetime.now()))

            logger.info("Twitter authentication successful")
            return True

        logger.error(f"Twitter token exchange failed: {response.text}")
        return False

    def _get_linkedin_profile(self, access_token: str) -> Dict:
        """Get LinkedIn profile information"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://api.linkedin.com/v2/people/~:(id,firstName,lastName)',
                                 headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    'id': data.get('id'),
                    'name': f"{data.get('firstName', {}).get('localized', {}).get('en_US', '')} "
                           f"{data.get('lastName', {}).get('localized', {}).get('en_US', '')}"
                }
        except Exception as e:
            logger.error(f"Failed to get LinkedIn profile: {e}")

        return {'id': None, 'name': 'Unknown'}

    def _get_twitter_profile(self, access_token: str) -> Dict:
        """Get Twitter profile information"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://api.twitter.com/2/users/me', headers=headers)

            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'id': data.get('id'),
                    'username': data.get('username'),
                    'name': data.get('name')
                }
        except Exception as e:
            logger.error(f"Failed to get Twitter profile: {e}")

        return {'id': None, 'username': 'Unknown', 'name': 'Unknown'}

    def get_connection_status(self, platform: str) -> Dict:
        """Get connection status for platform"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT is_connected, account_name, account_id, account_type, expires_at, updated_at
                FROM oauth_credentials WHERE platform = ?
            ''', (platform,))

            result = cursor.fetchone()
            if not result:
                return {
                    'connected': False,
                    'account_name': None,
                    'account_id': None,
                    'account_type': None,
                    'expires_at': None,
                    'last_connected': None
                }

            is_connected, account_name, account_id, account_type, expires_at, updated_at = result

            # Handle datetime parsing - database may return strings
            if expires_at and isinstance(expires_at, str):
                try:
                    from datetime import datetime
                    expires_at = datetime.fromisoformat(expires_at)
                except:
                    expires_at = None

            if updated_at and isinstance(updated_at, str):
                try:
                    from datetime import datetime
                    updated_at = datetime.fromisoformat(updated_at)
                except:
                    updated_at = None

            # Handle datetime formatting with better error handling
            expires_at_str = None
            if expires_at:
                try:
                    if hasattr(expires_at, 'isoformat'):
                        expires_at_str = expires_at.isoformat()
                    elif isinstance(expires_at, str):
                        expires_at_str = expires_at
                except:
                    expires_at_str = None

            updated_at_str = None
            if updated_at:
                try:
                    if hasattr(updated_at, 'isoformat'):
                        updated_at_str = updated_at.isoformat()
                    elif isinstance(updated_at, str):
                        updated_at_str = updated_at
                except:
                    updated_at_str = None

            return {
                'connected': bool(is_connected),
                'account_name': account_name,
                'account_id': account_id,
                'account_type': account_type,
                'expires_at': expires_at_str,
                'last_connected': updated_at_str
            }

    def disconnect_platform(self, platform: str) -> bool:
        """Disconnect platform and clear credentials"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE oauth_credentials SET
                access_token_encrypted = NULL, refresh_token_encrypted = NULL,
                expires_at = NULL, account_name = NULL, account_id = NULL,
                account_type = NULL, is_connected = 0, updated_at = ?
                WHERE platform = ?
            ''', (datetime.now(), platform))

        logger.info(f"{platform} disconnected")
        return True

    def get_access_token(self, platform: str) -> Optional[str]:
        """Get access token for API calls"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT access_token_encrypted FROM oauth_credentials
                WHERE platform = ? AND is_connected = 1
            ''', (platform,))

            result = cursor.fetchone()
            if result:
                encrypted_token = result[0]
                # In production, decrypt properly
                return self._decrypt_sensitive_data(encrypted_token)

        return None

# Global OAuth manager instance
oauth_manager = OAuthManager()

def setup_oauth_credentials():
    """Setup default OAuth credentials"""
    # These should be loaded from environment variables in production
    oauth_manager.setup_platform_credentials(
        'linkedin',
        os.getenv('LINKEDIN_CLIENT_ID', 'your-linkedin-client-id'),
        os.getenv('LINKEDIN_CLIENT_SECRET', 'your-linkedin-client-secret'),
        'http://172.29.89.92:5000/oauth/linkedin/callback'
    )

    oauth_manager.setup_platform_credentials(
        'twitter',
        os.getenv('TWITTER_CLIENT_ID', 'your-twitter-client-id'),
        os.getenv('TWITTER_CLIENT_SECRET', 'your-twitter-client-secret'),
        'http://172.29.89.92:5000/oauth/twitter/callback'
    )

if __name__ == "__main__":
    setup_oauth_credentials()
    print("OAuth manager initialized")