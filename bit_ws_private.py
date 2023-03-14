import websocket, _thread, time, json
from bit_py_umapi import BitClient

# ws_host = "wss://ws.bit.com"
ws_host = "wss://betaws.bitexch.dev"
# ws_host = "wss://alphaws.bitexch.dev"
# ws_host = "wss://spot-ws.bit.com"

api_host = "https://betaapi.bitexch.dev"
ak = ""
sk = ""

###########################################################


def get_ws_token():
    restClient = BitClient(ak, sk, api_host)
    ret = restClient.ws_auth()
    obj = json.loads(ret)
    return obj["data"]["token"]


def make_user_trade_req(token):
    return {
        "type": "subscribe",
        "channels": ["user_trade"],
        "currencies": ["BTC"],
        "categories": ["future", "option"],
        "interval": "raw",
        "token": token,
    }


def make_user_order_req(token):
    return {
        "type": "subscribe",
        "channels": ["order"],
        "pairs": ["BTC-USD", "ETH-USD"],
        "categories": ["future", "option"],
        "interval": "raw",
        "token": token,
    }


def make_umaccount_req(token):
    return {
        "type": "subscribe",
        "channels": ["um_account"],
        "interval": "100ms",
        "token": token,
    }


###########################################################


def ws_message(ws, message):
    print(f"ws_message: {message}")


def ws_open(ws):
    print("getting ws_token")
    ws_token = get_ws_token()
    # req = make_umaccount_req(ws_token)
    req = make_user_order_req(ws_token)
    print("ws_open: send req " + str(req))
    ws.send(json.dumps(req))


def ws_error(ws, evt):
    print(f"ws_error: event:{str(evt)}")


def ws_close(ws, status_code, msg):
    print(f"ws_close " + " status = " + str(status_code) + " msg = " + str(msg))


def ws_thread(*args):
    print(f"Connecting to {ws_host}...")
    ws = websocket.WebSocketApp(
        ws_host,
        on_open=ws_open,
        on_message=ws_message,
        on_error=ws_error,
        on_close=ws_close,
    )
    ws.run_forever()


_thread.start_new_thread(ws_thread, ())

while True:
    time.sleep(5)
    print("Main thread")
