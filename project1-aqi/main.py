import os
import requests
import readchar
import json

city = "Montreal"

current_channel = "news"

# get api key from apikey.env
with open("apikey.env") as f:
    api_key = f.read().strip()

# get words from words.json
with open("words.json") as f:
    words = json.load(f)
    first_names = words["first_names"]
    last_names = words["last_names"]
    adjectives = words["adjectives"]
    occupations = words["occupations"]

    
def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80
    

def get_AQI_data():
    # get aqi from waqi
    response = requests.get(f"https://api.waqi.info/feed/{city}/?token={api_key}")
    data = response.json()
    aqi = data['data']['aqi']
    return aqi

def get_channels_display():
    channels = {
        "news": "1 - News",
        "opinion": "2 - Opinion", 
        "sports": "3 - Sports",
        "weather": "4 - Weather"
    }
    
    display_parts = []
    for channel, label in channels.items():
        if channel == current_channel:
            display_parts.append(f"\033[93m{label}\033[0m")  # Yellow highlight
        else:
            display_parts.append(label)
    
    return "Available channels: " + ", ".join(display_parts)

def main_tv(): # will be looped constantly to fill terminal
    global current_channel
    global aqiData

    # clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    terminal_width = get_terminal_width()
    print("=" * terminal_width)
    print(get_channels_display())

    
    if current_channel == "news":
        news()
    elif current_channel == "opinion":
        opinion()
    elif current_channel == "sports":
        sports()
    elif current_channel == "weather":
        weather()

    input_char = readchar.readchar()
    if input_char == '1':
        current_channel = "news"
    elif input_char == '2':
        current_channel = "opinion"
    elif input_char == '3':
        current_channel = "sports"
    elif input_char == '4':
        current_channel = "weather"


def news():
    print("You are watching the news channel.")
    

def opinion():
    print("You are watching the opinion channel.")

def sports():
    print("You are watching the sports channel.")

def weather():
    print("You are watching the weather channel.")

global aqiData
aqiData = get_AQI_data()

while True:
    main_tv()
