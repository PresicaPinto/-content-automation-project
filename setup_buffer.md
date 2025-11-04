# Buffer Setup Guide for Ardelis Technologies

## Step 1: Create Buffer Account
1. Go to https://buffer.com
2. Click "Sign Up" or "Log In"
3. Choose free plan (sufficient for now)

## Step 2: Connect LinkedIn
1. Once logged in, click "Connect an Account"
2. Select "LinkedIn"
3. Authorize Buffer to access your LinkedIn
4. Grant necessary permissions for posting

## Step 3: Get Access Token
1. Go to https://buffer.com/developers/api
2. Click "Create new App" or use existing
3. Copy your "Access Token"

## Step 4: Add to Configuration
Add your Buffer Access Token to:
```
config/.env.production
```

Add this line:
```
BUFFER_ACCESS_TOKEN="your_actual_buffer_token_here"
```

## Step 5: Test Connection
Run the test:
```bash
python test_linkedin_connection.py
```

## Benefits of Buffer:
- ✅ Easy LinkedIn posting
- ✅ Automatic scheduling
- ✅ Post analytics
- ✅ No need for LinkedIn API complexities
- ✅ Safe and reliable