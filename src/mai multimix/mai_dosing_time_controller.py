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

# CONSTANT: GLOBAL PARAMETERS
BATCH_TIME = 5  # [FLOAT: seconds]
MIN_PAUSE = 20 # [FLOAT: seconds]
DELAY_WETPROBE_UNCOVERED = 2 # [INT: seconds], limits 2-120 seconds
DELAY_WETPROBE_COVERED = 10 # [INT: seconds], limits 2-20 seconds

# CONSTANT: DO NOT CHANGE!
DATA_VALUE_TRUE = ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
DATA_VALUE_FALSE = ua.DataValue(ua.Variant(False, ua.VariantType.Boolean))

async def main():
    
    while True:
        
        client = Client(url="opc.tcp://10.129.4.80:48010")
        
        try:
            async with client:
            
                # Set settings
                node_wetprobe_covered = client.get_node("ns=2;s=Tags.GECO/MPRX_DI_Wetprobe_Upper_Cov_Delay_s_I")
                node_wetprobe_uncovered = client.get_node("ns=2;s=Tags.GECO/MPRX_DI_Wetprobe_Upper_NCov_Delay_s_I")         
                await node_wetprobe_covered.set_data_value(ua.DataValue(ua.Variant(DELAY_WETPROBE_COVERED, ua.VariantType.Int16)))
                await node_wetprobe_uncovered.set_data_value(ua.DataValue(ua.Variant(DELAY_WETPROBE_UNCOVERED, ua.VariantType.Int16)))

                # Mixer nodes and interval handler
                node_mixer_disabled = client.get_node("ns=2;s=Tags.GECO/MPRX_DI_Mixer_Disabled")
                node_mixer_run = client.get_node("ns=2;s=Tags.GECO/MP_Mixer_Run")
                dosing_time_handler = DosingTimeHandler(node_mixer_disabled)
                sub_mixer_run = await client.create_subscription(100, dosing_time_handler)
                await sub_mixer_run.subscribe_data_change(node_mixer_run)

                while True:
                    await asyncio.sleep(1)
                    await client.check_connection()  # Throws an exception if the connection is lost
        
        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: %s", e)
        
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


class DosingTimeHandler:

    """
    Subscription Handler. To receive events from the server for a subscription.
    """
    
    def __init__(self, node_mixer_disabled : Node):

        """Initializes the event handler."""

        self.node_mixer_disabled = node_mixer_disabled
        self.start_time = datetime.now() # Start time of batch
        self.stop_time = datetime.now() # End time of batch
        self.stop_time_last = datetime.now() # End time of last batch
        self.interval_times = [] # Time between the end of two batches
        self.batch_times = [] # Time between start of batch and end of batch
        self.predictions = [] # Mass flow rate prediction
        self.dosing_flow_rate = 33.0 # Flow rate of mixer continous running

    async def datachange_notification(self, node, val, data):
        
        """
        Called for every data change notification from the server.
        """
        
        time = datetime.now()

        if val:
            logging.info("Mixer started.")
            self.start_time = time

            await asyncio.sleep(BATCH_TIME)
            await self.node_mixer_disabled.set_data_value(DATA_VALUE_TRUE)
        
        else:
            logging.info("Mixer stopped.")
            
            self.stop_time_last = self.stop_time
            self.stop_time = time

            batch_time = (self.stop_time - self.start_time).total_seconds()
            interval_time = (self.stop_time - self.stop_time_last).total_seconds()
            prediction = self.dosing_flow_rate * (batch_time / interval_time)
            
            self.batch_times.append(batch_time)
            self.interval_times.append(interval_time)
            self.predictions.append(prediction)
            
            logging.info("Batch duration [s]            : {0:.2f}".format(batch_time))
            logging.info("Interval time [s]             : {0:.2f}".format(interval_time))
            logging.info("Predicted mass flow rate      : {0:.5f}\n".format(prediction))
            
            await asyncio.sleep(MIN_PAUSE)
            await self.node_mixer_disabled.set_data_value(DATA_VALUE_FALSE)

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