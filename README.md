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
    
    # get account information
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

    # query USD-M(linear) positions
    client.linear_query_positions({
        'currency':'USD'
    })    

    # place USD-M(linear) limit order
    client.linear_place_order({
        'instrument_id': 'ETH-USD-PERPETUAL',
        'side':'buy',
        'qty':'0.05',
        'price': '1500',
        'order_type':'limit',
        'post_only': True
    })

    # place trigger limit order
    client.linear_place_order({
        'instrument_id': 'BTC-USD-PERPETUAL',
        'side':'buy',
        'qty':'0.01',
        'order_type':'trigger-market',
        'time_in_force': 'gtc',
        'stop_price': '25800',
        'trigger_type': 'last-price'
    })    

    # new batch orders
    client.linear_new_batch({
        'currency': 'USD', 
        'orders_data': [
            {'instrument_id': 'XRP-USD-PERPETUAL', 'side': 'buy', 'qty': '200', 'price': '0.371', 'order_type': 'limit', 'post_only': True}, 
            {'instrument_id': 'XRP-USD-PERPETUAL', 'side': 'buy', 'qty': '300', 'price': '0.36', 'order_type': 'limit', 'post_only': True}, 
            {'instrument_id': 'XRP-USD-PERPETUAL', 'side': 'buy', 'qty': '400', 'price': '0.37', 'order_type': 'limit', 'post_only': True}
        ]
    })


    # cancel order
    client.linear_cancel_order({
        'currency':'USD',
        'instrument_id': 'BTC-USD-PERPETUAL',
        'order_id': '14232321'
    })    


    # amend order
    client.linear_amend_order({
        'currency':'USD',
        'instrument_id': 'XRP-USD-PERPETUAL',
        'order_id': '58317173',
        'price': '0.3'
    })

    # batch amend orders
    client.linear_amend_batch({
        'currency':'USD',
        'orders_data': [
            {
                'instrument_id': 'XRP-USD-PERPETUAL',
                'order_id': '58317172',
                'price': '0.32'
            },
            {
                'instrument_id': 'XRP-USD-PERPETUAL',
                'order_id': '58317173',
                'price': '0.33'
            }            
        ]
    }) 

```        
