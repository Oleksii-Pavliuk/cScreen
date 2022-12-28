##
##    Makes API request 
##
##
import requests
from key import key


def info1(sym):
    #url for API
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
    #Request configuration
    parameters = {
    'amount' : '1',
    'symbol' : sym,
    'convert' : 'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': key,
    }
    #Request
    token = requests.get(url, params=parameters, headers=headers).json()
    if token['status']['error_code'] == 0:
        print(token)
        return token
    else:
        print(token)
        return 1
    
def info(sym):
    #url for API
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    #Requset configuration 
    parameters = {
        'symbol' : sym,
        'convert': 'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': key ,
    }
    token = requests.get(url, params=parameters, headers=headers).json()
    if token['status']['error_code'] == 0:
        print(token)
        return token
    else:
        print(token)
        return 1
