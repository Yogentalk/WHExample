import pandas as pd
import yfinance as yf
from time import sleep
from datetime import datetime
from telegram import Bot
import asyncio
from schwab_api import Schwab
from dotenv import load_dotenv
import os
import pprint

# Initialize Telegram bot with your actual API key and chat ID
TELEGRAM_API_KEY = '6795973832:AAHEJsp5oIx7wKYLsPt3am7VSIiK5gHs6bo'
TELEGRAM_CHAT_ID = '1203986483'
bot = Bot(token=TELEGRAM_API_KEY)

# Initialize Schwab instance
api = Schwab()

# Login to Schwab
print("Logging into Schwab")
logged_in = api.login(
    username="shivaniypatel",
    password="Sm@rtSh1v#",
    totp_secret="CB5E7XEJGRLBGCNJWN472ERQFKCEH4EV"  # Get this using itsjafer.com/#/schwab.
)

if logged_in:
    print("Login successful!")
    account_info = api.get_account_info_v2()
    account_id = next(iter(account_info))
    print(f"Account Number: {account_id}")
else:
    print("Login failed!")

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def fetch_and_analyze_stock(stock_symbol, loop):
    ticker = yf.Ticker(stock_symbol)
    data = ticker.history(period="1mo", interval="5m")  # Fetching 1 month of 5-minute data

    # Calculate the 12-period EMA
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()

    # Calculate the 26-period EMA
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()

    # Calculate MACD (the difference between 12-period EMA and 26-period EMA)
    data['MACD'] = data['EMA12'] - data['EMA26']

    # Calculate the 9-period EMA of MACD (Signal Line)
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Check for MACD and Signal Line crossovers in the last two rows
    last_row = data.iloc[-1]
    second_last_row = data.iloc[-2]

    if second_last_row['MACD'] > second_last_row['Signal_Line'] and last_row['MACD'] < last_row['Signal_Line']:
        message = f'{stock_symbol}: Cross Below Signal Line at {datetime.now()}'
        print(message)
        loop.run_until_complete(send_telegram_message(message))
        fetch_and_place_order("put")
    elif second_last_row['MACD'] < second_last_row['Signal_Line'] and last_row['MACD'] > last_row['Signal_Line']:
        message = f'{stock_symbol}: Cross Above Signal Line at {datetime.now()}'
        print(message)
        loop.run_until_complete(send_telegram_message(message))
        fetch_and_place_order("call")

def fetch_and_place_order(option_type):
    option_chain = api.get_options_chains_v2('$SPX')

    df1 = pd.json_normalize(option_chain, ['Expirations', 'Chains', 'Legs'], [['Expirations', 'ExpirationGroup']])
    df2 = pd.json_normalize(df1['Expirations.ExpirationGroup'])
    df1.drop('Expirations.ExpirationGroup', axis=1, inplace=True)
    df = pd.concat([df1, df2], axis=1)
    df = df.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(df)

    closest_expiration_options = df[(df.DaysUntil == df.DaysUntil.min())]

    current_price = float(option_chain['UnderlyingData']['Last'])

    if option_type == "call":
        ATM_option_index = abs(closest_expiration_options[closest_expiration_options.OptionType == "C"].Strk - current_price).idxmin()
        ATM_option = closest_expiration_options.iloc[ATM_option_index]
        symbols = [ATM_option.Sym]
        instructions = ["BTO"]
        quantities = [1]
        order_type = 202 # net debit
        limit_price = (ATM_option.Ask + ATM_option.Bid) / 2
        print(f"Call ATM option: {ATM_option.Sym} Ask: {ATM_option.Ask} Bid: {ATM_option.Bid}")
    elif option_type == "put":
        ATM_option_index = abs(closest_expiration_options[closest_expiration_options.OptionType == "P"].Strk - current_price).idxmin()
        ATM_option = closest_expiration_options.iloc[ATM_option_index]
        symbols = [ATM_option.Sym]
        instructions = ["BTO"]
        quantities = [1]
        order_type = 202 # net debit
        limit_price = (ATM_option.Ask + ATM_option.Bid) / 2
        print(f"Put ATM option: {ATM_option.Sym} Ask: {ATM_option.Ask} Bid: {ATM_option.Bid}")

    messages, success = api.option_trade_v2(
        strategy=0,  # Naked option strategy
        symbols=symbols,
        instructions=instructions,
        quantities=quantities,
        account_id=account_id,
        order_type=order_type,
        dry_run=True,
        limit_price=limit_price
    )

    print("The order verification was " + ("successful" if success else "unsuccessful"))
    print("The order verification produced the following messages: ")
    pprint.pprint(messages)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stock_symbols = ['^GSPC']

    while True:
        for stock_symbol in stock_symbols:
            fetch_and_analyze_stock(stock_symbol, loop)
        sleep(60)  # Run every 1 minute
