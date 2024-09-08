import pandas as pd
import yfinance as yf
from time import sleep
from datetime import datetime
from telegram import Bot
import asyncio

# Initialize Telegram bot with your actual API key and chat ID
TELEGRAM_API_KEY = '6795973832:AAHEJsp5oIx7wKYLsPt3am7VSIiK5gHs6bo'
TELEGRAM_CHAT_ID = '1203986483'
bot = Bot(token=TELEGRAM_API_KEY)

async def send_telegram_message(message):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def fetch_and_analyze_stock(stock_symbol, loop):
    ticker = yf.Ticker(stock_symbol)
    data = ticker.history(period="1mo", interval="1h")  # Fetching 5 days of 5-minute data

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
    elif second_last_row['MACD'] < second_last_row['Signal_Line'] and last_row['MACD'] > last_row['Signal_Line']:
        message = f'{stock_symbol}: Cross Above Signal Line at {datetime.now()}'
        print(message)
        loop.run_until_complete(send_telegram_message(message))

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    stock_symbols = ['GOOG', 'META', 'TSLA', 'NVDA', 'AMD', 'SPY', 'QQQ', 'UPST', 'MSFT']

    while True:
        for stock_symbol in stock_symbols:
            fetch_and_analyze_stock(stock_symbol, loop)
        sleep(180)  # Run every 3 minutes
