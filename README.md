# bitcom-python-umapi

## bit.com python api for SPOT, COIN-M, USD-M system

A reference demo bit.com API client including (SPOT, COIN-M, USD-M)

feel free to copy and modify to suit your need

### API request/response format
https://www.bit.com/docs/en-us/spot.html#order

### Guidelines for account mode
https://www.bit.com/docs/en-us/spot.html#guidelines-for-account-mode

### API Host:
https://www.bit.com/docs/en-us/spot.html#spot-api-hosts-production



## demo

```python
if __name__ == '__main__':
    # api_host = "https://api.bit.com" # production

    api_host = "https://betaapi.bitexch.dev" # testnet
    ak = "<input_your_access_key>"
    sk = "<input_your_private_key>"
    client = BitClient(ak, sk, api_host)

    mode_resp = client.um_query_account_mode()
    mode = mode_resp['data']['account_mode']
    
    if mode == 'um':
        um_account = client.um_query_accounts()
        print(um_account)
    elif mode == 'classic':
        classic_account_btc = client.query_accounts({'currency':'BTC'})
        classic_account_eth = client.query_accounts({'currency':'ETH'})
        classic_account_bch = client.query_accounts({'currency':'BCH'})
        classic_account_spot = client.spot_query_accounts({})

        print('BTC account = ' + str(classic_account_btc))
        print('ETH account = ' + str(classic_account_eth))
        print('BCH account = ' + str(classic_account_bch))
        print('Spot account = ' + str(classic_account_spot))

    else:
        print('account in transient state: ' + mode)
```        
