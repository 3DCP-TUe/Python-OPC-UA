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
from asyncua import Client, ua

async def main():
    
    while True:
        
        client = Client(url="opc.tcp://10.129.4.80:48010")
        
        try:
            async with client:

                node_mixer_run = client.get_node("ns=2;s=Tags.GECO/MP_Mixer_Run")
                mass_flow_handler = MassFlowHandler()
                sub_mixer_run = await client.create_subscription(100, mass_flow_handler)
                await sub_mixer_run.subscribe_data_change(node_mixer_run)

                while True:
                    await asyncio.sleep(1)
                    await client.check_connection()  # Throws an exception if the connection is lost
        
        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: %s", e)
        
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


class MassFlowHandler:

    """
    Subscription Handler. To receive events from the server for a subscription.
    """
    
    def __init__(self):

        """Initializes the event handler."""

        self.start_time = datetime.now() # Start time of batch
        self.stop_time = datetime.now() # End time of batch
        self.stop_time_last = datetime.now() # End time of last batch
        self.interval_times = {} # Time between the end of two batches
        self.batch_times = {} # Time between start of batch and end of batch
        self.predictions = {} # Mass flow rate prediction
        self.dosing_flow_rate = 33.0 # Flow rate of mixer continous running

    async def datachange_notification(self, node, val, data):
        
        """
        Called for every data change notification from the server.
        """
        
        time = datetime.now()

        if val:
            logging.info("Mixer started.")
            self.start_time = time
                    
        else:
            logging.info("Mixer stopped.")
            
            self.stop_time_last = self.stop_time
            self.stop_time = time

            batch_time = (self.stop_time - self.start_time).total_seconds()
            interval_time = (self.stop_time - self.stop_time_last).total_seconds()
            prediction = self.dosing_flow_rate * (batch_time / interval_time)
            
            self.batch_times[time] = batch_time
            self.interval_times[time] = interval_time
            self.predictions[time] = prediction

            logging.info("Batch duration [s]            : {0:.2f}".format(batch_time))
            logging.info("Interval time [s]             : {0:.2f}".format(interval_time))
            logging.info("Predicted mass flow rate      : {0:.5f}".format(prediction))
            
            # Mean of last x values
            values = list(self.predictions.values())
            sizes = [2, 4, 8, 16, 32]

            for size in sizes:
                sliced_values = values[-size:] if len(values) > size else values
                mean = sum(sliced_values) / len(sliced_values)
                logging.info("Mean predicted value k={0:<2}     : {1:.5f}".format(size, mean))

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