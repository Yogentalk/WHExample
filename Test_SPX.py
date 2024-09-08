from schwab_api import Schwab
from dotenv import load_dotenv
import os
import pandas as pd
import pprint


# Initialize our schwab instance
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

# Get quotes for options.
option_chain = api.get_options_chains_v2('$SPX') #try also with parameter greeks = True 

# The json output is deeply nested so here is how you can work with it:
# Normalizing the data into a pandas DataFrame
df1 = pd.json_normalize(option_chain,['Expirations','Chains','Legs'],[['Expirations','ExpirationGroup']])
# Normalizing Expirations.ExpirationGroup
df2 = pd.json_normalize(df1['Expirations.ExpirationGroup'])
# Dropping the column Expirations.ExpirationGroup in df1 and concatenating the two dataframes (side by side)
df1.drop('Expirations.ExpirationGroup',axis=1, inplace=True)
df = pd.concat([df1,df2],axis=1)
# Converting strings to numbers when relevant. Keeping strings is conversion is not possible.
df = df.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(df)

# Let's isolate options with closest expiration date:
closest_expiration_options = df[(df.DaysUntil==df.DaysUntil.min())]

# Let's find the call and put options with closest strike price to current price:
# First let's grab the current price. No need to use api.quote_v2(), it's already in chains
current_price = float(option_chain['UnderlyingData']['Last'])
# Finding the index of the closest strike prices
ATM_call_index = abs(closest_expiration_options[closest_expiration_options.OptionType=="C"].Strk - current_price).idxmin()
ATM_put_index = abs(closest_expiration_options[closest_expiration_options.OptionType=="P"].Strk - current_price).idxmin()
# Grabbing the rows at those indexes 
ATM_call_option = closest_expiration_options.iloc[ATM_call_index]
ATM_put_option = closest_expiration_options.iloc[ATM_put_index]
print(f"Call and Put ATM options (At The Money) with the closest expiration:")
print(f"Call: {ATM_call_option.Sym}         Ask: {ATM_call_option.Ask}      Bid: {ATM_call_option.Bid}")
print(f"Put:  {ATM_put_option.Sym}         Ask: {ATM_put_option.Ask}      Bid: {ATM_put_option.Bid}")
