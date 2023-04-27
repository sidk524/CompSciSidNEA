from asyncio import get_event_loop, wait, FIRST_COMPLETED, Queue, create_task, run
from websockets import serve
from Setup import HOST, PORT

class Server:

    def __init__(self):
        self._connected = set()
        self._msgq = Queue()

    async def _consumer_handler(self,websocket):
        async for message in websocket:
            await self._msgq.put(message)

    async def _producer_handler(self):
        while True:
            message = await self._msgq.get()
            if self._connected:
                await wait([create_task(ws.send(message)) for ws in self._connected])

    async def _server(self,websocket, path):
        # Register.
        self._connected.add(websocket)
        try:
            # Implement logic here.
            _, pending = await wait(
                [
                    create_task(self._consumer_handler(websocket)),
                    create_task(self._producer_handler())
                ],
                return_when=FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        finally:
            # Unregister.
            self._connected.remove(websocket)

    def run(self):
        loop = get_event_loop()
        server_task = serve(self._server, HOST, PORT)
        loop.run_until_complete(server_task)
        loop.run_forever()

if __name__ == "__main__":
    server = Server()
    server.run()
