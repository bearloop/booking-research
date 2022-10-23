from bs4 import BeautifulSoup
import requests as req
import pandas as pd
import math
import json

# ------------------------------------------------------------------------------------------------------------
REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
                  Chrome/50.0.2661.75 Safari/537.36",
                  "Content-Type":"application/json"}

# ------------------------------------------------------------------------------------------------------------
def fetch(date_in,date_out,people='4',city='Gennadi',offset='0'):
        
        date_in = date_in.split('-')
        date_out = date_out.split('-')

        url = "https://www.booking.com/searchresults.gr.html?checkin_month={in_month}" \
                "&checkin_monthday={in_day}&checkin_year={in_year}&checkout_month={out_month}" \
                "&checkout_monthday={out_day}&checkout_year={out_year}&group_adults={people}" \
                "&group_children=0&order=price&ss={city}%2C%20{country}&offset={offset}"\
                .format(in_month=date_in[1],
                        in_day=date_in[2],
                        in_year=date_in[0],
                        out_month=date_out[1],
                        out_day=date_out[2],
                        out_year=date_out[0],
                        people=people,
                        city=city,
                        country='Greece',
                        offset=str(offset))

        result = req.get(url,headers=REQUEST_HEADER)

        soup = BeautifulSoup(result.text, "html")

        return soup

# ------------------------------------------------------------------------------------------------------------
def create_property(prop, rev):
    dct = dict()

    try:
        dct['propId']             = prop['basicPropertyData']['__ref']
    except:
        dct['propId'] = '-'

    try:
        dct['displayPrice']       = prop['priceDisplayInfo']['displayPrice']['amountPerStay']['amountUnformatted']
    except:
        dct['displayPrice'] = '-'

    try:
        dct['displayName']        = prop['displayName']['text']
    except:
        dct['displayName'] = '-'

    try:
        dct['displayLocation']    = prop['location']['displayLocation']
    except:
        dct['displayLocation'] = '-'

    try:
        dct['mainDistance']       = prop['location']['mainDistance']
    except:
        dct['mainDistance'] = '-'

    try:
        dct['beachDistance']      = prop['location']['beachDistance']
    except:
        dct['beachDistance'] = '-'

    try:
        dct['nearbyBeachNames']   = prop['location']['nearbyBeachNames']
    except:
        dct['nearbyBeachNames'] = '-'

    try:
        dct['geoDistanceMeters']  = prop['location']['geoDistanceMeters']
    except:
        dct['geoDistanceMeters'] = '-'

    try:
        dct['isNewlyOpened']      = prop['isNewlyOpened']
    except:
        dct['isNewlyOpened'] = '-'

    try:
        dct['isSustainable']      = prop['sustainability']['isSustainable']
    except:
        dct['isSustainable'] = '-'

    try:
        dct['finalPrice']         = prop['blocks'][0]['finalPrice']['amount']
    except:
        dct['finalPrice'] = '-'

    try:
        dct['originalPrice']      = prop['blocks'][0]['originalPrice']['amount']
    except:
        dct['originalPrice'] = '-'

    try:
        dct['nbAllBeds']          = prop['matchingUnitConfigurations']['commonConfiguration']['nbAllBeds']
    except:
        dct['nbAllBeds'] = '-'

    try:
        dct['nbBathrooms']        = prop['matchingUnitConfigurations']['commonConfiguration']['nbBathrooms']
    except:
        dct['nbBathrooms'] = '-'

    try:
        dct['nbBedrooms']         = prop['matchingUnitConfigurations']['commonConfiguration']['nbBedrooms']
    except:
        dct['nbBedrooms'] = '-'

    try:
        dct['nbKitchens']         = prop['matchingUnitConfigurations']['commonConfiguration']['nbKitchens']
    except:
        dct['nbKitchens'] = '-'

    try:
        dct['nbLivingrooms']      = prop['matchingUnitConfigurations']['commonConfiguration']['nbLivingrooms']
    except:
        dct['nbLivingrooms'] = '-'

    try:
        dct['nbMaxAdults']        = prop['matchingUnitConfigurations']['commonConfiguration']['nbMaxAdults']
    except:
        dct['nbMaxAdults'] = '-'

    try:
        dct['nbUnits']            = prop['matchingUnitConfigurations']['commonConfiguration']['nbUnits']
    except:
        dct['nbUnits'] = '-'

    try:
        dct['propDescription']    = prop['matchingUnitConfigurations']['commonConfiguration']['unitTypeNames'][0]['translation']
    except:
        dct['propDescription'] = '-'

    try:
        dct['propSize']           = prop['matchingUnitConfigurations']['commonConfiguration']['localizedArea']['localizedArea']
    except:
        dct['propSize'] = '-'

    try:
        dct['propSizeUnit']       = prop['matchingUnitConfigurations']['commonConfiguration']['localizedArea']['unit']
    except:
        dct['propSizeUnit'] = '-'
    
    try:
        reviews = rev[dct['propId']]['reviews']
        dct['totalScore'] = reviews['totalScore']
        dct['reviewsCount'] = reviews['reviewsCount']
    except:
        dct['totalScore'] = '-'
        dct['reviewsCount'] = '-'

    return dct

# ------------------------------------------------------------------------------------------------------------
def find_offset(sp):
    
    res = eval(sp.find_all("h1",class_="e1f827110f d3a14d00da"
                    )[0].getText().split(':')[1].split('properties found')[0])

    return 25*(math.ceil(res/25)-1)+1

# ------------------------------------------------------------------------------------------------------------
def clean_up(dataset):

    overall = dict()

    for time_range in dataset:

        overall[time_range] = {}
        pages = dataset[time_range]

        for page in pages:
            
            base = json.loads(pages[page].find_all("script",type="application/json")[2].string)
            places = base['ROOT_QUERY']['searchQueries'][list(base['ROOT_QUERY']['searchQueries'].keys())[1]]['results']

            for place in places:

                dd = create_property(place, base)
                overall[time_range][dd['propId']] = dd
    
    ov_index = {(key, innerKey): innerVal for key, val in overall.items() for innerKey, innerVal in val.items()}
    ov_df = pd.DataFrame(ov_index).T
    print('Created dataframe')
    return ov_df