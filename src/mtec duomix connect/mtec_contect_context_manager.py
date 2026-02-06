"""
This file is part of the Python OPC UA examples of Eindhoven University of Technology. 
The files of this project are licensed under the terms of GNU General Public License 
version 3.0 (GPL v3.0) as published by the Free Software Foundation. For more information 
and the LICENSE file, see <https://github.com/3DCP-TUe/Python-OPC-UA>.
"""

import asyncio
import logging
from asyncua import Client

class MixerPump:
    
    def __init__(self) -> None:
        self.client = Client("opc.tcp://10.129.4.73:4840")

    async def __aenter__(self):
        await self.client.connect()

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.disconnect()


async def coroutine():
    
    mixer_pump = MixerPump()
    async with mixer_pump:
        print("Within the context manager.")
    

if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(coroutine())
