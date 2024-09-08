from schwab_api import Schwab
import pprint

# Initialize our schwab instance
api = Schwab()

# Login using playwright
print("Logging into Schwab")
logged_in = api.login(
    username="shivaniypatel",
    password="Sm@rtSh1v#",
    totp_secret="CB5E7XEJGRLBGCNJWN472ERQFKCEH4EV" # Get this by generating TOTP at https://itsjafer.com/#/schwab
)

# Get information about a few tickers
quotes = api.quote_v2(["$SPX"])
pprint.pprint(quotes)

# Get information about all accounts holdings
print("Getting account holdings information")
account_info = api.get_account_info()
pprint.pprint(account_info)

print("The following account numbers were found: " + str(account_info.keys()))
'''
print("Placing a dry run trade for AAPL stock")
# Place a dry run trade for account 99999999
messages, success = api.trade_v2(
    ticker="AAPL", 
    side="Buy", #or Sell
    qty=1, 
    account_id=68401015, # Replace with your account number
    dry_run=True # If dry_run=True, we won't place the order, we'll just verify it.
)

print("The order verification was " + "successful" if success else "unsuccessful")
print("The order verification produced the following messages: ")
pprint.pprint(messages)
'''
