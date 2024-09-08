import requests
import time
from datetime import datetime, timezone

class Client:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, environment: str, expiration_buffer: int = 30) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.expiration_buffer = expiration_buffer
        self.expires_in = 0
        self.time_of_last_refresh = 0
        self.auth_url = "https://signin.tradestation.com/oauth/token"
        self.account_id = "Unknown"

        if environment.upper() == "LIVE":
            self.base_url = "https://api.tradestation.com/v3"
        else:
            self.base_url = "https://sim-api.tradestation.com/v3"

    def get_access_token(self, force: bool = False) -> str:
        seconds_since_last_token = time.time() - self.time_of_last_refresh

        if force or seconds_since_last_token > self.expires_in - self.expiration_buffer:
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

    def fetch_account_info(self):
        url = f"{self.base_url}/brokerage/accounts"
        headers = self.get_auth_header()
        response = requests.get(url, headers=headers)
        accounts_data = response.json()
        if "Accounts" in accounts_data and len(accounts_data["Accounts"]) > 0:
            self.account_id = accounts_data["Accounts"][0]["AccountID"]

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

    def fetch_option_quotes(self, symbol: str, expiration_date: str, closest_strike: float) -> dict:
        bid_ask_values = {"C": {}, "P": {}}
        url = f"{self.base_url}/marketdata/stream/options/quotes"
        for option_type in ['C', 'P']:
            formatted_strike = f"{int(closest_strike)}" if closest_strike.is_integer() else f"{closest_strike}"
            symbol_formatted = f"{symbol} {expiration_date}{option_type}{formatted_strike}"
            querystring = {"legs[0].Symbol": symbol_formatted}
            headers = self.get_auth_header()
            response = requests.get(url, headers=headers, params=querystring, stream=True)

            for line in response.iter_lines():
                if line:
                    quote = line.decode('utf-8')
                    if "Ask" in quote and "Bid" in quote:
                        quote_data = eval(quote)
                        bid_ask_values[option_type]["Bid"] = quote_data.get("Bid", "N/A")
                        bid_ask_values[option_type]["Ask"] = quote_data.get("Ask", "N/A")
                        break  # Stop after receiving the first quote

            response.close()  # Ensure the connection is closed after the first quote

        return bid_ask_values

# Initialize client
client = Client(
    client_id="S2KRtHJwMPn12rMBMVG795eTiCfbCm11",
    client_secret="ZCqdwVdJClsJE-2FkW7pWdsxM5J_JYJ3QgZmIlLVCyt3AgnmUNLTN5OOTxJOVN4q",
    refresh_token="q2hjlp1--h4fQu3JkP0D3JVGDvLY1jDCNxd8-T_SbsYpn",
    environment="SIM"
)

# Fetch and print account information
client.fetch_account_info()
print(f"Account Number: {client.account_id}")

# List of symbols to process
symbols = ["SPY", "AAPL"]

for symbol in symbols:
    # Get the last price
    quotes_url = f"{client.base_url}/marketdata/quotes/{symbol}"
    auth_header = client.get_auth_header()
    quotes = requests.get(quotes_url, headers=auth_header).json()['Quotes']
    last_price = next((quote['Last'] for quote in quotes if quote['Symbol'] == symbol), None)

    if last_price is not None:
        last_price = float(last_price)
        # Get option strikes
        strikes = client.get_option_strikes(symbol)
        closest_strike = client.find_closest_strike(strikes, last_price)

        # Get option expirations
        expirations = client.get_option_expirations(symbol)
        closest_expiration = client.find_closest_expiration(expirations)
        expiration_date = datetime.fromisoformat(closest_expiration["Date"].replace("Z", "")).strftime("%y%m%d")  # Format as YYMMDD

        # Fetch option quotes
        bid_ask_values = client.fetch_option_quotes(symbol, expiration_date, closest_strike)

        # Print results
        print(f"Symbol: {symbol} | Last: {last_price} | Strike: {closest_strike} | Exp: {expiration_date}")
        print(f"C Option Bid: {bid_ask_values['C']['Bid']} | Ask: {bid_ask_values['C']['Ask']}")
        print(f"P Option Bid: {bid_ask_values['P']['Bid']} | Ask: {bid_ask_values['P']['Ask']}")
