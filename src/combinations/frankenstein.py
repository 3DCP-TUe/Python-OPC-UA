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
from datetime import datetime
from asyncua import Client, Node, ua

async def main():
  
    while True:
        
        mtec_client = Client(url="opc.tcp://10.129.4.73:4840")
        material_client = Client(url="opc.tcp://10.129.4.30:4840")
        vertico_client = Client(url="opc.tcp://10.129.4.40:4840")

        try:
            async with mtec_client, vertico_client, material_client:
                               
                node_mtec = mtec_client.get_node("ns=4;s=|var|ECC2100 0.8S 1131.Application.GVL_OPC.aut_mixer") #UInt16
                node_material = material_client.get_node("ns=4;i=22") #DO1, Boolean
                node_vertico = vertico_client.get_node("ns=5;i=2") # DO3, Boolean
                sync_handler = SyncHandler(node_material, node_vertico)

                sub = await mtec_client.create_subscription(100, sync_handler)
                await sub.subscribe_data_change(node_mtec)
                
                logging.info("Start")
                
                while True: 
                    
                    # Wait
                    await asyncio.sleep(1.0)
                    
                    # Check connections
                    await mtec_client.check_connection()
                    await material_client.check_connection()
                    await vertico_client.check_connection()

        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)

class SyncHandler:

    """
    Subscription Handler. To receive events from the server for a subscription.
    """
    
    def __init__(self, node_material : Node, node_vertico : Node):

        """Initializes the event handler."""

        self.node_material = node_material
        self.node_vertico = node_vertico
        self.last_batch_start = datetime.now()
        self.last_batch_end = datetime.now()
        self.dict_batch_duration = {}
        self.dict_batch_interval = {}
        self.dict_pred_mass_flow = {}

    async def datachange_notification(self, node, val, data):
        
        """
        Called for every data change notification from the server.
        """

        # Changes values of other systems
        await self.node_material.write_value(val)
        await self.node_vertico.write_value(val)

        time = datetime.now()

        # Mixer switched on
        if (val == True):
            logging.info("Mixer started.")
            self.last_batch_start = time

        # Mixer switched off
        else:
            logging.info("Mixer stopped.")

            # Calculate values
            duration = (time - self.last_batch_start).total_seconds()
            interval = (time - self.last_batch_end).total_seconds()

            # Set values
            self.dict_batch_duration[time] = duration
            self.dict_batch_interval[time] = interval
            self.last_batch_end = time

            logging.info("Batch interval [sec]  : {0:.2f}".format(interval))
            logging.info("Batch duration [sec]  : {0:.2f}\n".format(duration))


    def event_notification(self, event):
        
        """
        Called for every event notification from the server.
        """
        
        pass

    def status_change_notification(self, status):
        
        """
        Called for every status change notification from the server.
        """
        
        pass


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())