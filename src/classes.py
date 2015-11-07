#TODO: Add some stuff to the classes...
import Queue

# four conversion constants:
#   KB_TO_B: converts kilobytes to bytes.
#   B_to_b: converts bytes to bits
#   MB_TO_KB: converts megabytes to kilobytes
#   s_to_ms: converts seconds to milliseconds
KB_TO_B = 1024
B_to_b = 8
MB_TO_KB = 1024
s_to_ms = 1000

# some static constants:
#   DATA_SIZE: the size of a data packet (1024B)
#   ACK_SIZE: the size of an acknowledgment packet (64B)
DATA_SIZE = 1024
ACK_SIZE = 64

class bufferQueue:
    def __init__(self, size):
        """ Initializes a buffer queue for the link

        :param size: size of queue (in packets)
        :type size: Integer
        """

        self.packets = []
        self.maxSize = size
        self.occupancy = 0

    def empty(self):
        """ Checks to see if the size of the buffer is 0.
        """

        return self.packets == []

    def put(self, packet):
        """ Puts a packet into the buffer, first in first out.

        :param packet: The packet to put into the buffer
        :type packet: Packet
        """
        self.packets.insert(0, packet)
        self.occupancy += packet.data_size

    def get(self):
        """ Pops a packet from the buffer, first in first out.
        """

        if self.empty():
            raise BufferError("Tried to get element from empty bufferQueue")
        packet = self.packets.pop()
        self.occupancy -= packet.data_size
        return packet

    def currentSize(self):
        """ Returns the current size of the buffer in terms of memory
        """
        return self.occupancy

    def peek(self):
        """ Returns the next "poppable" element, without actually popping it.
        """
        
        if self.empty():
            raise BufferError("Tried to peek element from empty bufferQueue")
        return self.packets[len(self.packets) - 1]

    def bufferFullWith(self, packet):
        """Returns True if packet cannot be added to the buffer queue, False otherwise."""
        return (self.maxSize < self.occupancy + packet.data_size)



class Network:
    #####################################################################
    #### TODO: Look at runSimulation.py, make this Network basically ####
    ####       contain all the links, flows, etc. in the same way    ####
    #####################################################################

    def __init__(self, devices, links, flows):
        """ Takes in a list of devices, links, and flows, to make up the
        entire network.

        :param devices: List of devices that will be part of the network
        :type devices: List<Device>

        :param links: List of links that will be part of the network.
        :type links: List<Link>

        :param flows: List of flows that will be part of network.
        :type flows: List<Flow>
        """
        self.devices = devices
        self.links = links
        self.flows = flows


class Device:

    ###################################################################
    ### TODO: Write what members each Device has, and its functions ###
    ###################################################################
    
    def __init__(self, deviceID):
        """Instantiates the Device.
         
        :param deviceID: Unique ID of device
        :type deviceID: str
        :param links: Stores all attached links to the device
        :type links: Array of links
        """
        self.deviceID = deviceID
        self.links = []


    def attachLink(self, link):
        """Attach single link to Device.

        :param link: link to attach
        :type link: Link
        """
        self.links.append(link)

    def sendToLink(self, link, packet):
        """Attach packet to the appropriate link buffer.

        :param link: link that packet will be going to.
        :type link: Link

        :param packet: packet that the device received.
        :type packet: Packet
        """

        link.putIntoBuffer(packet, self)

class Router(Device):

    def createTable(self, table):
        """Compute routing table via Bellman Ford.

        :param table: Routing table for the router
        :type Table: dict<(Device, Link)>
        """
        # self.table  = ...
        return table

    def transfer(self, packet):
        """ Returns the link that the packet will be forwarded to.

        :param packet: packet that will be transferred
        :type packet: Packet
        """
        prevLink = packet.curr
        prevLink.decrRate(packet)

        nextLink = self.table[packet.dest]
        return nextLink

class Host(Device):

    def getLink(self):
        """ Will return the link attached to the host.
        """
        return self.links[0]


    def receive(self, packet):
        """ Host receives packet.

        Will receive a packet and do two things:
            1) If the packet is an ACK, the host will just print that it got it.
            2) If it's data, then the packet has arrived at destination.
            3) Return the packet.
        
        :param packet: packet that will be received
        :type packet: Packet
        """

        if packet.type == "ACK":
            # do nothing
            # decrease the current link rate
            link = packet.curr
            link.decrRate(packet)
            print "Packet acknowledged by Host " + str(self.deviceID)

        elif packet.type == "DATA":
            # send an acknowledgment packet
            link = packet.curr
            link.decrRate(packet)
            print "Packet data received by recipient... sending ack from " + str(self.deviceID)


