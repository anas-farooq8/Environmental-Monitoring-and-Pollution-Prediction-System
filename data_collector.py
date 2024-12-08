import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')

# Example API call for current air pollution data
air_pollution_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}'
response = requests.get(air_pollution_url)
if response.status_code == 200:
    data = response.json()
    print("Air Quality Data:", data)
else:
    print("Error fetching air quality data:", response.status_code)
