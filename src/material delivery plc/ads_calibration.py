"""
This file is part of the Python OPC UA examples of Eindhoven University of Technology. 
The files of this project are licensed under the terms of GNU General Public License 
version 3.0 (GPL v3.0) as published by the Free Software Foundation. For more information 
and the LICENSE file, see <https://github.com/3DCP-TUe/Python-OPC-UA>.
"""

import asyncio
import logging
from asyncua import Client, ua

async def main():
  
    while True:
        
        client = Client(url="opc.tcp://10.129.4.30:4840")

        try:
            async with client:               

                node_do0 = client.get_node("ns=4;i=22") # Start/stop
                node_ao0 = client.get_node("ns=4;i=78") # Speed

                while True:
                    
                    val1 = input("Enter speed [mA]: ")
                    val2 = input("Enter time [s]: ")
                    
                    await node_ao0.write_value(ua.DataValue(ua.Variant(float(val1), ua.VariantType.Float)))
                    await asyncio.sleep(1)
                    await node_do0.write_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                    
                    await asyncio.sleep(float(val2))
                    
                    await node_do0.write_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                    
                    await asyncio.sleep(1)
                    await client.check_connection()  # Throws a exception if connection is lost
        
        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())