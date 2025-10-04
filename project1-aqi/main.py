import os
import sys
import time
import json
import select
import requests
import random

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

def get_terminal_height():
    try:
        return os.get_terminal_size().lines
    except OSError:
        return 24

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

    face_closed = [
        "  _____  ",
        " /     \\ ",
        "|  o o  |",
        "|  ___  |",
        "|       |",
        " \\_____/ "
    ]
    face_open = [
        "  _____  ",
        " /     \\ ",
        "|  o o  |",
        "|  ___  |",
        "|  \\_/  |",
        " \\_____/ "
    ]
    # alternate every 5 ticks
    if (ticker_offset // 5) % 2 == 0:
        face = face_open
    else:
        face = face_closed

    news.face_lines = [line.center(terminal_width) for line in face]

    # cycle through anchor lines in order
    anchor_templates = phrases[aqiCategory]["news"]["anchor_lines"]
    if not hasattr(news, "anchor_index"):
        news.anchor_index = 0
    if not hasattr(news, "anchor_tick"):
        news.anchor_tick = 0

    # only update anchor line every 30 ticks
    if ticker_offset % 30 == 0:
        # use last anchor line after reaching the end
        idx = min(news.anchor_index, len(anchor_templates) - 1)
        template = anchor_templates[idx]
        anchor_line = template.format(
            city=city,
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            adjective=random.choice(adjectives),
            occupation=random.choice(occupations),
            aqi=aqiData
        )
        news.anchor_line = anchor_line[:terminal_width]
        if news.anchor_index < len(anchor_templates) - 1:
            news.anchor_index += 1
        news.anchor_tick = ticker_offset
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
        # print() 

        anchor_printed = False
        if current_channel == "news":
            news()
            # center the face + anchor line
            terminal_height = get_terminal_height()
            face_height = len(news.face_lines)
            # lines used: 4 (header) + 2 (padding) + 1 (anchor) + face height
            lines_used = 4 + 2 + 1 + face_height
            vertical_space = max(terminal_height - lines_used, 0)
            top_padding = vertical_space // 2
            for _ in range(top_padding):
                print()
            for line in news.face_lines:
                print(line)
            print()
            print(news.anchor_line.center(terminal_width))
            anchor_printed = True
        elif current_channel == "opinion":
            opinion()
        elif current_channel == "sports":
            sports()
        elif current_channel == "weather":
            weather()

        # calculate how many blank lines to print to push ticker to bottom
        lines_used = 4
        if current_channel == "news":
            if anchor_printed:
                terminal_height = get_terminal_height()
                face_height = len(news.face_lines)
                anchor_lines = 1
                vertical_space = max(terminal_height - (4 + 2 + 1 + face_height), 0)
                top_padding = vertical_space // 2
                lines_used += top_padding + anchor_lines + face_height + 1
        elif current_channel == "opinion":
            lines_used += 0
        elif current_channel == "sports":
            lines_used += 0
        elif current_channel == "weather":
            lines_used += 0

        terminal_height = get_terminal_height()
        blank_lines = max(terminal_height - lines_used - 2, 0)
        for _ in range(blank_lines):
            print()

        if current_channel == "news":
            print(news.ticker_line)
            print(news.ticker_text)
            print(news.ticker_line)
            time.sleep(0.15) 
        else:
            print("=" * terminal_width)

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