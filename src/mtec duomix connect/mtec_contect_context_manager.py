# SPDX-License-Identifier: GPL-3.0-or-later
# This file is part of Python-OPC-UA.
# Project: https://github.com/3DCP-TUe/Python-OPC-UA
#
# Copyright (c) 2024-2025 3D Concrete Printing Research Group at Eindhoven University of Technology
#
# Authors:
#   - Arjen Deetman (2024-2025)
#
# For license details, see the LICENSE file in the project root.

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
