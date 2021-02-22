import numpy as np
import cbpro
import time
import pandas as pd
import requests
import json
from twilio.rest import Client
import config

# -----------------------------------------------------------------------------------------------------------------------
#CoinbasePro API
apiKey = config.apiKey
apiSecret = config.apiSecret
passphrase = config.passphrase
auth_client = cbpro.AuthenticatedClient(apiKey, apiSecret, passphrase)

#Twilio API
account_sid = config.account_sid
auth_token = config.auth_token
client = Client(account_sid, auth_token)

# -----------------------------------------------------------------------------------------------------------------------
# Amount to initially invest
initInvestment = 100.00

# Currency to trade, for reference:
# 'BCH-USD' = Bitcoin Cash, 'BTC-USD' = Bitcoin, 'ETH-USD' = Ether
# Set crypto currency
currency = 'COMP-USD'

# Amount that will be used for purchase starts at the initial amount
funding = initInvestment

# Will return the ID of your specific currency account
def getSpecificAccount(cur):
    x = auth_client.get_accounts()
    for account in x:
        if account['currency'] == cur:
            return account['id']

# Get the currency's specific ID
# Change the number at the end to match the number of characters for the currency ignoring the '-USD' part
# EX: BTC-USD should just be 3 while COMP-USD should be 4.
while True:
    try:
        specificID = getSpecificAccount(currency[:4])
    except:
        continue
    break
# We will keep track of how many iterations our bot has done
iteration = 1

# Start off by looking to buy
buy = True

# Initializing variable we track and update through each iteration of the script
bought_price = 0.00

take_profit = 0.00

new_sell_signal = 0.00

profitCount = 0

num_buys = 0

num_sells = 0

take_profit_txt = 0

boll_Signal = 0.00

sma_Signal = 0.00

current = 0.00

#--------------------------------------------------------------------------
# This first function gets the Bollinger Band Buy signal.
# The data is pulled from binance.us since we can pull 1000 candlesticks from their api vs the 300 from coinbasepro
def getBollBuySignal(curr):
    # Set bitcoin currency
    currency = ''
    for i in range(len(curr)):
        if curr[i] != '-':
            currency += curr[i]
    limit = '1000'
    # -----------------------------------------------------------------------------------------------------------------------
    # Some variables for pulling data from Binance
    # The interval can be set with: m->minutes, h->hours, d->days, w->weeks,M->months
    # 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    base = 'https://api.binance.us'
    endpoint = '/api/v3/klines'
    params = '?&symbol=' + currency + '&interval=15m' + '&limit=' + limit

    url = base + endpoint + params

    ### Begin Loop and get Historic Data ###
    while True:
        while True:
            try:
                # Pulls the historical data from coinbase. The granularity is in seconds.
                data = requests.get(url)
                dictionary = json.loads(data.text)

                # The line below just puts the historic data we pulled into a data frame
                historic_df = pd.DataFrame.from_dict(dictionary)
                historic_df = historic_df.drop(range(6, 12), axis=1)

                # This gives the columns meaning full names based on what we pull
                col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
                historic_df.columns = col_names

                # Changing the columns to floats
                historic_df['open'] = historic_df['open'].astype(float)
                historic_df['high'] = historic_df['high'].astype(float)
                historic_df['low'] = historic_df['low'].astype(float)
                historic_df['close'] = historic_df['close'].astype(float)
                historic_df['volume'] = historic_df['volume'].astype(float)

                # Get latest data and show to the user for reference

            except:
                # In case something went wrong with binance
                continue
            break
        # -----------------------------------------------------------------------------------------------------------------------
        # Adding the simple moving average and typical price
        historic_df['SMA'] = historic_df.close.rolling(20).mean()

        # Calculating the Standard Deviation, BOLU and BOLD
        historic_df['STD'] = historic_df['close'].rolling(20).std()

        # Calculating upper Bollinger band
        historic_df['BOLU'] = historic_df['SMA'] + (historic_df['STD'] * 2)

        # Calculating lower Bollinger band
        historic_df['BOLD'] = historic_df['SMA'] - (historic_df['STD'] * 2)

        # Calculating second upper Bollinger band
        historic_df['BOLU2'] = historic_df['SMA'] + (historic_df['STD'])

        # Calculating second lower Bollinger band
        historic_df['BOLD2'] = historic_df['SMA'] - (historic_df['STD'])

        # -----------------------------------------------------------------------------------------------------------------------
        # calculating buy and sell signals
        # creates a df of just the last row of the historic_df
        buy_sell_df = historic_df.iloc[-1:]
        # storing the last value of the moving averages in side the bollinger bands
        buy_signal = buy_sell_df['BOLD2']
        # Changing the values to floats for if condition comparisons
        buy_signal = float(buy_signal)

        break

    return buy_signal

