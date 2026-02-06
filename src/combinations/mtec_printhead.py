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
from asyncua import Client, ua

DELTA_TIME = 10 # Minutes
MTEC_RPMS = [180, 180, 180, 180, 180, 180, 300, 300, 300, 300, 300, 300, 180, 180, 180, 180, 180, 180, 300, 300, 300, 300, 300, 300, 180]
PRINTHEAD_RPMS = [51, 450, 150, 50, 300, 600, 51, 450, 50, 300, 600, 150, 51, 150, 300, 50, 450, 600, 51, 600, 50, 300, 450, 150, 51]

async def main():
  
    while True:
        
        # Data check
        if (len(PRINTHEAD_RPMS) != len(MTEC_RPMS)):
            logging.error("List lenghts are not equal.")
            break
        
        n = len(PRINTHEAD_RPMS)
        mtec = Client(url="opc.tcp://10.129.4.73:4840")
        printhead = Client(url="opc.tcp://10.129.4.20:4840")

        try:
            async with mtec, printhead:
                
                counter = 0
                
                logging.info("Get nodes")
                node_printhead_rpm = printhead.get_node("ns=3;s=\"Velocity_Jog_left\"")
                node_mtec_rpm =  mtec.get_node("ns=4;s=|var|ECC2100 0.8S 1131.Application.GVL_OPC.set_value_mixingpump")
                
                logging.info("Start")
                
                while True: 
                    
                    # Get values
                    printhead_rpm = PRINTHEAD_RPMS[counter]
                    mtec_rpm = int((MTEC_RPMS[counter]-169.2)*65000.0/(420.0-169.2))

                    # Log
                    logging.info("Settings: {}, {}, {}, {}, {}".format(counter, n, printhead_rpm, MTEC_RPMS[counter], mtec_rpm))

                    # Write values
                    value1 = ua.DataValue(ua.Variant(printhead_rpm, ua.VariantType.Double))
                    value2 = ua.DataValue(ua.Variant(mtec_rpm, ua.VariantType.UInt16))

                    await node_printhead_rpm.write_value(value1)
                    await node_mtec_rpm.write_value(value2)

                    # Wait
                    await asyncio.sleep(DELTA_TIME*60)
                    
                    # Increase counter
                    counter = counter + 1

                    # Check connections
                    await mtec.check_connection()
                    await printhead.check_connection()

        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())