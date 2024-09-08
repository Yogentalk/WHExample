import requests 
import time 
 
 
class Client: 
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, environment: str, expiration_buffer: int = 30) -> None: 
        self.client_id = client_id 
        self.client_id = "S2KRtHJwMPn12rMBMVG795eTiCfbCm11"
        self.client_secret = "ZCqdwVdJClsJE-2FkW7pWdsxM5J_JYJ3QgZmIlLVCyt3AgnmUNLTN5OOTxJOVN4q"
        self.refresh_token = "q2hjlp1--h4fQu3JkP0D3JVGDvLY1jDCNxd8-T_SbsYpn"
        self.expiration_buffer = expiration_buffer 
        self.expires_in = 0 
        self.time_of_last_refresh = 0 
        self.auth_url = "https" + "://signin.tradestation.com/oauth/token" 
 
        if environment.upper() == "LIVE": 
            self.base_url = "https" + "://api.tradestation.com/v3" 
        else: 
            self.base_url = "https" + "://sim-api.tradestation.com/v3" 
 
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
 
 
c = Client(client_id="XXXXXXXXXX", 
           client_secret="XXXXXXXXXX", 
           refresh_token="XXXXXXXXXX",      
           environment="SIM") 
 
# Get and print user accounts 
accounts_url = f"{c.base_url}/brokerage/accounts" 
auth_header = c.get_auth_header()  # Access token is only updated if it is near expiration or expired 
accounts = requests.get(accounts_url, headers=auth_header).json()['Accounts'] 
 
for account in accounts: 
    account_id = account['AccountID'] 
    account_type = account['AccountType'] 
    print(f"{account_id} - {account_type}") 
 
# Get and print symbol quotes 
quotes_url = f"{c.base_url}/marketdata/quotes/SPY,MSFT" 
auth_header = c.get_auth_header()  # Access token is only updated if it is near expiration or expired 
quotes = requests.get(quotes_url, headers=auth_header).json()['Quotes'] 
 
for quote in quotes: 
    symbol = quote['Symbol'] 
    last = quote['Last'] 
    print(f"Symbol: {symbol} Last: {last}") 
