# TODO:
# - Impl ws 
import websockets
import yarl

class Node:
    def __init__(self, *, url: yarl.URL, password, client)
        self.client = client 
        self.password = password
        
        self.url = url
        
        self.ws = None
        self.ws_task = None # task with ws reading stuff
        self.closed = True

    @property
    def is_closed(self):
        return self.closed

    async def connect(self):
        """
        TODO: 
         - Open ws connection
         - Set closed to false
        """

        raise NotImplementedError()

    async def task(self):
        while not self.is_closed:
            try:
                payload = await self.ws.recv()

            except websockets.ConnectionClosed:
                raise RuntimeError() # Replace this with better exception and do cleanup

            print(payload)

        
   async def get_tracks(self, search: str):
       raise NotImplementedError()
