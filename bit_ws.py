# python3 -m pip install websocket-client
import websocket, _thread, time, json

ws_host = "wss://ws.bit.com"

subscribe_req = {
    "type": "subscribe",
    "channels": ["order_book.10.10"],
    "instruments": ["BTC-USD-PERPETUAL"],
    "interval": "100ms",
}

###########################################################


def ws_message(ws, message):
    print(f"ws_message: {message}")


def ws_open(ws):
    print("ws_open: send req " + str(subscribe_req))
    ws.send(json.dumps(subscribe_req))


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