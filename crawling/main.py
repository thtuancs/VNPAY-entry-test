# https://www.visualcrossing.com/resources/documentation/weather-api/weather-api-documentation/#history

import datetime
import requests
from localtions import HCM_DISTRICTS
import copy
import pandas as pd
import argparse
from io import StringIO

MAX_LOCATION_COUNT = 5

history_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history"

base_params = {'aggregateHours': '1', 
    'unitGroup': 'metric', 
    'contentType': 'csv', 
    'dayStartTime': '0:0:00', 
    'dayEndTime': '0:0:00', 
    'outputDateTimeFormat': 'd/M/Y H:00',
    'timezone': 'Asia/Ho_Chi_Minh',
}

def get_weather_history(args):
    global history_url, base_params
    
    end_date = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - datetime.timedelta(days=2)
    
    params = copy.deepcopy(base_params)
    params['startDateTime'] = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    params['endDateTime'] = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    params['key'] = args.key
    
    is_saved_header = False
    for locations in [HCM_DISTRICTS[i:i + MAX_LOCATION_COUNT] for i in range(0, len(HCM_DISTRICTS), MAX_LOCATION_COUNT)]:
        params['location'] = '|'.join(locations)
        try:
            reponse = requests.get(history_url, params=params)
            if reponse.status_code != 200:
                raise Exception(f"Bad request: {reponse.status_code} \nError: {reponse.text}")
            
            df = pd.read_csv(StringIO(reponse.text))
            df.to_csv(args.filename, mode='a', header=not is_saved_header, index=False)
            is_saved_header = True
            
        except Exception as e:
            print(e)
            print("Failed to get weather history for locations: ", locations)
            
    return True
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', type=str, required=True, help='Visual Crossing api key, found in https://www.visualcrossing.com/account', )
    parser.add_argument('--filename', type=str, default='weather-history-data.csv')
    args = parser.parse_args()
    if not args.key:
        args.error('API key is required. Please provide the --key argument.')
    get_weather_history(args)
    
