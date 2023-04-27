from asyncio import Queue, create_task, wait, FIRST_COMPLETED
from websockets import connect
from Setup import HOST, PORT
from json import dumps, loads

class Client:

    def __init__(self):
        self._uri = f"ws://{HOST}:{PORT}"
        self._txq = Queue()
        self._rxq = Queue()

    def quit(self):
        self._running = False
        self._txq.put_nowait(dumps("Stop"))
        self._rxq.put_nowait(dumps("Stop"))

    async def send(self,message):
        await self._txq.put(dumps(message))

    async def recv(self):
        message = await self._rxq.get()
        return loads(message)

    @property
    def can_recv(self):
        return not self._rxq.empty()

    async def _consumer_handler(self,websocket):
        while self._running:
            message = await websocket.recv()
            await self._rxq.put(message)

    async def _producer_handler(self,websocket):
        while self._running:
            message = await self._txq.get()
            await websocket.send(message)

    async def run(self):
        self._running = True
        async with connect(self._uri) as websocket:
            _, pending = await wait(
                [
                    create_task(self._consumer_handler(websocket)),
                    create_task(self._producer_handler(websocket))
                ],
                return_when=FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
