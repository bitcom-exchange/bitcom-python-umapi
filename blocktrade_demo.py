import time
from bit_py_umapi import *
import uuid

api_host = "https://betaapi.bitexch.dev"


bt_source = '<input_source>' # input bt_source

user_1 = {
    'user_id': 437348,
    'ak': '', # input user_1 api-key
    'sk': '' # input user_1 secret-key
}

user_2 = {
    'user_id': 473683,
    'ak': '', # input user_2 api-key
    'sk': ''  # input user_2 secret-key
}

def get_bt_req(source, label, counter_party, flag):
    req = {
        'currency': 'USD',
        'label': label,
        'role': 'maker' if flag else 'taker',
        'counterparty': counter_party,
        'bt_source': source,
        'trades': [
            # {
            #     'instrument_id': 'BTC-25SEP20-9000-C',
            #     'price': '0.35',
            #     'qty': '25',
            #     'side': ('sell' if flag else 'buy')
            # },
            {
                'instrument_id': 'BTC-USD-PERPETUAL',
                'price': '22800',
                'qty': '10',
                'side': ('buy' if flag else 'sell')
            }
        ]
    }
    return req


def get_label_timestamp():
    return 'bt-' + str(int(time.time() * 1000))


def get_label_uuid():
    return uuid.uuid4().hex


def new_block_trade_test():
    client_1 = BitClient(user_1['ak'], user_1['sk'], api_host)
    client_2 = BitClient(user_2['ak'], user_2['sk'], api_host)

    label = get_label_uuid()
    side_flag = True

    print('executing block trade, label = ' + label)
    print(client_1.linear_new_blocktrades(get_bt_req(bt_source, label, user_2['user_id'], side_flag)))

    time.sleep(1)
    print(client_2.linear_new_blocktrades(get_bt_req(bt_source, label, user_1['user_id'], not side_flag)))


def query_blocktrades_test():
    client_1 = BitClient(user_1['ak'], user_1['sk'], api_host)
    client_1.linear_query_blocktrades({'currency': 'USD', 'bt_source': bt_source})



if __name__ == "__main__":
    new_block_trade_test()
