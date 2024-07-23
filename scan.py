import requests
import json
import webbrowser
import time
import ccxt
from datetime import datetime
from pybit.unified_trading import HTTP

session = HTTP(
    testnet=False,
    api_key="",
    api_secret=""
)
# Load my data base that contains price levels
with open("data.json") as f:
    levels_data = json.load(f)

# List of undesired coins
undesired_tickers = [
"AVAILUSDT","ROSEUSDT","PIRATEUSDT","A8USDT", "UXLINKUSDT","PRCLUSDT","MOCAUSDT","DOP1USDT","CLOUDUSDT","BANANAUSDT", "AEROUSDT", "1000IQ50USDT", "1000000PEIPEIUSDT", "MANEKIUSDT", "BLASTUSDT", "AKTUSDT", "ZCXUSDT", "LISTAUSDT", "ZROUSDT", "1000APUUSDT", "ZKJUSDT", "ATHUSDT", "AIOZUSDT", "IOUSDT", "GMEUSDT", "1000000BABYDOGEUSDT", "ZKUSDT", "TAIKOUSDT", "PONKEUSDT", "ETHBTCUSDT", "RAYDIUMUSDT", "DOGUSDT", "BENDOGUSDT", "PHAUSDT", "1000BEERUSDT", "OSMOUSDT", "MONUSDT", "NYANUSDT", "PENGUSDT", "XCHUSDT", "SPECUSDT", "MAPOUSDT", "CANTOUSDT", "MASAUSDT", "DRIFTUSDT", "VELOUSDT", "NOTUSDT", "LFTUSDT", "FTNUSDT", "1000000MOGUSDT", "GNOUSDT", "BBUSDT", "COSUSDT", "FIREUSDT", "REZUSDT", "SAFEUSDT", "SCAUSDT", "LAIUSDT", "BRETTUSDT", "SUNUSDT", "1000000VINUUSDT", "IGUUSDT",
    "PAXGUSDT", "XCNUSDT", "USTCUSDT", "USDCUSDT", "BUSDUSDT", "ETHWUSDT", "TUSDT", "USDCUSDT"
]

# Get the current price for x ticker

def get_current_price(ticker):
    try:
        response = session.get_tickers(category="linear")
        if response['retCode'] != 0:
            print("Failed with Message:", response['retMsg'])
            return None     
        for ticker_data in response['result']['list']:
            if ticker == ticker_data['symbol']:
                return float(ticker_data['lastPrice'])    
        print("Ticker not found")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def getListOfTickersCloseToLevel():
    try:
        # Connect to Bybit and fetch tickers data
        response = session.get_tickers(category="linear")

        # Check for successful response
        if response['retCode'] != 0:
            print("Failed with Message:", response['retMsg'])
            return []

        result_list = []
        current_level_index = 0

        # Ensure all tickers correspond to the coins levels in the database
        for ticker in response['result']['list']:
            if ticker['symbol'] not in undesired_tickers and ticker['symbol'].endswith("USDT"):
                if ticker['symbol'] != levels_data[current_level_index]['ticker']:
                    print('ERROR AT', ticker['symbol'], 'vs', levels_data[current_level_index]['ticker'], current_level_index)
                    return []
                current_level_index += 1

        # Check each ticker against the levels data
        for ticker in response["result"]["list"]:
            if ticker['symbol'] not in undesired_tickers:
                for level in levels_data:
                    if ticker['symbol'] == level['ticker']:
                        current_price = float(ticker['lastPrice'])
                        for level_info in level['levels']:
                            price_of_interest = float(level_info[0])
                            percentage_threshold = float(level['close'])
                            lower_bound = price_of_interest * (1 - percentage_threshold)
                            upper_bound = price_of_interest * (1 + percentage_threshold)
                            if lower_bound <= current_price <= upper_bound:
                                result_list.append(ticker['symbol'])
                                break
        return result_list

    except Exception as e:
        # Handle any unexpected errors
        print(f"An error occurred: {e}")
        return []
    
def filterResultArray(movers):
    print("Movers", movers)
    for x in movers:
        for y in levels_data:
            if y["ticker"] == x and x not in already_visited_chart:
                myobj = datetime.now()
                print("COIN : ", x)
                print("TIME : ", myobj)
                print("CHART : ", y["web"])
                print("")
                webbrowser.open(y["web"], new=0)
                already_visited_chart.append(y["ticker"])


# Variables to know if a chart already has been visited inside the loop
counter = 0
added = []
deleted = []
already_visited_chart = []

# Infinite loop
while True:
    # Get a price snapshot of all the assets listed on bybit futures
    first_run = getListOfTickersCloseToLevel()
    time.sleep(60)
    second_run = getListOfTickersCloseToLevel()

    # Reset Already visited charts after x loops
    if counter == 25:
        added = []
        deleted = []
        already_visited_chart = []
        counter = 0

    # Check elements that enter interest zone
    for element in second_run:
        if element not in first_run:
            added.append(element)

    # Check elements that exit interest zone
    for element in first_run:
        if element not in second_run:
            deleted.append(element)

    # For each elements that ENTER or EXIT zone of interest, check if we don't already had it open the last x loops (counter), if not, open the chart in browser, and add element to already visited charts
    if len(added) > 0:
        filterResultArray(added)

    if len(deleted) > 0:
        filterResultArray(deleted)

    print("Already visited : ", already_visited_chart)
    # To know when to reset already visited chart to none (see : if counter == 3: ....)
    counter += 1
    print("GO")
