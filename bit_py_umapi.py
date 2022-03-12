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

class HttpMethod:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'


# COIN-M
V1_ACCOUNTS = '/v1/accounts'
V1_POSITIONS = '/v1/positions'
V1_ORDERS = '/v1/orders'
V1_CANCEL_ORDERS = '/v1/cancel_orders'
V1_OPENORDERS = '/v1/open_orders'
V1_USER_TRADES = '/v1/user/trades'
V1_STOP_ORDERS = '/v1/stop_orders'
V1_AMEND_ORDERS = '/v1/amend_orders'
V1_TRANSACTION_LOGS = '/v1/transactions'
V1_DELIVERIES = '/v1/user/deliveries'
V1_SETTLEMENTS = '/v1/user/settlements'
V1_DELIVERY_INFO = '/v1/delivery_info'
V1_EST_MARGINS = '/v1/margins'
V1_CLOSE_POS = '/v1/close_positions'
V1_WS_AUTH = '/v1/ws/auth'
V1_BLOCK_TRADES = '/v1/blocktrades'
V1_PLATFORM_BLOCK_TRADES = '/v1/platform_blocktrades'
V1_BATCH_ORDERS = '/v1/batchorders'
V1_AMEND_BATCH_ORDERS = '/v1/amend_batchorders'
V1_MMP_STATE = "/v1/mmp_state"
V1_MMP_UPDATE_CONFIG = "/v1/update_mmp_config"
V1_RESET_MMP = "/v1/reset_mmp"
V1_USER_INFO = "/v1/user/info"
V1_ORDERS_MARGIN = "/v1/orders/margin"
V1_ACCOUNT_CONFIGS_COD = "/v1/account_configs/cod"


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

class BitClient(object):

    def __init__(self, ak, sk, base_url):
        self.access_key = ak
        self.secret_key = sk
        self.base_url = base_url

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
            print(list_val)
        # list_val = sorted(list_val)
        output = '&'.join(list_val)
        output = '[' + output + ']'
        return output

    def encode_object(self, param_map):
        sorted_keys = sorted(param_map.keys())
        ret_list = []
        for key in sorted_keys:
            val = param_map[key]
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
            query_string = '&'.join([f'{k}={v}' for k, v in param_map.items()])
            url += '?' + query_string
        else:
            js = json.loads(json.dumps(param_map))
            js['timestamp'] = int(js['timestamp'])

        header = {'X-Bit-Access-Key': self.access_key, 'language-type': '1'}

        res = requests.request(method, url, headers=header, json=js)
        try:
            return res.json()
        except Exception as ex:
            print(
                f'Server returns non-json data: {res.text}, excpeiton = {str(ex)}')
            raise ex

    ######################
    # COIN-M endpoints
    ######################
    def query_accounts(self, params={}):
        return self.call_private_api(V1_ACCOUNTS, HttpMethod.GET, params)

    def query_positions(self, params):
        return self.call_private_api(V1_POSITIONS, HttpMethod.GET, params)

    def query_transactions(self, params):
        return self.call_private_api(V1_TRANSACTION_LOGS, HttpMethod.GET, params)

    def query_deliveries(self, params):
        return self.call_private_api(V1_DELIVERIES, HttpMethod.GET, params)

    def query_settlements(self, params):
        return self.call_private_api(V1_SETTLEMENTS, HttpMethod.GET, params)

    def query_orders(self, params):
        return self.call_private_api(V1_ORDERS, HttpMethod.GET, params)

    def query_open_orders(self, params):
        return self.call_private_api(V1_OPENORDERS, HttpMethod.GET, params)

    def get_est_margin(self, params):
        return self.call_private_api(V1_EST_MARGINS, HttpMethod.GET, params)

    def query_stop_orders(self, params):
        return self.call_private_api(V1_STOP_ORDERS, HttpMethod.GET, params)

    def query_trades(self, params):
        return self.call_private_api(V1_USER_TRADES, HttpMethod.GET, params)

    def place_order(self, order_req):
        return self.call_private_api(V1_ORDERS, HttpMethod.POST, order_req)

    def cancel_order(self, cancel_req):
        return self.call_private_api(V1_CANCEL_ORDERS, HttpMethod.POST, cancel_req)

    def amend_order(self, req):
        return self.call_private_api(V1_AMEND_ORDERS, HttpMethod.POST, req)

    def close_position(self, close_req):
        return self.call_private_api(V1_CLOSE_POS, HttpMethod.POST, close_req)

    def ws_auth(self):
        return self.call_private_api(V1_WS_AUTH, HttpMethod.GET)

    def new_blocktrades(self, order_req):
        return self.call_private_api(V1_BLOCK_TRADES, HttpMethod.POST, order_req)

    def query_blocktrades(self, req):
        return self.call_private_api(V1_BLOCK_TRADES, HttpMethod.GET, req)

    def query_userinfo(self):
        return self.call_private_api(V1_USER_INFO, HttpMethod.GET, {})

    def query_platform_blocktrades(self, req):
        return self.call_private_api(V1_PLATFORM_BLOCK_TRADES, HttpMethod.GET, req)

    def new_batch_orders(self, req):
        return self.call_private_api(V1_BATCH_ORDERS, HttpMethod.POST, req)

    def amend_batch_orders(self, req):
        return self.call_private_api(V1_AMEND_BATCH_ORDERS, HttpMethod.POST, req)

    def query_mmp_state(self, req):
        return self.call_private_api(V1_MMP_STATE, HttpMethod.GET, req)

    def update_mmp_config(self, req):
        return self.call_private_api(V1_MMP_UPDATE_CONFIG, HttpMethod.POST, req)

    def reset_mmp(self, req):
        return self.call_private_api(V1_RESET_MMP, HttpMethod.POST, req)

    def enable_cod(self, req):
        return self.call_private_api(V1_ACCOUNT_CONFIGS_COD, HttpMethod.POST, req)

    ######################
    # SPOT endpoints
    ######################
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
    # USDT-M endpoints
    ######################
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
        classic_account_btc = client.query_accounts({'currency':'BTC'})
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