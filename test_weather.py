import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('WEATHER_API_KEY')
print(api_key)
payload = {'key': api_key, 'city': '110100'}
result = requests.get("https://restapi.amap.com/v3/weather/weatherInfo", params=payload)
print(result.json())