import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("WEATHER_API_KEY")


def get_city_code(city_name):
    request_url = os.getenv('AD_CODE_URL')
    parameters = {'key': api_key, 'address': city_name}
    response = requests.get(request_url, params=parameters)
    geocodes = response.json()['geocodes']
    return geocodes[0]['adcode']


def get_weather(city_name):
    request_url = os.getenv("WEATHER_URL")
    city_code = get_city_code(city_name)
    parameters = {'key': api_key, 'city': city_code}
    response = requests.get(request_url, params=parameters)
    live = response.json()['lives'][0]
    print(f'{city_name}当前的天气如下：'
          f'天气：{live['weather']}\n'
          f'温度：{live['temperature']}度\n'
          f'风向：{live['winddirection']}风\n'
          f'风速：{live['windpower']}级')


get_weather(input())