# This function pulls the Simple Moving Average Buy Signal
def getSMABuySignal(curr):
    # Set bitcoin currency
    currency = ''
    for i in range(len(curr)):
        if curr[i] != '-':
            currency += curr[i]
    limit = '500'
    # -----------------------------------------------------------------------------------------------------------------------
    # Some variables for pulling data from Binance
    # The interval can be set with: m->minutes, h->hours, d->days, w->weeks,M->months
    # 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    base = 'https://api.binance.us'
    endpoint = '/api/v3/klines'
    params = '?&symbol=' + currency + '&interval=15m' + '&limit=' + limit

    url = base + endpoint + params
    ### Begin Loop and get Historic Data ###
    while True:
        while True:
            try:
                # Pulls the historical data from coinbase. The granularity is in seconds.
                data = requests.get(url)
                dictionary = json.loads(data.text)

                # The line below just puts the historic data we pulled into a data frame
                historic_df = pd.DataFrame.from_dict(dictionary)
                historic_df = historic_df.drop(range(6, 12), axis=1)

                # This gives the columns meaning full names based on what we pull
                col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
                historic_df.columns = col_names

                # Changing the columns to floats
                historic_df['open'] = historic_df['open'].astype(float)
                historic_df['high'] = historic_df['high'].astype(float)
                historic_df['low'] = historic_df['low'].astype(float)
                historic_df['close'] = historic_df['close'].astype(float)
                historic_df['volume'] = historic_df['volume'].astype(float)

                # Get latest data and show to the user for reference

            except:
                # In case something went wrong with binance
                continue
            break
        # -----------------------------------------------------------------------------------------------------------------------
        # Adding the simple moving average and typical price
        historic_df['SMA'] = historic_df.close.rolling(21).mean()

        # -----------------------------------------------------------------------------------------------------------------------
        # calculating buy and sell signals
        # creates a df of just the last row of the historic_df
        buy_sell_df = historic_df.iloc[-1:]
        # storing the last value of the moving averages in side the bollinger bands
        buy_signal = buy_sell_df['SMA']
        # Changing the values to floats for if condition comparisons
        buy_signal = float(buy_signal)

        break

    # This is shows our graph to us.

    return buy_signal

# This functions checks the current price of the coin from coinbasepro
def getCurrentPrice(curr):
    coin = curr
    base = 'https://api.pro.coinbase.com'
    endpoint = '/products/' + coin + '/trades'

    url = base + endpoint

    data = requests.get(url)
    dictionary = json.loads(data.text)

    first_dic = dictionary[1]
    currentPrice = first_dic['price']

    return currentPrice

#-----------------------------------------------------------------------------------------------------------------------
### Begin Loop and get Historic Data ###

while True:

    try:
        #Pulls the historical data from binance and the current price from coinbase.
        boll_Signal = getBollBuySignal(currency)
        sma_Signal = getSMABuySignal(currency)
        current = getCurrentPrice(currency)

    except:
        # In case something went wrong with cbpro
        print("Error Encountered")

