import webbrowser
import requests

client_id = "S2KRtHJwMPn12rMBMVG795eTiCfbCm11"
client_secret = "ZCqdwVdJClsJE-2FkW7pWdsxM5J_JYJ3QgZmIlLVCyt3AgnmUNLTN5OOTxJOVN4q"
redirect_uri = "http://localhost:3000"
auth_url = f"https://signin.tradestation.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid profile MarketData ReadAccount Trade"

# Open the authorization URL in the web browser
webbrowser.open(auth_url)

# After the user authorizes the app, they will be redirected to your redirect URI with a code parameter.
# Extract the authorization code from the URL.
authorization_code = input("Enter the authorization code: ")

token_url = "https://signin.tradestation.com/oauth/token"
payload = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": redirect_uri,
    "code": authorization_code,
}

response = requests.post(token_url, data=payload)
tokens = response.json()

# Print the response for debugging
print("Response from token endpoint:", tokens)

# Extract and save the refresh token
refresh_token = tokens.get("refresh_token")
if refresh_token:
    print("Refresh Token:", refresh_token)
    # Save the refresh token to a file for later use
    with open("refresh_token.txt", "w") as file:
        file.write(refresh_token)
else:
    print("Error: Refresh token not found in the response.")
