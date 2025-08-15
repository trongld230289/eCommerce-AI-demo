# OpenAI Quota Error Resolution Guide

## 🚨 Problem: "insufficient_quota" Error

You're getting this error because your OpenAI API key has exceeded its usage quota or doesn't have sufficient credits.

## 🔧 Solutions

### Option 1: Add Credits to Your OpenAI Account
1. Go to [OpenAI Platform Billing](https://platform.openai.com/account/billing)
2. Add credits to your account
3. Restart the Whisper API service

### Option 2: Check Current Usage
1. Visit [OpenAI Usage Dashboard](https://platform.openai.com/account/usage)
2. Check your current month's usage
3. See if you've hit your monthly limit

### Option 3: Use a Different API Key
1. Create a new OpenAI account (if needed)
2. Generate a new API key
3. Update the `.env` file in the `BE` folder:
   ```
   OPENAI_API_KEY=your_new_api_key_here
   ```
4. Restart the Whisper API service

### Option 4: Test with Mock Data (Development)
The system now includes a fallback for quota errors:
- When quota is exceeded, it returns mock Vietnamese text
- This allows you to test the translation functionality
- Look for "[Mock Transcription]" in the response

## 🧪 Test Your Quota Status

You can check your API quota status by visiting:
```
http://localhost:5005/check-quota
```

This will tell you if your OpenAI API is working or if quota is exceeded.

## 💰 OpenAI Pricing Reference

### Whisper API Pricing:
- $0.006 per minute of audio

### GPT-3.5-turbo Pricing (for translation):
- $0.0015 per 1K input tokens
- $0.002 per 1K output tokens

## 🔄 How to Restart After Fixing Quota

1. Fix your OpenAI quota (add credits or new API key)
2. Stop the Whisper API service (Ctrl+C in terminal)
3. Start it again:
   ```bash
   cd BE
   python whisper_api.py
   ```
4. Test voice chat again

## 📞 Need Help?

If you continue having issues:
1. Check [OpenAI Status Page](https://status.openai.com/)
2. Contact OpenAI Support through their platform
3. Make sure your API key has the correct permissions

The voice chat will work perfectly once the quota issue is resolved! 🎤✨
