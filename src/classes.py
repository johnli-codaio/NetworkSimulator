#TODO: Add some stuff to the classes...
import constants
from math import *

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
        :param neighbors: Stores all neighbors of the device
        :type neighbors: Array of Routers.
        """
        self.deviceID = deviceID
        
        self.links = []
        self.neighbors = []


    def attachLink(self, link):
        """Attach single link to Device.

        :param link: link to attach
        :type link: Link
        """
        print self
        print link

        self.links.append(link)
        self.neighbors.append(link.otherDevice(self))


    def sendToLink(self, link, packet):
        """Attach packet to the appropriate link buffer.

        :param link: link that packet will be going to.
        :type link: Link

        :param packet: packet that the device received.
        :type packet: Packet
        """

        link.putIntoBuffer(packet)
        packet.curr = link

    def __str__(self):
        s = "Device is: " + "HOST" if isinstance(self, Host) else "ROUTER"
        s += "\nName is: " + str(self.deviceID)
        s += "\nLinks: " + str([l.linkID for l in self.links])
        s += "\n"
        return s

class Router(Device):

    def receiveRoutingPacket(self, packet):
        """Receives a routing packet.

        If packet is from host, update routing table.
        If packet is from another router, send new packets.
        """
        return


    def sendRoutingPackets(self, packet = None):
        """Sends a routing packet to each adjacent device."""

        # TODO:
        if(packet == None):
            packet = RoutingPacket(self, self, rout_to = None, distance = 0)


    def initializeDistTable(self):
        """Initializes table of distances to other devices.
        """

        self.distTable = {}
        self.distTable[self] = 0

        for link in links:
            otherDev = link.otherDevice(self)
            self.distTable[otherDev] = link.delay

    def transferTo(self, packet):
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
            3) Return the packet ????

        :param packet: packet that will be received
        :type packet: Packet
        """

        print "Host " + self.deviceID + " received " + packet.data_type + "packet"

        if(packet.data_type == "ACK"):
            # decrease the current link rate
            link = packet.curr
            link.decrRate(packet)
            print "Packet " + packet.packetID + " acknowledged by Host " + str(self.deviceID)

        elif(packet.data_type == "DATA"):
            # send an acknowledgment packet
            link = packet.curr
            link.decrRate(packet)
            print "Packet " + packet.packetID + " received by Host" + str(self.deviceID)

        #elif(packet.data_type == "ROUT"):
            # stuff
            

