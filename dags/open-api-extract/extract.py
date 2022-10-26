import os
import requests
import json
import pandas as pd


cities = ["Tilburg"]
def get_weather_data_from_api(cities):
    api_key = "6092402787f9f4206afa86aa168f6df4"

    for city in cities:
        url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s" % (city, api_key)

        response = requests.get(url)
        data = json.loads(response.text)
        df = pd.json_normalize(data)

        pathfile = 'gcp_data_extraction_api/dags/open-api-extract/weatherData.csv'
        if not os.path.isfile(pathfile):
            df.to_csv(pathfile,header=False, index=False)
        else: # else it exists so append without writing the header
            df.to_csv(pathfile, mode='a', header=False, index=False)

get_weather_data_from_api(cities)


