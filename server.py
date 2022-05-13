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
        ws.send(message)
        ws.recv()


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connected.')

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnected.')

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        except Exception as e:
            logging.warning(f'ws handler: {e}')
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        data = await ws.recv()
        print(data)

        async for message in ws:
            await self.send_to_clients(message)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    host, port = 'localhost', 4000

    server = Server()
    start_server = websockets.serve(server.ws_handler, host, port)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()