from utils import fetch, find_offset, clean_up
from datetime import datetime
import pandas as pd

current_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
file_name = './assets/{0}.csv'.format(current_date)

date_range = list(pd.date_range( start = datetime.strptime('29-01-2023',"%d-%m-%Y"),
                         end = datetime.strptime('3-12-2023',"%d-%m-%Y"),freq='W').astype(str))

dataset = dict()

for i in range(1,len(date_range)):
        
    start, end = date_range[i-1], date_range[i]

    soup = fetch(start,end)
    max_offset = find_offset(soup)

    soup_dct = dict()
    soup_dct[0] = soup

    for i in range(0,max_offset,25):

        if i != 0 :
            soup_dct[i] = fetch(start,end,offset=str(i))

    dataset[start+':'+end] = soup_dct
    print('Done: ', start,':',end)
    

df = clean_up(dataset)

df.to_csv(file_name)
print('Exported data to csv')