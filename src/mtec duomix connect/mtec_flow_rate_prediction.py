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
        
        client = Client(url="opc.tcp://10.129.4.73:4840")

        try:
            async with client:

                # Live bit handler
                livebit2duomix = client.get_node("ns=4;s=|var|ECC2100 0.8S 1131.Application.GVL_OPC.Livebit2DuoMix")
                live_bit_handler = LivebitHandler(livebit2duomix)
                livebit2extern = client.get_node("ns=4;s=|var|ECC2100 0.8S 1131.Application.GVL_OPC.Livebit2extern")
                sub_live_bit = await client.create_subscription(1000, live_bit_handler)
                await sub_live_bit.subscribe_data_change(livebit2extern)
                
                # Prediction of mass flow rate
                sub_handler_flow = SubHandlerFlow() 
                node_flow = client.get_node("ns=4;s=|var|ECC2100 0.8S 1131.Application.GVL_OPC.aut_solenoid_valve")
                sub_flow = await client.create_subscription(10, sub_handler_flow)
                await sub_flow.subscribe_data_change(node_flow)

                while True:
                    await asyncio.sleep(1)
                    await client.check_connection()  # Throws a exception if connection is lost
        
        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


# Toggle Livebit by subscription
class LivebitHandler:

    """
    Subscription Handler. To receive events from server for a subscription.
    """
    
    def __init__(self, livebit2duomix):

        """Initializes the event handler."""
    
        self.livebit2duomix = livebit2duomix

    async def datachange_notification(self, node: Node, value, data):
        await self.livebit2duomix.set_value(ua.Variant(value, ua.VariantType.Boolean))

    def event_notification(self, event: ua.EventNotificationList):
        
        """
        Called for every event notification from server
        """

        pass

    def status_change_notification(self, status: ua.StatusChangeNotification):
        
        """
        Called for every status change notification from server.
        """

        pass 


class SubHandlerFlow:

    """
    Subscription Handler. To receive events from server for a subscription.
    """

    def __init__(self):

        """Initializes the event handler."""

        self.last_batch_start = datetime.now()
        self.last_batch_end = datetime.now()
        self.dict_batch_duration = {}
        self.dict_batch_interval = {}
        self.dict_pred_mass_flow = {}
        self.counter = 0

    def datachange_notification(self, node: Node, val, data):
        
        """
        Called for every datachange notification from server.
        """
        
        time = datetime.now()

        # Dosing switched on
        if (val == True):
            logging.info("Mixer started.")
            self.last_batch_start = time

        # Dosing switched off
        else:
            logging.info("Mixer stopped.")

            # Calculate values
            duration = (time - self.last_batch_start).total_seconds()
            interval = (time - self.last_batch_end).total_seconds()
            pred = 27.0 * (float(duration) / interval)

            # Set values
            self.dict_batch_duration[time] = duration
            self.dict_batch_interval[time] = interval
            self.dict_pred_mass_flow[time] = pred
            self.last_batch_end = time
            
            # Get all values from dictionary
            values = list(self.dict_pred_mass_flow.values())
            
            values60 = values
            values40 = values
            values20 = values
            values10 = values

            if (len(values) > 60):
                values60 = values[-60:]
            if (len(values) > 40):
                values40 = values[-40:]
            if (len(values) > 20):
                values20 = values[-20:]
            if (len(values) > 10):
                values10 = values[-10:]
                
            mean10 = sum(values10) / len(values10)
            mean20 = sum(values20) / len(values20)
            mean40 = sum(values40) / len(values40)
            mean60 = sum(values60) / len(values60)

            self.counter += 1

            logging.info("Counter [-]                               : {}".format(self.counter))
            logging.info("Batch interval [sec]                      : {0:.2f}".format(interval))
            logging.info("Batch duration [sec]                      : {0:.2f}".format(duration))
            logging.info("Predicted flow (actual) [kg/min]          : {0:.1f}".format(pred))
            logging.info("Predicted flow (movmean 10) [kg/min]      : {0:.1f}".format(mean10))
            logging.info("Predicted flow (movmean 20) [kg/min]      : {0:.1f}".format(mean20))
            logging.info("Predicted flow (movmean 40) [kg/min]      : {0:.1f}".format(mean40))
            logging.info("Predicted flow (movmean 60) [kg/min]      : {0:.1f}\n".format(mean60))

    def event_notification(self, event: ua.EventNotificationList):
        
        """
        Called for every event notification from server
        """
        pass

    def status_change_notification(self, status: ua.StatusChangeNotification):
        
        """
        Called for every status change notification from server.
        """
        pass 


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())