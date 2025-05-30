# A reference demo bit.com API client including (SPOT, COIN-M, USDT-M)
# feel free to copy and modify to suit your need
#
# API request/response format
# https://www.bit.com/docs/en-us/spot.html#order
#
# Guidelines for account mode
# https://www.bit.com/docs/en-us/spot.html#guidelines-for-account-mode
#
# API Host:
# https://www.bit.com/docs/en-us/spot.html#spot-api-hosts-production

import requests
import hashlib
import hmac
import time
import json
import os

class HttpMethod:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'


V1_WS_AUTH = '/v1/ws/auth'
V1_ACCOUNT_CONFIGS_COD = '/v1/account_configs/cod'


# SPOT
V1_SPOT_INSTRUMENTS = '/spot/v1/instruments'
V1_SPOT_ACCOUNTS = '/spot/v1/accounts'
V1_SPOT_ORDERS = '/spot/v1/orders'
V1_SPOT_CANCEL_ORDERS = '/spot/v1/cancel_orders'
V1_SPOT_OPENORDERS = '/spot/v1/open_orders'
V1_SPOT_USER_TRADES = '/spot/v1/user/trades'
V1_SPOT_AMEND_ORDERS = '/spot/v1/amend_orders'
V1_SPOT_TRANSACTION_LOGS = '/spot/v1/transactions'
V1_SPOT_WS_AUTH = '/spot/v1/ws/auth'
V1_SPOT_BATCH_ORDERS = '/spot/v1/batchorders'
V1_SPOT_AMEND_BATCH_ORDERS = '/spot/v1/amend_batchorders'
V1_SPOT_MMP_STATE = '/spot/v1/mmp_state'
V1_SPOT_MMP_UPDATE_CONFIG = '/spot/v1/update_mmp_config'
V1_SPOT_RESET_MMP = '/spot/v1/reset_mmp'
V1_SPOT_ACCOUNT_CONFIGS_COD = '/spot/v1/account_configs/cod'
V1_SPOT_ACCOUNT_CONFIGS = "/spot/v1/account_configs"
V1_SPOT_AGG_TRADES = "/spot/v1/aggregated/trades"

# UM
V1_UM_ACCOUNT_MODE = "/um/v1/account_mode"
V1_UM_ACCOUNTS = "/um/v1/accounts"
V1_UM_TRANSACTIONS = "/um/v1/transactions"
V1_UM_INTEREST_RECORDS = "/um/v1/interest_records"

# LINEAR
V1_LINEAR_POSITIONS = '/linear/v1/positions'
V1_LINEAR_ORDERS = '/linear/v1/orders'
V1_LINEAR_CANCEL_ORDERS = '/linear/v1/cancel_orders'
V1_LINEAR_OPENORDERS = '/linear/v1/open_orders'
V1_LINEAR_USER_TRADES = '/linear/v1/user/trades'
V1_LINEAR_AMEND_ORDERS = '/linear/v1/amend_orders'
V1_LINEAR_EST_MARGINS = '/linear/v1/margins'
V1_LINEAR_CLOSE_POS = '/linear/v1/close_positions'
V1_LINEAR_BATCH_ORDERS = '/linear/v1/batchorders'
V1_LINEAR_AMEND_BATCH_ORDERS = '/linear/v1/amend_batchorders'
V1_LINEAR_BLOCK_TRADES = '/linear/v1/blocktrades'
V1_LINEAR_USER_INFO = '/linear/v1/user/info'
V1_LINEAR_PLATFORM_BLOCK_TRADES = '/linear/v1/platform_blocktrades'
V1_LINEAR_ACCOUNT_CONFIGS = "/linear/v1/account_configs"
V1_LINEAR_LEVERAGE_RATIO = "/linear/v1/leverage_ratio"
V1_LINEAR_AGG_POSITIONS = "/linear/v1/aggregated/positions"
V1_LINEAR_AGG_TRADES = "/linear/v1/aggregated/trades"

