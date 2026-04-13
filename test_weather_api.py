#!/usr/bin/env python
"""
Test script to verify Weather API is working
"""
import os
import sys
import requests
import json

# Weather API configuration
WEATHER_API_KEY = "e0f58f02ae07966898ecf53c37dca217"
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def test_weather_api(location="Kashmir"):
    """Test weather API for a given location"""
    print(f"🌤️ Testing Weather API for: {location}")
    print("=" * 50)
    
    try:
        # Test coordinates for Kashmir
        location_coords = {
            'kashmir': {'lat': 34.0837, 'lon': 74.7973},
            'manali': {'lat': 32.2396, 'lon': 77.1888},
            'goa': {'lat': 15.2993, 'lon': 74.1240},
            'delhi': {'lat': 28.6139, 'lon': 77.2090}
        }
        
        if location.lower() in location_coords:
            coords = location_coords[location.lower()]
            url = f"{WEATHER_BASE_URL}?lat={coords['lat']}&lon={coords['lon']}&appid={WEATHER_API_KEY}&units=metric"
        else:
            url = f"{WEATHER_BASE_URL}?q={location}&appid={WEATHER_API_KEY}&units=metric"
        
        print(f"🔗 API URL: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print("✅ API Response Status: SUCCESS")
        print(f"📍 Location: {data.get('name', 'Unknown')}")
        print(f"🌡️ Temperature: {data['main']['temp']:.1f}°C")
        print(f"💧 Humidity: {data['main']['humidity']}%")
        print(f"☁️ Weather: {data['weather'][0]['description']}")
        print(f"💨 Wind Speed: {data['wind']['speed']} m/s")
        print(f"🌅 Sunrise: {data['sys']['sunrise']}")
        print(f"🌇 Sunset: {data['sys']['sunset']}")
        
        return {
            'success': True,
            'location': data.get('name', location),
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return {'success': False, 'error': str(e)}
    except KeyError as e:
        print(f"❌ Data Parsing Error: {e}")
        return {'success': False, 'error': f"Missing key: {e}"}
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return {'success': False, 'error': str(e)}

def test_multiple_locations():
    """Test weather API for multiple locations"""
    locations = ['Kashmir', 'Manali', 'Goa', 'Delhi', 'London', 'New York']
    
    print("🌍 Testing Weather API for Multiple Locations")
    print("=" * 60)
    
    results = {}
    for location in locations:
        result = test_weather_api(location)
        results[location] = result
        print("\n" + "-" * 40 + "\n")
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 30)
    success_count = sum(1 for r in results.values() if r['success'])
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All weather API tests PASSED!")
    else:
        print("⚠️ Some weather API tests FAILED!")
    
    return results

if __name__ == "__main__":
    print("🚀 Weather API Test Script")
    print("=" * 40)
    
    # Test single location
    print("\n1️⃣ Testing Single Location (Kashmir):")
    test_weather_api("Kashmir")
    
    print("\n\n2️⃣ Testing Multiple Locations:")
    test_multiple_locations()
    
    print("\n✨ Test Complete!")
