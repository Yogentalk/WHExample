import pandas as pd
import yfinance as yf
from time import sleep
from datetime import datetime, time
from telegram import Bot
import asyncio
import pytz
import pandas_ta as ta

# Initialize Telegram bot with your actual API key and chat ID
TELEGRAM_API_KEY = '6795973832:AAHEJsp5oIx7wKYLsPt3am7VSIiK5gHs6bo'
TELEGRAM_CHAT_ID = '1203986483'
bot = Bot(token=TELEGRAM_API_KEY)

# Define market hours (7:30 AM to 3:30 PM Central Time)
MARKET_OPEN = time(7, 30)
MARKET_CLOSE = time(15, 30)
CENTRAL_TZ = pytz.timezone('US/Central')

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def fetch_and_analyze_stock(stock_symbol, loop):
    ticker = yf.Ticker(stock_symbol)
    data = ticker.history(period="1mo", interval="5m")  # Fetching 1 month of 5m data

    # Calculate the MACD and Signal Line using pandas_ta with updated fast, slow, and signal values
    data.ta.macd(close='close', fast=10, slow=16, signal=6, append=True)

    # Check for MACD and Signal Line crossovers in the last two rows
    last_row = data.iloc[-1]
    second_last_row = data.iloc[-2]

    if second_last_row['MACD_10_16_6'] > second_last_row['MACDs_10_16_6'] and last_row['MACD_10_16_6'] < last_row['MACDs_10_16_6']:
        message = f'{stock_symbol}: Cross Below Signal Line at {datetime.now(CENTRAL_TZ)}'
        print(message)
        loop.run_until_complete(send_telegram_message(message))
    elif second_last_row['MACD_10_16_6'] < second_last_row['MACDs_10_16_6'] and last_row['MACD_10_16_6'] > last_row['MACDs_10_16_6']:
        message = f'{stock_symbol}: Cross Above Signal Line at {datetime.now(CENTRAL_TZ)}'
        print(message)
        loop.run_until_complete(send_telegram_message(message))

def is_market_open():
    now = datetime.now(CENTRAL_TZ).time()
    return MARKET_OPEN <= now <= MARKET_CLOSE

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    stock_symbols = ['SPY', 'QQQ', '^GSPC']

    while True:
        if is_market_open():
            print(f"Market is open. Fetching data every minute. {datetime.now(CENTRAL_TZ)}")
            for stock_symbol in stock_symbols:
                fetch_and_analyze_stock(stock_symbol, loop)
            sleep(60)  # Run every minute during market hours
        else:
            print(f"Market is closed. Waiting for market to open. {datetime.now(CENTRAL_TZ)}")
            sleep(1800)  # Check every 30 minutes if market is open