################################################################################
### Variables used to calculate how much we can buy and profits###

    # The maximum amount of Cryptocurrency that can be purchased with your funds
    possiblePurchase = (float(funding)) / float(current)

    # The amount of currency owned
    while True:
        try:
            owned = float(auth_client.get_account(specificID)['available'])
        except:
            continue
        break
    # The value of the cryptourrency in USD
    possibleIncome = float(current) * owned

    ################################################################################
    ###Decision Making###

    # Buy Conditions:
    # Checks that the current price is below both buy signals.
    # If you just want to use one strategy change the second 'and' to 'or' in the if statement below
    if (buy == True and float(current) < float(boll_Signal)) and (buy == True and float(current) < float(sma_Signal)):
        # Place the order
        auth_client.place_market_order(product_id=currency, side='buy', funds=str(funding))

        num_buys += 1

        newData = auth_client.get_product_ticker(product_id=currency)
        afterBuyPrice = newData['price']
        # Print message in the terminal for reference
        message = "Buying Approximately " + str(possiblePurchase) + " " + \
                  currency + "  Now @ " + str(afterBuyPrice) + "/Coin. TOTAL = " + str(funding)
        print(message)
        # Txt notification
        txt_message = client.messages \
            .create(
            body=message,
            from_= config.from_,
            to=config.to
        )
        print(txt_message.sid)

        # Update funding level and Buy variable
        amount_spent = funding
        funding = 0
        buy = False
        bought_price = (float(current) + float(afterBuyPrice)) /2
        # Setting the sell signal at 4%
        # You can change to 5% with 1.05 or 10% with 1.10
        new_sell_signal = bought_price * 1.04
        # adjust profit level if price goes up

    # We set a take profit level here if the current price is greater than the sell signal
    # The take profit level is 2% less than the sell signal.
    # If you just want 1% less change .98 to .99 or for 3% less put it to .97
    if buy == False and float(current) > new_sell_signal and (float(current) * .98) > take_profit:
        take_profit = float(current) * .98

        take_profit_txt += 1

    # The script will text the first time the current price is greater than the take profit level
    if take_profit_txt ==1:

        message = "The profit level for " + currency + " has been reached or passed, and your current take_profit level is: " + str(take_profit)
        txt_message = client.messages \
           .create(
           body=message,
           from_= config.from_,
           to= config.to
        )
        print(txt_message.sid)

        take_profit_txt += 1

    # Checks if the current price is less than or equal to the take_profit level. If it is then it sells all the coins
    if buy == False and (float(current) <= take_profit):

        # Place the order
        auth_client.place_market_order(product_id=currency, side='sell', size=str(owned))

        num_sells += 1
        take_profit_txt = 0

        #To accurately count the profit count.
        if profitCount == 0:
            profitCount = float(possibleIncome) - (initInvestment + profitCount)

        else:
            saleProfit = float(possibleIncome) - float(amount_spent)
            profitCount += saleProfit


        # Updating the funding to use the profit plus original funding
        funding = initInvestment + profitCount
        funding = int(funding)
        # Print message in the terminal for reference
        message = "Selling " + str(owned) + " " + currency + "Now @ " + \
                str(current) + "/Coin. TOTAL = " + str(possibleIncome) + " Your profit so far is: " + str(profitCount)
        print(message)
        # Txt Notification
        txt_message = client.messages \
            .create(
            body=message,
            from_= config.from_,
            to= config.to
        )
        print(txt_message.sid)

        # Updating  variables
        buy = True
        bought_price = 0.00
        new_sell_signal = 0.00
        take_profit = 0.00
        # Stop loss: sell everything and stop trading if your value is less than 80% of initial investment
    if buy == False and (float(current) <= (0.90 * bought_price)):

        # If there is any of the crypto owned, sell it all
        if owned > 0.0:
            auth_client.place_market_order(product_id=currency, side='sell', size=str(owned))
            print("STOP LOSS SOLD ALL")

        # Txt notification
        txt_message = client.messages \
            .create(
            body='Stop Loss has been triggered!',
            from_= config.from_,
            to= config.to
        )

        print(
            txt_message.sid)  
        # Will break out of the while loop and the program will
        # Printing here to make the details easier to read in the terminal

        buy = True
        bought_price = 0.00
        new_sell_signal = 0.00
        break


    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("iteration number", iteration)

    # Print the details for reference
    print("Current Price: ", current)
    print("Your Funds = ", funding)
    print("You Own ", owned, currency)
    print("The Boll buy signal is at: ", str(boll_Signal))
    print("The SMA buy signal is at: ", str(sma_Signal))
    print("The sell signal is at: ", str(new_sell_signal))
    print("Take profit level: ", str(take_profit))
    print("Your profit count so far: ", str(profitCount))
    print("You bought at: ", str(bought_price))
    print("The number of times the script has bought:", str(num_buys))
    print("The number of times the script has sold:", str(num_sells))

    # Wait time in seconds and iteration count
    time.sleep(11)
    iteration += 1

