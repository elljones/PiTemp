#Code to read the raspberry temperature and get the temperature from external, save to REDIS and then display
#on the inky Phat

import redis   
from redis.commands.json.path import Path 
import os
import time
import json
import geocoder
import datetime
from sys import exit

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")


def connect_to_redis(host='pi', port=6379, password=None, db=0):
    """
    Connects to a Redis database and returns the connection object.

    Parameters:
    - host (str): Redis server hostname or IP address.
    - port (int): Redis server port (default is 6379).
    - password (str): Password for Redis authentication (default is None).
    - db (int): Redis database index (default is 0).

    Returns:
    - redis.Redis: Redis connection object.
    """
    try:
        # Create a connection to the Redis server
        connection = redis.Redis(host=host, port=port, password=password, db=db)

        # Test the connection by sending a PING command
        if connection.ping():
            print(f"Connected to Redis server at {host}:{port}")
            return connection
        else:
            print("Failed to connect to Redis server. Check your connection parameters.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage:
# Replace 'your_redis_password' with your actual Redis password if applicable.
# The default values assume a local Redis server running on the default port without authentication.
redis_connection = connect_to_redis(host='pi', port=6379, password='9999', db=0)

# Once connected, you can use the 'redis_connection' object to interact with the Redis database.
# For example, you can use commands like redis_connection.set(), redis_connection.get(), etc.

CITY = "Chester"
COUNTRYCODE = "GB"
WARNING_TEMP = 25.0


# Convert a city name and country code to latitude and longitude
def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords


# Query OpenMeteo (https://open-meteo.com) to get current weather data
def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=" + str(coords[0]) + "&longitude=" + str(coords[1]) + "&current_weather=true")
    if res.status_code == 200:
        j = json.loads(res.text)
        current = j["current_weather"]
        weather["temperature"] = current["temperature"]
        weather["windspeed"] = current["windspeed"]
        weather["weathercode"] = current["weathercode"]
        return weather
    else:
        return weather
    

location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)
timestamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
key=f"wx_ref:{timestamp}"
wx_record=str(weather["temperature"])+":"+str(weather["windspeed"])
redis_connection.set(key,wx_record)