class Flow:

    def __init__(self, flowID, src, dest, data_amt, flow_start):
        """ Instantiates a Flow

        :param flowID: unique ID of flow
        :type flowID: str

        :param src: Host source of flow
        :type src: Host

        :param dest: Host destination of flow
        :type dest: Host

        :param data_amt: Data amount (in MB)
        :type data_amt: float

        :param flow_start: Time flow begins
        :type flow_start: float

        :param inTransit: List of packet ID's in transit at the moment.
        :type inTransit: List<int>

        :param window_sze: Window size in packets
        :type window_size: int
        """
        self.flowID = flowID
        self.src = src
        self.dest = dest
        self.data_amt = data_amt
        self.flow_start = flow_start
        self.inTransit = []

        self.window_size = 1


    def addPacketToTransit(self, packet):
        """ This will add a packet into the transit link.

        :param packet: Packet that is now in transit.
        :type packet: Packet
        """

        self.inTransit.append(packet.id)

    def generateDataPacket(self):
        """ This will produce a data packet, heading the forward
        direction
        """
        packet = Packet(self.src, self.dest, DATA_SIZE, "DATA", None)

        # This packet is now in transit.

        return packet

    def generateAckPacket(self, packet):
        """ This will produce an acknowledgment packet, heading the reverse
        direction
        """
        packet = Packet(self.dest, self.src, ACK_SIZE, "ACK", None)
        return packet

    def removePacketFromTransit(self, packet):
        """ This will remove a packet from the transit list

        :param packet : packet that has finished its trip.
        :type packet : Packet
        """
        self.inTransit.remove(packet.id)

    def receiveAcknowledgement(self, packet):
        #TODO
        return



class Link:

    ###############################################################
    ## TODO: Write what members each Link has, and its functions ##
    ###############################################################

    def __init__(self, linkID, rate, delay, buffer_size, device1, device2, direction):
        """ Instantiates a Link
        
        :param linkID: unique ID of link
        :type linkID: str

        :param rate: max link rate (in Mbps)
        :type rate: int
        
        :param delay: link delay (in ms)
        :type delay: int
        
        :param buffer_size: buffer size (in KB)
        :type buffer_size: int
        
        :param device1: Device 1 joined by link
        :type device1: Device
        
        :param device2: Device 2 joined by link
        :type device2: Device

        :param direction: Link direction of packets. NoneType
                          indicates inactive link.

        :param type: Boolean or NoneType
        """

        self.linkID = linkID
        self.rate = rate * MB_TO_KB * KB_TO_B / B_to_b
        self.delay = delay
        self.device1 = device1
        self.device1.attachLink(self)
        self.device2 = device2
        self.device2.attachLink(self)

        self.current_rate = 0

        self.linkBuffer = bufferQueue(buffer_size * KB_TO_B)

        self.dev1todev2 = None

    def rateFullWith(self, packet):
        """Returns True if packet cannot be sent, False otherwise."""
        return (self.rate < self.current_rate + packet.data_size)

    def sendPacket(self, device):
        """Sends next packet in buffer queue corresponding to device along link. 

        Returns packet if success, else None.
        """
        try:
            packet = self.linkBuffer.peek()
            if(not self.rateFullWith(packet)):
                self.linkBuffer.get()
                link.incrRate(packet)
                if(device == device1):
                    print "Sending a packet from device 1 to 2"
                    link.dev1todev2 = True
                else:
                    print "Sending a packet from device 2 to 1"
                    link.dev1todev2 = False
                return packet
                # possibly need to update packet location?
            else:
                return None
        except BufferError as e:
            print e

    def putIntoBuffer(self, packet):
        """Puts packet into buffer.

        :param packet : Packet to be put into the buffer.
        :type packet : Packet
        """
        self.linkBuffer.put(packet)

    def decrRate(self, packet):
        """Decrease current rate by packet size."""
        self.current_rate -= packet.data_size

    def incrRate(self, packet):
        """Increase current rate by packet size."""
        self.current_rate += packet.data_size
            

class Packet:

    def __init__(self, packetId, src, dest, data_size, data_type, curr_loc):
        """ Instatiates a Packet.

        :param packetId: ID of the packet.
        :type packetId: int

        :param src: Source (device) of packet
        :type src: Device

        :param dest: Destination (device) of packet
        :type dest: Device

        :param data_size: data size (in bytes)
        :type data_size: int

        :param data_type: type of packet, either ACK or DATA
        :type data_type: str

        :param curr_loc: Link where the packet is.
        :type curr_loc: Link
        """
        self.id = packetId
        self.src = src
        self.dest = dest
        self.data_size = data_size
        self.type = data_type
        self.curr = curr_loc

    def updateLoc(self, newLoc):
        """ Updates the location of the packet.

        :param newLoc: New location of the packet.
        :type newLoc: Device or Link
        """
        self.curr = newLoc

