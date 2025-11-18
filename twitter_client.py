import os
import requests

class TwitterClient:
    """
    A client for interacting with the Twitter API v2.
    """
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.base_url = 'https://api.twitter.com/2'

    def is_configured(self):
        """Check if the bearer token is configured."""
        return bool(self.bearer_token)

    def get_user_profile(self, username="Presica_Pinto"):
        """
        Fetches profile information for a given Twitter username.
        
        Args:
            username (str): The Twitter handle to look up.

        Returns:
            dict: A dictionary containing the user's profile data and public metrics,
                  or None if the request fails or the client is not configured.
        """
        if not self.is_configured():
            print("❌ Twitter client is not configured. TWITTER_BEARER_TOKEN is missing.")
            return None

        # The endpoint to get a user by username
        url = f"{self.base_url}/users/by/username/{username}" 
        
        # Specify the fields you want to receive
        params = {
            "user.fields": "public_metrics,profile_image_url,description"
        }
        
        # Set up the authorization header
        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx) 
            
            data = response.json()
            if 'data' in data:
                return data['data']
            else:
                print(f"⚠️ Twitter API response did not contain user data: {data}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Twitter user profile for '{username}': {e}")
            if e.response is not None:
                print(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

if __name__ == '__main__':
    # Example usage:
    # Ensure you have a .env file with TWITTER_BEARER_TOKEN set
    from dotenv import load_dotenv
    load_dotenv()
    
    client = TwitterClient()
    if client.is_configured():
        print("Twitter client is configured.")
        profile = client.get_user_profile()
        if profile:
            print("\nSuccessfully fetched profile:")
            print(f"Name: {profile.get('name')}")
            print(f"Username: {profile.get('username')}")
            print(f"Description: {profile.get('description')}")
            
            metrics = profile.get('public_metrics', {})
            print("\nPublic Metrics:")
            print(f"  Followers: {metrics.get('followers_count')}")
            print(f"  Following: {metrics.get('following_count')}")
            print(f"  Tweets: {metrics.get('tweet_count')}")
    else:
        print("\nTwitter client is not configured. Please check your .env file.")
