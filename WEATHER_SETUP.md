# Weather API Setup Guide

## OpenWeatherMap API Setup

To enable the weather intelligence feature in your SmartGear voice assistant, you need to get an API key from OpenWeatherMap.

### Steps:

1. **Sign up for OpenWeatherMap**
   - Go to https://openweathermap.org/
   - Click "Sign Up" and create a free account
   - Verify your email address

2. **Get API Key**
   - After logging in, go to your account dashboard
   - Navigate to "API keys" tab
   - Copy your default API key or generate a new one

3. **Update the API Key in Your Code**
   - Open `core/views.py`
   - Find line 27: `WEATHER_API_KEY = "your_openweathermap_api_key"`
   - Replace `"your_openweathermap_api_key"` with your actual API key

### Example:
```python
WEATHER_API_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

## Features Enabled

Once the API key is set up, your voice assistant will be able to:

- **Real-time Weather Detection**: Automatically detects when users mention travel plans
- **Temperature-Based Recommendations**: Suggests appropriate clothing based on temperature
- **Weather Condition Matching**: Recommends waterproof items for rain, UV protection for sun, etc.
- **Location Intelligence**: Recognizes 25+ Indian destinations with precise coordinates
- **Smart Product Scoring**: Ranks products based on weather appropriateness

## Example Usage

Users can now say things like:
- "I'm going to Manali next week"
- "Planning a beach trip to Goa"
- "Going hiking in the mountains"
- "Visiting Delhi for a business meeting"

The assistant will:
1. Detect the destination
2. Fetch current weather data
3. Suggest perfect products based on conditions
4. Provide temperature and weather details

## Testing

To test the weather feature:
1. Set up your API key
2. Restart your Django server
3. Try queries like "I'm going to Goa" or "Planning a trip to Manali"
4. The assistant should respond with weather information and product recommendations

## Free Tier Limits

OpenWeatherMap free tier includes:
- 60 calls per minute
- 1,000,000 calls per month
- Current weather data
- 5-day weather forecast (if you want to extend later)

This should be more than sufficient for most SmartGear applications.
