import schwabdev
from datetime import datetime, timedelta
from dotenv import load_dotenv
from time import sleep
import os


def main():
    # place your app key and app secret in the .env file
    load_dotenv()  # load environment variables from .env file

    client = schwabdev.Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))
    client.update_tokens_auto()  # update tokens automatically (except refresh token)

    print("\n\nAccounts and Trading - Accounts.")

    # get account number and hashes for linked accounts
    print("|\n|client.account_linked().json()", end="\n|")
    linked_accounts = client.account_linked().json()
    print(linked_accounts)
    # this will get the first linked account
    account_hash = linked_accounts[0].get('hashValue')

    # get a single quote
    print("|\n|client.quote(\"UPST\").json()", end="\n|")
    print(client.quote("UPST").json())


if __name__ == '__main__':
    print("Welcome to the unofficial Schwab interface!\nGithub: https://github.com/tylerebowers/Schwab-API-Python")
    main()  # call the user code above
