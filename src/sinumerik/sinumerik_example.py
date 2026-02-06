"""
This file is part of the Python OPC UA examples of Eindhoven University of Technology. 
The files of this project are licensed under the terms of GNU General Public License 
version 3.0 (GPL v3.0) as published by the Free Software Foundation. For more information 
and the LICENSE file, see <https://github.com/3DCP-TUe/Python-OPC-UA>.
"""

import asyncio
import logging
from asyncua import Client, Node, ua
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

CERT = "PythonOPCUA-Client@TUE025918.der"
PRIVATE_KEY = "PythonOPCUA-Client@TUE025918.pem"


async def main():

    handler = SubHandler()

    while True:
        
        client = Client(url="opc.tcp://10.129.4.100:4840")
        
        client.set_user("TUe") ## User with write and read acces
        client.set_password("TUe")
        client.application_uri = "urn:TUE025918:PythonOPCUA-Client"
        
        await client.set_security(SecurityPolicyBasic256Sha256, certificate=CERT, private_key=PRIVATE_KEY)
            
        try:
            async with client:
                
                subscription = await client.create_subscription(10, handler)
                node = client.get_node("ns=2;s=/Channel/MachineAxis/aaVactM[1,4]")
                await subscription.subscribe_data_change(node)
                
                while True:
                    await asyncio.sleep(1)
                    await client.check_connection()  # Throws a exception if connection is lost
        
        except ua.UaError as e:
            logging.warning("An OPC UA error occurred: {}".format(e))
        except ConnectionError:
            logging.warning("Lost connection to the OPC UA server. Reconnecting in 2 seconds...")
            await asyncio.sleep(2)


class SubHandler:

    """
    Subscription Handler. To receive events from server for a subscription
    This class is just a sample class. Whatever class having these methods can be used
    """

    def datachange_notification(self, node: Node, val, data):
        
        """
        Called for every datachange notification from server
        """
        
        logging.info("datachange_notification %r %s", node, val)

    def event_notification(self, event: ua.EventNotificationList):
        
        """
        Called for every event notification from server
        """
        
        pass

    def status_change_notification(self, status: ua.StatusChangeNotification):
        
        """
        Called for every status change notification from server
        """
        
        pass 


if __name__ == "__main__":
    logging.getLogger('asyncua').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())






