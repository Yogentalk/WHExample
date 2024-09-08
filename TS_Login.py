from ts.client import TradeStationClient
import json
from datetime import datetime, timedelta

# Your TradeStation API credentials
USERNAME = "yogenpatel"
CLIENT_ID = "S2KRtHJwMPn12rMBMVG795eTiCfbCm11"
CLIENT_SECRET = "ZCqdwVdJClsJE-2FkW7pWdsxM5J_JYJ3QgZmIlLVCyt3AgnmUNLTN5OOTxJOVN4q"
REDIRECT_URI = "https://127.0.0.1"

# Create the TradeStation client
try:
    ts_client = TradeStationClient(
        username=USERNAME,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        paper_trading=True  # Set to True for SIM environment
    )
    print("Successfully created TradeStation client.")
except Exception as e:
    print(f"Error creating TradeStation client: {e}")
    exit(1)

# Function to fetch and print quotes
def fetch_quotes(symbol):
    try:
        quotes = ts_client.quotes(symbols=[symbol])
        print(f"\nQuotes for {symbol}:")
        print(json.dumps(quotes, indent=2))
    except Exception as e:
        print(f"Error fetching quotes for {symbol}: {e}")

# Function to fetch and print historical bars
def fetch_historical_bars(symbol, days=30):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        bars = ts_client.get_bars(
            symbol=symbol,
            interval=1,
            unit='Daily',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        print(f"\nHistorical bars for {symbol} (last {days} days):")
        print(json.dumps(bars, indent=2))
    except Exception as e:
        print(f"Error fetching historical bars for {symbol}: {e}")

# Main execution
if __name__ == "__main__":
    symbol = '$SPX'  # S&P 500 index

    # Fetch quotes
    fetch_quotes(symbol)

    # Fetch historical bars
    fetch_historical_bars(symbol)

    print("\nScript execution completed.")
