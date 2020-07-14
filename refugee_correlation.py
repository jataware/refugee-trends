import os
from pytrends.request import TrendReq
from google.cloud import translate_v2
import pandas as pd
import configparser
from unhcr_refugee import get_refugee_data
from tabulate import tabulate

config = configparser.ConfigParser()
configFile = 'config.ini'
config.read(configFile)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['GOOGLE']['credentials']

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
    return (term, corr)

if __name__ == "__main__":
    print("Obtaining refugee data...")
    df_refugee = get_refugee_data()    
    
    print("\nThis application will translate a term of interest into a target language.\n"\
         "It will then check the correlation of the Google trend for that term (in the target language) against refugee arrivals in Ethiopia.")
    
    correlations = []
    running = True
    while running:
        country_check = False   
        trend_check = False   
        while country_check == False:
            while trend_check == False:
                print("\nPlease select (1 or 2) a country of interest:\n\t1. Somalia\n\t2. South Sudan")
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
                    print("\nPlease input a term of interest:")
                    term = input()

                translation_check = False
                print("\nWould you like to translate the term into the native language? Yes (y) or No (n)?")
                while translation_check == False:
                    translation = input()
                    if translation.lower() in ['y','yes','n','no']:
                        translation_check = True
                    else:
                        print("Please enter a valid response (y or n)")

                if translation.lower() == 'y' or translation.lower() == 'yes':
                    translated = translate(term, lang)
                    print(f"\n{term} translated into {lang} is {translated}.")
                    trend_term = translated
                else:
                    trend_term = term
                
                df_trend = get_trend(trend_term, geo)

                if df_trend.shape[0] == 0:
                    print("\nTerm has no associated trend. Please try another term.")
                else:
                    trend_check = True

        corr = get_corr(df_refugee, df_trend, trend_term)
        correlations.append([corr[0],geo, corr[1]])

        print("\nWould you like to try another term? Yes (y) or No (n)?")
        retry = input()
        if retry.lower() == 'n' or retry.lower() == 'no':
            running = False
    
    # print results            
    df_corr = pd.DataFrame(correlations, columns=['Term','Country','Correlation']).sort_values('Correlation', ascending=False)
    print(tabulate(df_corr, headers='keys', tablefmt='psql'))