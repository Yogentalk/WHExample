import requests
import time
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf
import pandas_ta as ta

class Client:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, environment: str, expiration_buffer: int = 30) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.expiration_buffer = expiration_buffer
        self.expires_in = 0
        self.time_of_last_refresh = 0
        self.auth_url = "https://signin.tradestation.com/oauth/token"

        if environment.upper() == "LIVE":
            self.base_url = "https://api.tradestation.com/v3"
        else:
            self.base_url = "https://sim-api.tradestation.com/v3"

    def get_access_token(self, force: bool = False) -> str:
        seconds_since_last_token = time.time() - self.time_of_last_refresh

        if (force or seconds_since_last_token > self.expires_in - self.expiration_buffer):
            payload = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
            }
            response = requests.request("POST", self.auth_url, data=payload)
            self.time_of_last_refresh = time.time()
            json_data = response.json()
            self.expires_in = int(json_data["expires_in"])
            self.access_token = json_data["access_token"]
            return self.access_token
        else:
            return self.access_token

    def get_auth_header(self, force: bool = False) -> dict:
        auth_header = {"Authorization": f"Bearer {self.get_access_token(force=force)}"}
        return auth_header

    def get_option_strikes(self, symbol: str) -> list:
        url = f"{self.base_url}/marketdata/options/strikes/{symbol}"
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        strikes_data = response.json()
        strikes = strikes_data.get("Strikes", [])
        return [float(strike[0]) for strike in strikes if isinstance(strike[0], str) and strike[0].replace('.', '', 1).isdigit()]

    def get_option_expirations(self, symbol: str) -> list:
        url = f"{self.base_url}/marketdata/options/expirations/{symbol}"
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        expirations_data = response.json()
        return expirations_data.get("Expirations", [])

    def find_closest_strike(self, strikes: list, last_price: float) -> float:
        closest_strike = min(strikes, key=lambda strike: abs(strike - last_price))
        return closest_strike

    def find_closest_expiration(self, expirations: list) -> dict:
        today = datetime.now(timezone.utc)
        closest_expiration = min(expirations, key=lambda exp: abs(datetime.fromisoformat(exp["Date"].replace("Z", "")).replace(tzinfo=timezone.utc) - today))
        return closest_expiration

    def fetch_option_quotes(self, symbol: str, expiration_date: str, closest_strike: float):
        url = f"{self.base_url}/marketdata/stream/options/quotes"
        bid_ask_values = {'C': {'Bid': None, 'Ask': None}, 'P': {'Bid': None, 'Ask': None}}

        for option_type in ['C', 'P']:
            formatted_strike = f"{int(closest_strike)}" if closest_strike.is_integer() else f"{closest_strike}"
            symbol_formatted = f"{symbol} {expiration_date}{option_type}{formatted_strike}"
            querystring = {"legs[0].Symbol": symbol_formatted}
            headers = self.get_auth_header()
            response = requests.get(url, headers=headers, params=querystring, stream=True)

            print(f"Fetching {option_type} Option Quote for {symbol_formatted}")

            for line in response.iter_lines():
                if line:
                    quote = line.decode('utf-8')
                    if "Ask" in quote and "Bid" in quote:
                        data = eval(quote)  # Unsafe, replace with a safer JSON parser if possible
                        bid_ask_values[option_type]['Bid'] = data.get("Bid", None)
                        bid_ask_values[option_type]['Ask'] = data.get("Ask", None)
                        break  # Stop after receiving the first quote
                    elif "Heartbeat" not in quote:
                        print(f"Received data: {quote}")
                        break  # Optionally stop after receiving the first non-heartbeat message

            response.close()  # Ensure the connection is closed after the first quote

        return bid_ask_values

# Initialize client
client = Client(
    client_id="S2KRtHJwMPn12rMBMVG795eTiCfbCm11",
    client_secret="ZCqdwVdJClsJE-2FkW7pWdsxM5J_JYJ3QgZmIlLVCyt3AgnmUNLTN5OOTxJOVN4q",
    refresh_token="q2hjlp1--h4fQu3JkP0D3JVGDvLY1jDCNxd8-T_SbsYpn",
    environment="SIM"
)

# Fetch SPX data from yfinance
spx_data = yf.download('^GSPC', period='1mo', interval='5m')

# Calculate MACD
macd = ta.macd(spx_data['Close'], 10, 16, 6)
spx_data = spx_data.join(macd)

macd_value = spx_data['MACD'].iloc[-1]
signal_value = spx_data['MACDs'].iloc[-1]

print(f"MACD Value: {macd_value}")
print(f"Signal Value: {signal_value}")

# Fetch SPX option data from TradeStation
symbol = "$SPX.X"

# Get the last price
quotes_url = f"{client.base_url}/marketdata/quotes/{symbol}"
auth_header = client.get_auth_header()
quotes = requests.get(quotes_url, headers=auth_header).json()['Quotes']
last_price = next((quote['Last'] for quote in quotes if quote['Symbol'] == symbol), None)

if last_price is not None:
    last_price = float(last_price)
    print(f"Symbol: SPX Last: {last_price}")

    # Get option strikes
    strikes = client.get_option_strikes(symbol)
    if strikes:
        closest_strike = client.find_closest_strike(strikes, last_price)
        print(f"Closest strike to {last_price} for SPX: {closest_strike}")
    else:
        print(f"No valid strike prices found for SPX")

    # Get option expirations
    expirations = client.get_option_expirations(symbol)
    if expirations:
        closest_expiration = client.find_closest_expiration(expirations)
        expiration_date = datetime.fromisoformat(closest_expiration["Date"].replace("Z", "")).strftime("%y%m%d")  # Format as YYMMDD
        print(f"Closest expiration for SPX: {expiration_date}")

        # Fetch option quotes
        bid_ask_values = client.fetch_option_quotes(symbol, expiration_date, closest_strike)

        # Print results
        print(f"Symbol: SPX | Last: {last_price} | Strike: {closest_strike} | Exp: {expiration_date}")
        print(f"C Option Bid: {bid_ask_values['C']['Bid']} | Ask: {bid_ask_values['C']['Ask']}")
        print(f"P Option Bid: {bid_ask_values['P']['Bid']} | Ask: {bid_ask_values['P']['Ask']}")
    else:
        print(f"No expiration data found for SPX")
else:
    print(f"No quote data found for SPX")

# Print account number
account_info_url = f"{client.base_url}/accounts"
account_response = requests.get(account_info_url, headers=client.get_auth_header())
account_data = account_response.json()
account_id = account_data['Accounts'][0]['AccountID'] if 'Accounts' in account_data and account_data['Accounts'] else 'Unknown'
print(f"Account Number: {account_id}")
