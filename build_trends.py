from pytrends.request import TrendReq
import requests
import pandas as pd
from unhcr_refugee import get_refugee_data

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_trends(term):
    s=requests.get(base_url.format(term)).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')),skiprows=1)
    return c

def get_trends_dfs(terms, geo):
    trend_dfs = []
    pytrend = TrendReq(hl='en-US', tz=360, geo=geo)
    for term_list in chunks(terms,5):
        pytrend.build_payload(kw_list=term_list)
        trend_df = pytrend.interest_over_time()
        trend_dfs.append(trend_df)
    return trend_dfs

if __name__ == "__main__":
    print("Obtaining refugee data...")
    df_refugee = get_refugee_data()    

    print("\nThis application accepts a set of terms and a country of interest.\n"\
         "It will then build a spreadsheet of Google Trends and Ethiopian refugee data for further modeling.")
    
    country_check = False   
    while country_check == False:
        print("\nPlease select (1 or 2) a country of interest:\n\t1. Somalia\n\t2. South Sudan")
        try:
            country = int(input())
            if country == 1:
                geo = 'SO'
                country_check = True
                print("You have chosen Somalia.\n")
            elif country == 2:
                geo = 'SS'
                country_check = True
                print("You have chosen South Sudan.\n")
            else:
                print('Please select a valid country.')            
        except:
            print('Please select a valid country.')

    terms_check = False
    terms = []
    while terms_check == False:
        print("Please enter a term of interest (leave blank if done):")
        term = input()
        if term == '':
            terms_check = True
        else:
            terms.append(term)

    trend_dfs = get_trends_dfs(terms,geo)

    count = 0
    for d in trend_dfs:
        if d.shape != (0,0):
            if count == 0:
                d_ = d.drop(columns=['isPartial'])
            else:
                d_ = d_.join(d.drop(columns=['isPartial']), rsuffix='_dupe')
            count += 1    

    df_refugee = df_refugee.resample('1M').sum()
    gtrends_resample = d_.resample('1M').mean()
    mig_eth = df_refugee.join(gtrends_resample)

    print("Please enter a file name (.csv) for the output refugee/trends file:")
    filename = input()
    mig_eth.to_csv(filename)
    print(f"\nOutput saved as {filename}")