class Flow:


    # Should be responsible for
    # - Generating all packets
    # - Dealing with congestion control
    # -

    def __init__(self, flowID, src, dest, data_amt, flow_start):
        """ Instantiates a Flow

        :param flowID: unique ID of flow
        :type flowID: str

        :param src: Host source of flow
        :type src: Host

        :param dest: Host destination of flow
        :type dest: Host

        :param data_amt: Data amount (in bytes)
        :type data_amt: float

        :param flow_start: Time flow begins (in ms)
        :type flow_start: float

        :param inTransit: List of packet ID's in transit at the moment.
        :type inTransit: List<int>

        :param window_size: Window size in packets
        :type window_size: int

        :param packets: List of all packet ID's generated by flow, aka needed to be sent.
        :type packets: List<int>
        """
        self.flowID = flowID
        self.src = src
        self.dest = dest
        self.data_amt = data_amt * constants.MB_TO_KB * constants.KB_TO_B
        self.current_amt = 0
        self.flow_start = flow_start * constants.s_to_ms


        self.window_size = 1

        # Congestion Control Variables
        self.packets = []
        self.acksAcknowledged = [] # Array of bools that will go from false to true
                                   # when an ack is received.
        self.window_upper = 0
        self.packets_index = 0
        self.window_lower = 0
        self.window_counter = 0
        self.error_counter = 0

        self.resending = False

        # How much successfully sent.
        self.data_acknowledged = 0

    def __str__(self):
        s = "Flow ID is: " + str(self.flowID)
        s += "\nSource is: " + str(self.src)
        s += "\nDestination is: " + str(self.dest)
        s += "\nData amount in bytes is: " + str(self.data_amt)
        s += "\nFlow start time in ms is: " + str(self.flow_start)
        return s

    def initializePackets(self):
        """ We will create all the packets and put them into
            an array.
        """

        index = 0

        while(self.current_amt < self.data_amt):
            packetID = self.flowID + "token" + str(index)
            packet = DataPacket(index, self.src, self.dest, "DATA", constants.DATA_SIZE, packetID, None)
            self.packets.append(packet)
            self.acksAcknowledged.append(False)
            self.current_amt = self.current_amt + constants.DATA_SIZE
            index = index + 1


    def checkIfAcked(self, packetId):
        """ We will check if a particular packet has been acked.
            this is for the timeOut portion.
        """
        return self.acksAcknowledged[packetId] == True


    def selectDataPacket(self):
        """ When we call SELECTPACK events, we
            just send in the next packet that can be sent in the 
            array. (This is tracked by packets_index).
        """

        if self.packets_index >= len(self.packets):
            print "WE REACHED THE END: " + str(self.packets_index)
            return None

        else:
            ## TODO: Refactor so that we're just taking packets out of an array.
            ## We want to create all the packets before hand. 
            ## So, we'll probably need a new event like "Initialize" or something
            ## To initialize the flow packet.
            packet = self.packets[self.packets_index]
            self.packets_index = self.packets_index + 1
            return packet

    def printDataSent(self):
        """ Prints how much data this flow has generated so far
        """

        print ("Flow " + str(self.flowID) + " has generated "
                + str(float(self.current_amt) /
                    (constants.MB_TO_KB * constants.KB_TO_B))
                + " MB so far")


    def generateAckPacket(self, packet):
        """ This will produce an acknowledgment packet with same ID, heading the reverse
        direction
        """
        newPacket = DataPacket(packet.index, packet.dest, packet.src, "ACK", constants.ACK_SIZE, packet.packetID, None)
        return newPacket

    # TODO: refactor
    def receiveAcknowledgement(self, packet):
        """ This will call TCPReno to update the window size depending on
            the ACK ID...

        :param packet: packet that will be compared.
        :type packet: Packet
        """

        # Updates the expected ack packet id.

        # If the ACK ID matches the host's expected ACK ID, then 
        # we increment the hosts expected ACK ID by one.
        print "Host expects: " + self.packets[self.window_lower].packetID
        print "Host received: " + packet.packetID

        print "HOST EXPECT: " + str(self.window_lower) + \
              " PACKET INDEX: " + str(self.packets_index) + \
              " ACK INDEX: " + str(packet.packetID)

        print str(packet.index)

        if self.packets[self.window_lower].packetID == packet.packetID:
            self.data_acknowledged = self.data_acknowledged + constants.DATA_SIZE
            self.acksAcknowledged[packet.index] = True

            if self.window_lower != len(self.packets) - 1:
                while self.acksAcknowledged[self.window_lower] == True:

                    if self.window_lower == len(self.packets) - 1:
                        pass
                    else:
                        self.window_lower = self.window_lower + 1
            self.error_counter = 0
            self.resending = False
            self.TCPReno(True)

        elif self.resending == True:
            if self.acksAcknowledged[packet.index] == False:
                self.acksAcknowledged[packet.index] = True
                self.data_acknowledged = self.data_acknowledged + constants.DATA_SIZE
                self.TCPReno(True)

        else:
            self.error_counter = self.error_counter + 1

            if self.acksAcknowledged[packet.index] == False:
                self.acksAcknowledged[packet.index] = True
                self.data_acknowledged = self.data_acknowledged + constants.DATA_SIZE

            if(self.error_counter == 3):
                #self.threshIndex = self.packets_index
                self.TCPReno(False)
                print "DROPPED PACKET " + self.packets[self.window_lower].packetID + \
                    "... GOBACKN.\n"
                self.resending = True
                self.error_counter = 0
                return True


        print "Window counter: " + str(self.window_counter)
        return False
            
    # Congestion Control:
    # IDEA: We have an array of all the packets. We also will store 
    #       several congestion control variables: 
    #           packet index
    #           ackPacket index. 
    #
    #       The ackPacket index will only change if a host receives a 
    #       correct ackPacket in order. The packet counter will change
    #       after a packet is sent.
    #       
    #       We will be detecting lost packets (controlled by the host)
    #       by comparing the ackPacket id to the expected ack packet id.
    #       Then, we will update things accordingly.

    def TCPReno(self, boolean):
        """ The boolean that will determine if window size 
            increases or decreases.
        """

        # If true, we increment window size slightly.
        if boolean == True:
            self.window_size = self.window_size + float(1) / float(self.window_size)
            self.window_upper = floor(self.window_size) + self.window_lower - 1

            if(self.window_upper > len(self.packets) - 1):
                self.window_upper = len(self.packets) - 1

        # Else, we will halve the window size, and reset the index of the packet.
        else:
            self.window_size = self.window_size / 2
            self.window_upper = floor(self.window_size) + self.window_lower - 1

            if(self.window_upper > len(self.packets) - 1):
                self.window_upper = len(self.packets) - 1

        print "Window size: " + str(self.window_size)
        print "Window Upper: " + str(self.window_upper)

    def getWindowSize(self):
        #TODO
        return self.window_size


