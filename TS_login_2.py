from ts.client import TradeStationClient

ts_client = TradeStationClient(
    username="yogenpatel",
    client_id="S2KRtHJwMPn12rMBMVG795eTiCfbCm11",
    client_secret="ZCqdwVdJClsJE-2FkW7pWdsxM5J_JYJ3QgZmIlLVCyt3AgnmUNLTN5OOTxJOVN4q",
    redirect_uri="http://localhost:27353/callback",
    paper_trading=True  # Use True or False instead of "PAPER_TRADING"
)

# Login to the client
if ts_client.login():
    print("Login successful.")
    
    try:
        # Fetch quotes for AMZN
        url_endpoint = ts_client._api_endpoint('data/quote/AMZN')
        params = {'access_token': ts_client.state['access_token']}
        response = ts_client._handle_requests(url=url_endpoint, method='get', args=params)
        
        # Print the quote
        print("Quote for AMZN:")
        print(response)
    except Exception as e:
        print(f"Error fetching quote: {e}")
else:
    print("Login failed.")


