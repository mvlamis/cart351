# STEP 4 - INITIAL REQUEST
import requests # import library to do api shenanigans 

token = "a9ad674728a09d9bdb8df9af11ae99bc0337cbbf" # set key
url = "https://api.waqi.info/search/" # base url 
response = requests.get(url, params={"token": token, "keyword": "montreal"}) # send request 
results = response.json() # jsonification

# STEP 5 - QUESTIONS
# print(results) # output jsonified data

# print(type(results)) # <class 'dict'>

# print(results.keys()) # dict_keys(['status', 'data'])

responseData = results['data']

# print(type(responseData)) # <class 'list'>

for item in responseData: # output each AQ from list
    # print(item) # each item is a different station in dict form

    # print(item.keys()) # dict_keys(['uid', 'aqi', 'time', 'station'])

    # print(item['station']['name'])
    # Maisonneuve, Montreal, Canada
    # Drummond, Montreal, Canada
    # St-Dominique, Montreal, Canada
    # Jardin Botanique, Montreal, Canada
    # Verdun, Montreal, Canada
    # Duncan, Montreal, Canada
    # Anjou, Montreal, Canada
    # Dorval, Montreal, Canada
    # Chénier, Montreal, Canada
    # Saint-Jean-Baptiste, Montreal, Canada
    # Aéroport de Montréal, Montreal, Canada
    # Sainte-Anne-de-Bellevue, Montreal, Canada

    # print(f"{item['station']['name']}, lat: {item['station']['geo'][0]}, long: {item['station']['geo'][1]}")
    # Maisonneuve, Montreal, Canada, lat: 45.501531, long: -73.574311
    # Drummond, Montreal, Canada, lat: 45.497859, long: -73.573035
    # St-Dominique, Montreal, Canada, lat: 45.512189, long: -73.566842
    # Jardin Botanique, Montreal, Canada, lat: 45.56221, long: -73.571785
    # Verdun, Montreal, Canada, lat: 45.472854, long: -73.57296
    # Duncan, Montreal, Canada, lat: 45.4660102, long: -73.6336838
    # Anjou, Montreal, Canada, lat: 45.602846, long: -73.558874
    # Dorval, Montreal, Canada, lat: 45.439119, long: -73.7333
    # Chénier, Montreal, Canada, lat: 45.60176, long: -73.541992
    # Saint-Jean-Baptiste, Montreal, Canada, lat: 45.641026, long: -73.499682
    # Aéroport de Montréal, Montreal, Canada, lat: 45.468297, long: -73.741185
    # Sainte-Anne-de-Bellevue, Montreal, Canada, lat: 45.426509, long: -73.928944

    print(f"Station Name: {item['station']['name']}, Latitude: {item['station']['geo'][0]}, Longitude: {item['station']['geo'][1]}, AQI: {item['aqi']}, UID: {item['uid']}")
    # Station Name: Maisonneuve, Montreal, Canada, Latitude: 45.501531, Longitude: -73.574311, AQI: 22, UID: 5465
    # Station Name: Drummond, Montreal, Canada, Latitude: 45.497859, Longitude: -73.573035, AQI: 21, UID: 8626
    # Station Name: St-Dominique, Montreal, Canada, Latitude: 45.512189, Longitude: -73.566842, AQI: 20, UID: 10138
    # Station Name: Jardin Botanique, Montreal, Canada, Latitude: 45.56221, Longitude: -73.571785, AQI: 17, UID: 8695
    # Station Name: Verdun, Montreal, Canada, Latitude: 45.472854, Longitude: -73.57296, AQI: 12, UID: 8594
    # Station Name: Duncan, Montreal, Canada, Latitude: 45.4660102, Longitude: -73.6336838, AQI: -, UID: 5462
    # Station Name: Anjou, Montreal, Canada, Latitude: 45.602846, Longitude: -73.558874, AQI: 27, UID: 8625
    # Station Name: Dorval, Montreal, Canada, Latitude: 45.439119, Longitude: -73.7333, AQI: -, UID: 8627
    # Station Name: Chénier, Montreal, Canada, Latitude: 45.60176, Longitude: -73.541992, AQI: 30, UID: 5460
    # Station Name: Saint-Jean-Baptiste, Montreal, Canada, Latitude: 45.641026, Longitude: -73.499682, AQI: 27, UID: 5459
    # Station Name: Aéroport de Montréal, Montreal, Canada, Latitude: 45.468297, Longitude: -73.741185, AQI: 24, UID: 5466
    # Station Name: Sainte-Anne-de-Bellevue, Montreal, Canada, Latitude: 45.426509, Longitude: -73.928944, AQI: 30, UID: 5468

# STEP 6 - FEED RESULTS

url_feed = "https://api.waqi.info/feed/@5468"
response_feed = requests.get(url_feed, params={"token": token})
results_feed = response_feed.json()
# print(results_feed)

response_data_feed = results_feed['data']
# print(type(response_data_feed)) # <class 'dict'>

for item in response_data_feed:
    print(item)
    # aqi
    # idx
    # attributions
    # city
    # dominentpol
    # iaqi
    # time
    # forecast
    # debug

aqi = response_data_feed['aqi'] # real time AQI
dominentpol = response_data_feed['dominentpol'] # pollutant

# print(aqi, dominentpol)

iaqi = response_data_feed['iaqi']
pollutant = iaqi[dominentpol]
print(pollutant) 
# {'v': 30}

# STEP 7 - DIFFERENT CITIES

# To find the dominant pollutant value of another city, find the city's code from its name with a search request. 
# Do another request for the specific city's data, containing its dominant pollutant and iaqi. 
# Find the value of the dominant pollutant by using it as a key within iaqi.