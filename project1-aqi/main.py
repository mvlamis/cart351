import os
import sys
import time
import json
import select
import requests

city = "Montreal"
current_channel = "news"
ticker_offset = 0

# load API key and word lists
with open("apikey.env") as f:
    api_key = f.read().strip()

with open("words.json") as f:
    words = json.load(f)
    first_names = words["first_names"]
    last_names = words["last_names"]
    adjectives = words["adjectives"]
    occupations = words["occupations"]

with open("phrases.json") as f:
    phrases = json.load(f)

def get_AQI_data():
    response = requests.get(f"https://api.waqi.info/feed/{city}/?token={api_key}")
    data = response.json()
    aqi = data['data']['aqi']
    return aqi

def get_aqi_category(aqi):
    if aqi >= 250:
        return "terrible"
    elif aqi >= 150:
        return "bad"
    elif aqi >= 100:
        return "okay"
    elif aqi >= 50:
        return "good"
    else:
        return "great"

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def get_channels_display():
    channels = {
        "news": "1 - News",
        "opinion": "2 - Opinion", 
        "sports": "3 - Sports",
        "weather": "4 - Weather",
        "Q": "Q - Quit"
    }
    display_parts = []
    for channel, label in channels.items():
        if channel == current_channel:
            display_parts.append(f"\033[93m{label}\033[0m")  # Yellow highlight
        else:
            display_parts.append(label)
    return " | ".join(display_parts)

def news():
    global ticker_offset
    terminal_width = get_terminal_width()
    # news ticker logic
    tickers = phrases[aqiCategory]["news"]["tickers"]
    ticker_text = "     ".join(tickers) + "     "
    ticker_text *= 2
    start = ticker_offset % len(ticker_text)
    end = start + terminal_width
    if end <= len(ticker_text):
        visible = ticker_text[start:end]
    else:
        visible = ticker_text[start:] + ticker_text[:end - len(ticker_text)]
    # store for later printing at bottom
    news.ticker_line = "=" * terminal_width
    news.ticker_text = visible[:terminal_width]
    ticker_offset += 1

def opinion():
    print("You are watching the opinion channel.")

def sports():
    print("You are watching the sports channel.")

def weather():
    print("You are watching the weather channel.")

# non blocking input for constant screen refresh with input
def nonblocking_input():
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)

# main loop
def tv_loop():
    global current_channel
    terminal_width = get_terminal_width()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(get_channels_display().center(terminal_width))
        print("=" * terminal_width)
        print() 

        if current_channel == "news":
            news()
        elif current_channel == "opinion":
            opinion()
        elif current_channel == "sports":
            sports()
        elif current_channel == "weather":
            weather()

        # calculate how many blank lines to print to push ticker to bottom
        lines_used = 4
        if current_channel == "news":
            lines_used += 0 
        elif current_channel == "opinion":
            lines_used += 1
        elif current_channel == "sports":
            lines_used += 1
        elif current_channel == "weather":
            lines_used += 1

        try:
            terminal_height = os.get_terminal_size().lines
        except OSError:
            terminal_height = 24  # default

        blank_lines = max(terminal_height - lines_used - 2, 0)
        for _ in range(blank_lines):
            print()

        # Draw ticker at the bottom if on news channel
        if current_channel == "news":
            print(news.ticker_line)
            print(news.ticker_text)
            time.sleep(0.04)
        else:
            print("=" * terminal_width)
            print("".ljust(terminal_width))

        input_char = nonblocking_input()
        if input_char == '1':
            current_channel = "news"
        elif input_char == '2':
            current_channel = "opinion"
        elif input_char == '3':
            current_channel = "sports"
        elif input_char == '4':
            current_channel = "weather"
        elif input_char is not None and input_char.lower() == 'q':
            break
        time.sleep(0.04)

global aqiData
global aqiCategory
aqiData = get_AQI_data()
aqiCategory = get_aqi_category(aqiData)

if os.name != 'nt': # if not windows, set terminal to cbreak mode
    import tty
    tty.setcbreak(sys.stdin.fileno())

tv_loop()