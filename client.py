import asyncio
import logging
import websockets
from websockets.legacy.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)


async def consumer_handler(websocket: websockets.WebSocketClientProtocol) -> None:
    async for message in websocket:
        logging.info(f'Message: {message}')


async def consume(host: str, port: int) -> None:
    ws_url = f'ws://{host}:{port}'
    async with websockets.connect(ws_url) as websocket:
        await consumer_handler(websocket)


async def produce(message: str, host: str, port: int) -> None:
    ws_url = f'ws://{host}:{port}'
    async with websockets.connect(ws_url) as ws:
        res = await ws.send(message)
        res2 = await ws.recv()
        print(res, res2)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    host, port = 'localhost', 4000

    asyncio.run(produce('test run', host, port))
