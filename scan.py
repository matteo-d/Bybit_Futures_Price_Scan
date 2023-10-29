import requests
import json
import webbrowser
import time
import ccxt
from datetime import datetime

# Load my data base that contains price levels
with open("data.json") as f:
        levels_data = json.load(f)

# Bybit
bybit = ccxt.bybit()
base_url = "https://api.bybit.com/v2"
headers = {"Content-Type": "application/json", "api-key": ""}

# List of undesired coins
undesired_tickers = ["WSMUSDT","WAXPUSDT","TOMIUSDT","STRAXUSDT","STEEMUSDT","RIFUSDT","POWRUSDT","POLYXUSDT","ORBSUSDT","NTRNUSDT","GASUSDT","GASUSDT","BONDUSDT","BIGTIMEUSDT","10000STARLUSDT","STPTUSDT","VRAUSDT","MNTUSDT","ETHUSDH24","BTCUSDH24","LOOMUSDT","MULTIUSDT","FRONTUSDT","HNTUSDT","XVSUSDT","PERPUSDT","PROMUSDT","NMRUSDT","TONUSDT","OGUSDT","HIFIUSDT","YFIIUSDT","BADGERUSDT","SEIUSDT","CYBERUSDT","RDNTUSDT","QNTUSDT","BTCUSDZ23","COMBOUSDT","UMAUSDT","KEYUSDT","RADUSDT","LEVERUSDT","AMBUSDT","10000LADYSUSDT","TUSDT","TRUUSDT","DOTUSD","GFTUSDT","NKNUSDT", "AGIXUSDT","USDCUSDT","COREUSDT","EOSUSD","FETUSDT", "ATOMUSD","ADAUSD","BITUSD","BTCUSD","BTCUSDH23","BTCUSDM23","BTCUSDZ22","C98USD","ETHUSD","ETHUSDH23","ETHUSDM23","ETHUSDZ23","ETHWUSDT","LTCUSD","MANAUSD","USDCUSDT","BUSDUSDT","XRPUSD","SSVUSDT","RPLUSDT","LQTYUSDT","GPTUSDT", "FLRUSDT","ETHUSDU23","HFTUSDT","BTCUSDU23","IDUSDT","RLCUSDT","ORDIUSDT","KEYUSDT"]
webbrowser.open("https://www.youtube.com/watch?v=kse87ocS0Uo", new=0)
# Get the current price for x ticker
def get_current_price(ticker):
    # Connect to bybit
    response = requests.get(base_url + "/public/tickers", headers=headers)
    if response.status_code != 200:
            print("failed with status code :", response.status_code)
    else:
        data = response.json()
        for response_data in data['result']:
            if ticker == response_data['symbol']:
                current_price = float(response_data['last_price'])
                return current_price

def getListOfTickersCloseToLevel() :
    # Connect to bybit
    response = requests.get(base_url + "/public/tickers", headers=headers)
    if response.status_code != 200:
        print("failed with status code :", response.status_code)
    else:
        data = response.json()
        result_array = []
        # Check if the coin tracked correspond to the coins levels in the database 
        c = 0
        for ticker in data['result']:
            if ticker['symbol'] not in undesired_tickers:
                if ticker['symbol'] != levels_data[c]['ticker']:
                    print('ERROR AT' , ticker['symbol'] , 'vs', levels_data[c]['ticker'], c )
                    exit()
                    return
                c += 1
      
        for ticker in data["result"] :
            if ticker['symbol'] not in undesired_tickers :
                for x in levels_data:
                    if ticker['symbol'] == x['ticker']:
                        for inner_list in x['levels']:
                            price_of_interest = float(inner_list[0])
                            grade = int(inner_list[1])
                            current_price = float(ticker['last_price'])
                            percentage = float(x['close'])
                            # grade == 0 means mid range, the zone of interest of a mid range is 2 times smaller than the normal price_of_interest
                            if grade == 0 and price_of_interest - price_of_interest * (percentage/2) <= current_price <= price_of_interest + price_of_interest * (percentage/2) :
                                result_array.append(ticker['symbol'])
                            if grade != 0 and price_of_interest - price_of_interest * percentage <= current_price <= price_of_interest + price_of_interest * percentage :
                                result_array.append(ticker['symbol'])
        return result_array

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
    time.sleep(200)
    second_run = getListOfTickersCloseToLevel()

    # Reset Already visited charts after x loops
    if counter == 4:
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