class BitClient(object):

    def __init__(self, ak, sk, base_url, verbose=False):
        self.access_key = ak
        self.secret_key = sk
        self.base_url = base_url
        self.verbose_log = verbose

    #############################
    # call private API
    #############################
    def get_nonce(self):
        return str(int(round(time.time() * 1000)))

    def encode_list(self, item_list):
        list_val = []
        for item in item_list:
            obj_val = self.encode_object(item)
            list_val.append(obj_val)
            # print(list_val)
        # list_val = sorted(list_val)
        output = '&'.join(list_val)
        output = '[' + output + ']'
        return output

    def encode_object(self, obj):
        if isinstance(obj, (str, int)):
            return obj

        # treat obj as dict
        sorted_keys = sorted(obj.keys())
        ret_list = []
        for key in sorted_keys:
            val = obj[key]
            if isinstance(val, list):
                list_val = self.encode_list(val)
                ret_list.append(f'{key}={list_val}')
            elif isinstance(val, dict):
                # call encode_object recursively
                dict_val = self.encode_object(val)
                ret_list.append(f'{key}={dict_val}')
            elif isinstance(val, bool):
                bool_val = str(val).lower()
                ret_list.append(f'{key}={bool_val}')
            else:
                general_val = str(val)
                ret_list.append(f'{key}={general_val}')

        sorted_list = sorted(ret_list)
        output = '&'.join(sorted_list)
        return output

    def get_signature(self, http_method, api_path, param_map):
        str_to_sign = api_path + '&' + self.encode_object(param_map)
        sig = hmac.new(self.secret_key.encode('utf-8'), str_to_sign.encode('utf-8'),
                       digestmod=hashlib.sha256).hexdigest()
        return sig

    def get_str(self, x):
        if isinstance(x, bool):
            return str(x).lower()
        else:
            return str(x)
                
    def call_private_api(self, path, method="GET", param_map=None):
        if param_map is None:
            param_map = {}

        nonce = self.get_nonce()
        param_map['timestamp'] = nonce

        sig = self.get_signature(
            http_method=method, api_path=path, param_map=param_map)
        param_map['signature'] = sig

        url = self.base_url + path

        js = None
        if method == HttpMethod.GET:
            query_string = '&'.join([f'{k}={self.get_str(v)}' for k, v in param_map.items()])
            url += '?' + query_string
        else:
            js = json.loads(json.dumps(param_map))
            js['timestamp'] = int(js['timestamp'])

        header = {'X-Bit-Access-Key': self.access_key, 'language-type': '1'}

        res = requests.request(method, url, headers=header, json=js)
        
        if self.verbose_log:
            print('')
            print('>>>>> Request:')
            print('--------------')
            if method == 'GET':
                print(f'curl -H "X-Bit-Access-Key: {self.access_key}" "{url}" ')
            else:
                print(
                    f"""curl -X "{method}" "{url}" -H "Content-Type: application/json" -H "X-Bit-Access-Key: {self.access_key}"  -d '{json.dumps(js)}' """)

            print('')                
            print('<<<<< Response:')
            print('--------------')
            print(res.status_code)
            print(res.text)
            print('')

        try:
            return res.json()
        except Exception as ex:
            print(
                f'Server returns non-json data: {res.text}, excpeiton = {str(ex)}')
            raise ex


    def ws_auth(self):
        return self.call_private_api(V1_WS_AUTH, HttpMethod.GET)
    
    def enable_cod(self, req):
        return self.call_private_api(V1_ACCOUNT_CONFIGS_COD, HttpMethod.POST, req)

    def query_cod(self, req={}):
        return self.call_private_api(V1_ACCOUNT_CONFIGS_COD, HttpMethod.GET, req)

    ######################
    # SPOT endpoints
    ######################
    def spot_account_configs(self, req):
        return self.call_private_api(V1_SPOT_ACCOUNT_CONFIGS, HttpMethod.GET, req)            

    def spot_query_accounts(self, params={}):
        return self.call_private_api(V1_SPOT_ACCOUNTS, HttpMethod.GET, params)

    def spot_query_transactions(self, params):
        return self.call_private_api(V1_SPOT_TRANSACTION_LOGS, HttpMethod.GET, params)

    def spot_query_orders(self, params):
        return self.call_private_api(V1_SPOT_ORDERS, HttpMethod.GET, params)

    def spot_query_open_orders(self, params):
        return self.call_private_api(V1_SPOT_OPENORDERS, HttpMethod.GET, params)

    def spot_query_trades(self, params):
        return self.call_private_api(V1_SPOT_USER_TRADES, HttpMethod.GET, params)

    def spot_place_order(self, order_req):
        return self.call_private_api(V1_SPOT_ORDERS, HttpMethod.POST, order_req)

    def spot_cancel_order(self, cancel_req):
        return self.call_private_api(V1_SPOT_CANCEL_ORDERS, HttpMethod.POST, cancel_req)

    def spot_amend_order(self, req):
        return self.call_private_api(V1_SPOT_AMEND_ORDERS, HttpMethod.POST, req)

    def spot_ws_auth(self):
        return self.call_private_api(V1_SPOT_WS_AUTH, HttpMethod.GET)

    def spot_new_batch_orders(self, req):
        return self.call_private_api(V1_SPOT_BATCH_ORDERS, HttpMethod.POST, req)

    def spot_amend_batch_orders(self, req):
        return self.call_private_api(V1_SPOT_AMEND_BATCH_ORDERS, HttpMethod.POST, req)

    def spot_query_mmp_state(self, req):
        return self.call_private_api(V1_SPOT_MMP_STATE, HttpMethod.GET, req)

    def spot_update_mmp_config(self, req):
        return self.call_private_api(V1_SPOT_MMP_UPDATE_CONFIG, HttpMethod.POST, req)

    def spot_reset_mmp(self, req):
        return self.call_private_api(V1_SPOT_RESET_MMP, HttpMethod.POST, req)

    def spot_enable_cod(self, req):
        return self.call_private_api(V1_SPOT_ACCOUNT_CONFIGS_COD, HttpMethod.POST, req)

    def spot_query_agg_trades(self, params):
        self.call_private_api(V1_SPOT_AGG_TRADES, HttpMethod.GET, params)

    ######################
    # UM endpoints
    ######################
    def um_query_account_mode(self):
        return self.call_private_api(V1_UM_ACCOUNT_MODE, HttpMethod.GET)

    def um_query_accounts(self):
        return self.call_private_api(V1_UM_ACCOUNTS, HttpMethod.GET)

    def um_query_transactions(self, param):
        return self.call_private_api(V1_UM_TRANSACTIONS, HttpMethod.GET, param)

    def um_query_interest_records(self, param):
        return self.call_private_api(V1_UM_INTEREST_RECORDS, HttpMethod.GET, param)

    ######################
    # USD-M endpoints
    ######################
    def linear_account_configs(self, req):
        return self.call_private_api(V1_LINEAR_ACCOUNT_CONFIGS, HttpMethod.GET, req)            

    def linear_query_positions(self, params):
        return self.call_private_api(V1_LINEAR_POSITIONS, HttpMethod.GET, params)

    def linear_query_orders(self, params):
        return self.call_private_api(V1_LINEAR_ORDERS, HttpMethod.GET, params)

    def linear_query_open_orders(self, params):
        return self.call_private_api(V1_LINEAR_OPENORDERS, HttpMethod.GET, params)

    def linear_query_trades(self, params):
        return self.call_private_api(V1_LINEAR_USER_TRADES, HttpMethod.GET, params)

    def linear_place_order(self, order_req):
        return self.call_private_api(V1_LINEAR_ORDERS, HttpMethod.POST, order_req)

    def linear_cancel_order(self, cancel_req):
        return self.call_private_api(V1_LINEAR_CANCEL_ORDERS, HttpMethod.POST, cancel_req)

    def linear_amend_order(self, req):
        return self.call_private_api(V1_LINEAR_AMEND_ORDERS, HttpMethod.POST, req)

    def linear_new_batch(self, req):
        return self.call_private_api(V1_LINEAR_BATCH_ORDERS, HttpMethod.POST, req)

    def linear_amend_batch(self, req):
        return self.call_private_api(V1_LINEAR_AMEND_BATCH_ORDERS, HttpMethod.POST, req)

    def linear_close_position(self, req):
        return self.call_private_api(V1_LINEAR_CLOSE_POS, HttpMethod.POST, req)

    def linear_estimated_margins(self, req):
        return self.call_private_api(V1_LINEAR_EST_MARGINS, HttpMethod.GET, req)

    def linear_query_leverage_ratio(self, params):
        return self.call_private_api(V1_LINEAR_LEVERAGE_RATIO, HttpMethod.GET, params)

    def linear_update_leverage_ratio(self, params):
        return self.call_private_api(V1_LINEAR_LEVERAGE_RATIO, HttpMethod.POST, params)

    # usdx blocktrades
    def linear_new_blocktrades(self, order_req):
        return self.call_private_api(V1_LINEAR_BLOCK_TRADES, HttpMethod.POST, order_req)

    def linear_query_blocktrades(self, req):
        return self.call_private_api(V1_LINEAR_BLOCK_TRADES, HttpMethod.GET, req)

    def linear_query_userinfo(self, req={}):
        return self.call_private_api(V1_LINEAR_USER_INFO, HttpMethod.GET, req)

    def linear_query_platform_blocktrades(self, req):
        return self.call_private_api(V1_LINEAR_PLATFORM_BLOCK_TRADES, HttpMethod.GET, req)

    def linear_cond_orders(self, req):
        self.call_private_api('/linear/v1/conditional_orders', 'GET', req)            

    # agg
    def linear_query_agg_positions(self, params):
        self.call_private_api(V1_LINEAR_AGG_POSITIONS, HttpMethod.GET, params)

    def linear_query_agg_trades(self, params):
        self.call_private_api(V1_LINEAR_AGG_TRADES, HttpMethod.GET, params)


    def linear_tpsl_new(self, params):
        self.call_private_api('/linear/v1/tpsl/new', 'POST', params)

    def linear_tpsl_edit(self, params):
        self.call_private_api('/linear/v1/tpsl/edit', 'POST', params)

    def linear_tpsl_cancel(self, params):
        self.call_private_api('/linear/v1/tpsl/cancel', 'POST', params)

    def linear_tpsl_list(self, params):
        self.call_private_api('/linear/v1/tpsl/list', 'GET', params)
        
if __name__ == '__main__':
    # api_host = "https://api.bit.com" # production

    api_host = "https://betaapi.bitexch.dev" # testnet

    # access-key and private-key read from env
    ak = os.getenv('BITCOM_AK')
    sk = os.getenv('BITCOM_SK')

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
