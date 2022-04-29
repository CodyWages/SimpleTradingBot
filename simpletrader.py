import time
import requests
import urllib.parse
import hashlib
import hmac
import base64

api_url = 'https://api.kraken.com'
api_key = 'YOUR API KEY'
api_sec = 'YOUR API PRIVATE KEY'

# Kraken API Signature 
def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Kraken API Request
def kraken_request(url_path, data, api_key, api_sec):
    headers = {"API-Key": api_key, "API-Sign": get_kraken_signature(url_path, data, api_sec)}
    response = requests.post((api_url + url_path), headers=headers, data=data)
    return response

# Trade Parameters
buy_limit = 30000
sell_limit = 45000
buy_amount = 0.01
sell_amount = 0.01
frequency = 10 # in seconds
asset = 'XBTUSD'

# Trade Algo
while True:

    # Price Request
    current_price = requests.get('https://api.kraken.com/0/public/Ticker?pair=BTCUSD').json()['result']['XXBTZUSD']['c'][0]

    # Buy Order
    if float(current_price) < buy_limit:
        print(f'Buying {buy_amount} of BTC at {current_price}.')
        response = kraken_request('/0/private/AddOrder', {
            'nonce': str(int(1000 * time.time())),
            'ordertype': 'market',
            'type': 'buy',
            'volume': buy_amount,
            'pair': asset,
        }, api_key, api_sec)

        if not response.json()['error']:
            print('Buy Successful!')
        else:
            print(f'Error: {response.json()["error"]}')

    # Sell Order
    elif float(current_price) > sell_limit:
        print(f'Selling {sell_amount} of BTC at {current_price}.')
        response = kraken_request('/0/private/AddOrder', {
            'nonce': str(int(1000 * time.time())),
            'ordertype': 'market',
            'type': 'sell',
            'volume': sell_amount,
            'pair': asset,
        }, api_key, api_sec)

        if not response.json()['error']:
            print('Sell Successful!')
        else:
            print(f'Error: {response.json()["error"]}')

    # Waiting For Action        
    else:
        print(f'\nCurrent {asset} Price: ${current_price}\npatiently waiting...')
        
    time.sleep(frequency)