class Link:

    ###############################################################
    ## TODO: Write what members each Link has, and its functions ##
    ###############################################################

    def __init__(self, linkID, rate, delay, buffer_size, device1, device2):
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
        self.rate = rate
        self.delay = delay
        self.device1 = device1
        self.device2 = device2
        self.current_rate = 0 #BYTES
        self.linkBuffer = bufferQueue(buffer_size * constants.KB_TO_B)

        self.dev1todev2 = None

        self.device1.attachLink(self)
        self.device2.attachLink(self)


    def __str__(self):
        s = "Link ID is: " + str(self.linkID)
        s += "\nConnects devices: " + str(self.device1.deviceID) + " " + \
            str(self.device2.deviceID)
        s += "\nLink rate: " + str(self.rate)
        s += "\nLink delay: " +  str(self.delay)
        s += "\nLink buffer size: " +  str(self.linkBuffer.maxSize)
        s += "\n"
        return s

    def otherDevice(self, device):
        """Returns the other device

        :param device: One of the devices connected to the link
        :type device: Device
        """

        if(self.device1 == device):
            return self.device2
        else:
            return self.device1

    def rateFullWith(self, packet):
        """Returns True if packet cannot be sent, False otherwise.
        :param packet: the packet that is about to be sent out
        :type packet: Packet
        """
        return (self.rate <= self.currentRateMbps(packet))

    def sendPacket(self, device):
        """Sends next packet in buffer queue corresponding to device along link.
        Returns packet if success, else None.
        Should only fail when there the link is at its maximum capacity.

        :param device: device packet should be sent to
        :type device: Device

        """
        try:
            packet = self.linkBuffer.peek()
            if(not self.rateFullWith(packet)):
                self.linkBuffer.get()
                self.incrRate(packet)
                if(device == self.device1):
                    print "Sending a packet from device 1 to 2"
                    self.dev1todev2 = True
                else:
                    print "Sending a packet from device 2 to 1"

                    self.dev1todev2 = False
                return packet
                # possibly need to update packet location?
            else:
                # if isinstance(packet, Packet):
                #     print "Packet ", packet.packetID, " not sent"
                return None
        except BufferError as e:
            print e

    def putIntoBuffer(self, packet):
        """Puts packet into buffer.

        :param packet : Packet to be put into the buffer.
        :type packet : Packet
        """

        if(packet.data_size + self.linkBuffer.occupancy >
           self.linkBuffer.maxSize):
            print "Packet dropped"
        else:
            self.linkBuffer.put(packet)


    def decrRate(self, packet):
        """Decrease current rate by packet size.

        :param packet : uses the size of the passed in packet.
        :type packet : Packet"""
        self.current_rate -= packet.data_size

    def incrRate(self, packet):
        """Increase current rate by packet size.

        :param packet : uses the size of the passed in packet.
        :type packet : Packet
        """
        self.current_rate += packet.data_size

    def currentRateMbps(self, packet):
        """Gets the link rate, in Mbps, if a packet were added.
        Used for logging. If the packet argument
        isn't specified, then it just returns the current rate.
        :param packet : Packet to be sent using this link
        :type packet : Packet
        """
        if packet:
            return (float(self.current_rate + packet.data_size) /
                (constants.MB_TO_KB * constants.KB_TO_B / constants.B_to_b) /
                (self.delay / constants.s_to_ms))

        else:
            return (float(self.current_rate) /
                (constants.MB_TO_KB * constants.KB_TO_B / constants.B_to_b) /
                (self.delay / constants.s_to_ms))

class Packet(object):
    def __init__(self, src, dest, data_type, data_size, packetID, curr_loc):
        self.src = src
        self.dest = dest
        self.data_type = data_type # ROUT, ACK, DATA
        self.data_size = data_size
        self.packetID = packetID
        self.curr = curr_loc

    def updateLoc(self, newLoc):
        """ Updates the location of the packet.

        :param newLoc: New location of the packet.
        :type newLoc: Device, Link
        """
        self.curr = newLoc


class DataPacket(Packet):
    # Captures both acknowledgement packets and actual data packets
    # Differentiated from routing packets

    def __init__(self, index, src, dest, data_type, data_size, packetID, curr_loc):
        """ Instatiates a Packet.

        :param packetID: ID of the packet.
        :type packetID: string

        :param index: The packet (in #) that was sent by flow.
        :type index: int 

        :param src: Source (device) of packet
        :type src: Device

        :param dest: Destination (device) of packet
        :type dest: Device

        :param data_size: data size (in bytes)
        :type data_size: int

        :param curr_loc: Link where the packet is.
        :type curr_loc: Link
        """
        super(DataPacket, self).__init__(src, dest, data_type, data_size, packetID, curr_loc)
        self.index = index

class RoutingPacket(Packet):

    def __init__(self, src, dest, data_size, table, latency, packetID, curr_loc):
        super(RoutingPacket, self).__init__(src, dest, "ROUT", constants.ROUTING_SIZE, packetID, curr_loc)

        self.latency = latency
        self.table = table
