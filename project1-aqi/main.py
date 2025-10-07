import os
import sys
import time
import json
import select
import random
import textwrap
import datetime
import requests

city = "Montreal"
current_channel = "news"
ticker_offset = 0
AQI_override = None  # set to an AQI category string to override API data for testing

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

def get_forecast_data():
    response = requests.get(f"https://api.waqi.info/feed/{city}/?token={api_key}")
    data = response.json()
    forecast = data['data'].get('forecast', {}).get('daily', {})
    
    return forecast  

def get_aqi_category(aqi):
    if AQI_override in ["terrible", "bad", "okay", "good", "great"]:
        return AQI_override
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

def center_vertically(content_height):
    terminal_height = get_terminal_height()
    # account for the header (channel bar + separator line)
    available_height = terminal_height - 2
    padding = max(0, (available_height - content_height) // 2)
    
    for i in range(padding):
        print()
    
    return padding

def news():
    global ticker_offset
    terminal_width = get_terminal_width()
    terminal_height = get_terminal_height()

    face_height = 6  # face animation height
    spacing = 2      # empty line after face, first ticker line
    
    # estimate anchor text height (will vary based on text wrapping)
    if hasattr(news, "anchor_line"):
        anchor_height = len(textwrap.wrap(news.anchor_line, width=terminal_width))
    else:
        anchor_height = 1
    
    # The ticker will be at the bottom, so don't include it in centered content
    total_content_height = face_height + spacing + anchor_height
    
    # Print vertical padding - account for header (2 lines) and ticker (3 lines)
    available_height = terminal_height - 2 - 3  # Header and ticker lines
    padding_top = max(0, (available_height - total_content_height) // 2)
    
    for i in range(padding_top):
        print()
    
    # Face animation (alternate every 5 ticks)
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

    face_lines = [line.center(terminal_width) for line in face]

    # cycle through anchor lines in order
    anchor_templates = phrases[aqiCategory]["news"]["anchor_lines"]
    if not hasattr(news, "anchor_index"):
        news.anchor_index = 0
    if not hasattr(news, "anchor_tick"):
        news.anchor_tick = 0
    if ticker_offset % 30 == 0:
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
        news.anchor_line = anchor_line
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
    ticker_line = "=" * terminal_width
    ticker_display = visible[:terminal_width]

    # Print face and anchor message
    for line in face_lines:
        print(line)
    print()
    
    # Wrap anchor text to terminal width and center each line
    for wrapped_line in textwrap.wrap(news.anchor_line, width=terminal_width):
        print(wrapped_line.center(terminal_width))
    
    # calculate remaining space to fill before ticker at bottom
    content_used = padding_top + face_height + spacing + anchor_height
    remaining_lines = terminal_height - content_used - 2 - 2  # 2 for ticker, 2 for header
    
    # fill remaining space with empty lines
    for i in range(remaining_lines):
        print()
    
    print(ticker_line)
    print(ticker_display)
    # print(ticker_line)
    
    time.sleep(0.15)
    ticker_offset += 1

def opinion():
    terminal_width = get_terminal_width()
    
    intro_height = 2
    spacing = 1 # empty line after intro
    quote_height = 1
    speaker_height = 1
    
    total_height = intro_height + spacing + quote_height + speaker_height
    
    # Print vertical padding
    center_vertically(total_height)
    
    # cycle through opinion lines in order, stop at last
    opinion_lines = phrases[aqiCategory]["opinion"]["lines"]
    if not hasattr(opinion, "line_index"):
        opinion.line_index = 0
    if not hasattr(opinion, "line_tick"):
        opinion.line_tick = 0
    if not hasattr(opinion, "tick_counter"):
        opinion.tick_counter = 0
    opinion.tick_counter += 1
    if opinion.tick_counter % 100 == 1:
        idx = min(opinion.line_index, len(opinion_lines) - 1)
        template = opinion_lines[idx]
        # pick speaker for this line
        opinion.speaker_first = random.choice(first_names)
        opinion.speaker_last = random.choice(last_names)
        opinion.speaker_occupation = random.choice(occupations)
        opinion.current_line = template.format(
            city=city,
            adjective=random.choice(adjectives),
            aqi=aqiData
        )
        if opinion.line_index < len(opinion_lines) - 1:
            opinion.line_index += 1
        opinion.line_tick = opinion.tick_counter

    # intro
    print(f"We went out to the streets of {city} to get some opinions on the air quality.".center(terminal_width))
    print("Here's what they had to say:".center(terminal_width))
    print()

    # main content
    quote = f'“{opinion.current_line}”'
    speaker = f'- {opinion.speaker_first} {opinion.speaker_last}, {opinion.speaker_occupation}'
    print(quote.center(terminal_width))
    print(speaker.center(terminal_width))

def sports():
    terminal_width = get_terminal_width()

    # get animation frames for current AQI category
    frames_dict = phrases[aqiCategory].get("sports", {}).get("frames", {})
    
    # sort frame keys numerically
    frame_keys = sorted(frames_dict.keys(), key=int)
    if not hasattr(sports, "frame_index"):
        sports.frame_index = 0
    
    # get current frame to calculate height
    current_frame = frames_dict[frame_keys[sports.frame_index % len(frame_keys)]]
    caption = phrases[aqiCategory].get("sports", {}).get("caption", "")
    
    # calculate total content height
    frame_height = len(current_frame)
    caption_height = 1
    total_height = frame_height + caption_height
    
    center_vertically(total_height)
    
    for line in current_frame:
        print(line.center(terminal_width))
    
    print(caption.center(terminal_width))
    
    sports.frame_index = (sports.frame_index + 1) % len(frame_keys)
    time.sleep(0.15)

def weather():
    global ticker_offset
    global forecastData

    terminal_width = get_terminal_width()
    
    # get today's date for comparison
    today = datetime.datetime.now().date()

    forecast_types = ['pm25', 'pm10', 'o3']
    aqi_forecast = []
    
    # try each forecast type until one has data
    for forecast_type in forecast_types:
        if forecast_type in forecastData and forecastData[forecast_type]:
            aqi_forecast = forecastData[forecast_type]
            break
    
    # filter forecast to only include today and future days
    future_forecast = []
    for day in aqi_forecast:
        date = day.get('day', 'Unknown')
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        if date_obj >= today:
            future_forecast.append(day)
    
    forecast_days = 3

    title_height = 1
    title_spacing = 1
    lines_per_day = 3 # Date + bar + blank line
    forecast_height = forecast_days * lines_per_day
    quote_spacing = 1
    quote_height = 1
    
    total_height = title_height + title_spacing + forecast_height + quote_spacing + quote_height
    
    center_vertically(total_height)
    
    print(f"Air Quality Forecast for {city}".center(terminal_width))
    print()
    
    # graph forecast data
    for day in future_forecast[:forecast_days]:
        date = day.get('day', 'Unknown')
        min_aqi = day.get('min', 0)
        max_aqi = day.get('max', 0)
        avg_aqi = day.get('avg', 0)
        
        # format readable date
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%a, %b %d")
            
        # determine AQI category and color
        category = get_aqi_category(avg_aqi)
        if category == "terrible":
            color = "\033[91m"  # red
        elif category == "bad":
            color = "\033[93m"  # yellow
        elif category == "okay":
            color = "\033[95m"  # magenta
        elif category == "good":
            color = "\033[94m"  # blue
        else:  # great
            color = "\033[92m"  # green

        reset = "\033[0m"
        
        # bar representation
        bar_width = terminal_width - 20
        bar_length = int(min(avg_aqi / 300 * bar_width, bar_width))
        bar_char = "█" * bar_length
        padding = " " * (bar_width - bar_length)
        
        print(f"{formatted_date}: {color}AQI {avg_aqi} ({category}){reset}".center(terminal_width))
        print(f"[{color}{bar_char}{reset}{padding}] Min: {min_aqi}, Max: {max_aqi}".center(terminal_width))
        print()
    
    weather_lines = phrases.get(aqiCategory, {}).get("weather", {}).get("lines", [])

    if not hasattr(weather, "line_index"):
        weather.line_index = 0
    
    if not hasattr(weather, "line_adjectives"):
        weather.line_adjectives = {}
     
    if ticker_offset % 50 == 0:
        weather.line_index = (weather.line_index + 1) % len(weather_lines)
        # assign a new adjective only when changing to a new line
        if str(weather.line_index) not in weather.line_adjectives:
            weather.line_adjectives[str(weather.line_index)] = random.choice(adjectives)
    
    current_adjective = weather.line_adjectives.get(str(weather.line_index), random.choice(adjectives))
        
    weather_line = weather_lines[weather.line_index % len(weather_lines)]
    print(weather_line.format(
        city=city,
        adjective=current_adjective,
        aqi=aqiData
    ).center(terminal_width))
    
    time.sleep(0.15)
    ticker_offset += 1

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

        if current_channel == "news":
            news()
        elif current_channel == "opinion":
            opinion()
        elif current_channel == "sports":
            sports()
        elif current_channel == "weather":
            weather()

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
global forecastData
global aqiCategory

# fetch data
os.system('cls' if os.name == 'nt' else 'clear')
print("Loading air quality data for " + city + "...")
aqiData = get_AQI_data()

os.system('cls' if os.name == 'nt' else 'clear')
print("Loading forecast data...")
forecastData = get_forecast_data()

os.system('cls' if os.name == 'nt' else 'clear')
print("Data loaded. Turning on TV...")
time.sleep(2)

aqiCategory = get_aqi_category(aqiData)

if os.name != 'nt': # if not windows, set terminal to cbreak mode
    import tty
    tty.setcbreak(sys.stdin.fileno())

tv_loop()
