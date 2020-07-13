import os
from pytrends.request import TrendReq
from google.cloud import translate_v2
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'world-modelers-268718-3c82e082c7de.json'

df_refugee = pd.read_csv('EthiopiaArrivals.csv')
df_refugee['date'] = pd.to_datetime(df_refugee['date'])
df_refugee = df_refugee.set_index('date')

def translate(text, lang):
    client = translate_v2.Client(target_language=lang)
    translated = client.translate(text)['translatedText']
    return translated
    
def get_trend(term, geo):
    pytrend = TrendReq(hl='en-US', tz=360, geo=geo)
    pytrend.build_payload(kw_list=[term])
    trend_df = pytrend.interest_over_time()
    return trend_df

def get_corr(df_refugee, df_trend, term):
    dfr_resample = df_refugee.resample('1M').sum()
    gtrends_resample = df_trend.resample('1M').mean()
    combined = dfr_resample.join(gtrends_resample)
    corr = combined.corr()[term]['EthiopiaArrivals']
    print(f"{term} has a {corr} correlation with Ethiopian refugees.")

if __name__ == "__main__":
    print("\nThis application will translate a term of interest into a target language.\n"\
         "It will then check the correlation of the Google trend for that term (in the target language) against refugee arrivals in Ethiopia.")
    
    running = True
    while running:
        country_check = False   
        trend_check = False   
        while country_check == False:
            while trend_check == False:
                print("Please select (1 or 2) a country of interest:\n\t1. Somalia\n\t2. South Sudan")
                try:
                    country = int(input())
                    if country == 1:
                        lang = 'so'
                        geo = 'SO'
                        country_check = True
                        print("You have chosen Somalia.")
                    elif country == 2:
                        lang = 'su'
                        geo = 'SS'
                        country_check = True
                        print("You have chosen South Sudan.")
                    else:
                        print('Please select a valid country.')            
                except:
                    print('Please select a valid country.')

                if country_check:
                    print("Please input a term of interest:")
                    term = input()

                    translated = translate(term, lang)
                    print(f"{term} translated into {lang} is {translated}.")

                    df_trend = get_trend(translated, geo)
                    if df_trend.shape[0] == 0:
                        print("Term has no associated trend. Please try another term.")
                    else:
                        trend_check = True

        corr = get_corr(df_refugee, df_trend, translated)

        print("Would you like to try another term? Yes (y) or No (n)?")
        retry = input()
        if retry.lower() == 'n' or retry.lower() == 'no':
            running = False