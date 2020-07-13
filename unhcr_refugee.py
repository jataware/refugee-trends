import requests
import pandas as pd
import io

def get_refugee_data():
    data = requests.get('https://data2.unhcr.org/api/population/get/timeseries?widget_id=171273&geo_id=160&population_group=5121&frequency=day&fromDate=1900-01-01').json()
    df_refugee = pd.DataFrame(data['data']['timeseries'])
    df_refugee['date'] = df_refugee['data_date'].apply(lambda x: pd.to_datetime(x))
    df_refugee = df_refugee.sort_values('date')
    df_refugee['EthiopiaArrivals'] = df_refugee['individuals']
    df_refugee = df_refugee[['date','EthiopiaArrivals']].set_index('date')
    return df_refugee