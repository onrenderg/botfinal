import asyncio
import websockets
import json
import time

async def serve_quotes(websocket, path):
    while True:
        quote = generate_quote()
        await websocket.send(json.dumps(quote))
        await asyncio.sleep(1)  # Adjust this to control the frequency of updates

def generate_quote():
    timestamp = int(time.time())
    quote_data = {
        "e": "kline",
        "E": timestamp,
        "s": "BTCUSDT",
        "k": {
            "t": timestamp,
            "T": timestamp + 59999,
            "s": "BTCUSDT",
            "i": "1m",
            "f": 3522977662,
            "L": 3522977698,
            "o": "69882.01000000",
            "c": "69882.01000000",
            "h": "69882.01000000",
            "l": "69882.00000000",
            "v": "0.13567000",
            "n": 37,
            "x": False,
            "q": "9480.89124840",
            "V": "0.03084000",
            "Q": "2155.16118840",
            "B": "0"
        }
    }
    return quote_data

start_server = websockets.serve(serve_quotes, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


