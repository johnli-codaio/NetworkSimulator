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
        """ Returns the current size of the buffer in terms of bytes
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
        :type devices: Dict<DeviceID, Device>

        :param links: List of links that will be part of the network.
        :type links: Dict<LinkID, Link>

        :param flows: List of flows that will be part of network.
        :type flows: Dict<FlowID, Flow>
        """
        self.devices = devices
        self.links = links
        self.flows = flows

    def allFlowsComplete(self):
        for flowID in self.flows:
            flow = self.flows[flowID]
            if(not flow.flowComplete()):
                return False
        return True


class Device(object):

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
        packet.currLink = link

        packet.currDev = self

        if(link.device1 == packet.currDev):
            packet.nextDev = link.device2
        else:
            packet.nextDev = link.device1

        packet.total_delay = packet.total_delay + link.delay

    def __str__(self):
        s = "Device is: " + ("HOST" if isinstance(self, Host) else "ROUTER")
        s += "\nName is: " + str(self.deviceID)
        s += "\nLinks: " + str([l.linkID for l in self.links])
        s += "\n"
        return s

class Router(Device):

    def __init__(self, deviceID):
        super(Router, self).__init__(deviceID)


        # Dictionary rout_table:
        #   - Device
        #       - (latency, nextLink)
        self.rout_table = {}
        self.initializeNeighborsTable()

        self.routing_table_recently_updated = True

    def __str__(self):
        s = super(Router, self).__str__()
        s += "Routing table: \n"
        for device in self.rout_table:

            (latency, nextLink) = self.rout_table[device]
            s += "Device " + str(device.deviceID) + " has distance " + \
                str(latency) + " with nextLink " + \
                (str(nextLink.linkID) if nextLink != None else 'N/A')
            s += "\n"
        return s

    def initializeNeighborsTable(self):
        """Initializes table to include neighbors.
        """
        for link in self.links:
            otherDev = link.otherDevice(self)
            self.rout_table[otherDev] = (link.delay, link)

        self.rout_table[self] = (0, None)

    def initializeRerout(self):
        for device in self.rout_table:
            if device == self:
                self.rout_table[device] = (0, None)

            nextLink = self.rout_table[device][1]
            self.rout_table[device] = (constants.ROUTING_INF, nextLink)

        for link in self.links:
            otherDev = link.otherDevice(self)
            self.rout_table[otherDev] = (link.calcExpectedLatency(), link)

    def handleRoutingPacket(self, packet):
        '''Updates routing table if appropriate. Returns if router should send table to neighbors.'''

        #assert(isinstance(packet, RoutingPacket))
        updated = False

        # Decrease the link rate size.
        link = packet.currLink
        link.decrRate(packet)

        # comingFrom = packet.link.otherDevice(self)

        for device in packet.table:
            dist = packet.latency + packet.table[device][0]

            if(device not in self.rout_table):
                self.rout_table[device] = (dist, packet.link)
                updated = True
            else:
                mindist = self.rout_table[device][0]
                if(dist < mindist):
                    self.rout_table[device] = (dist, packet.link)
                    updated = True


        # for device in packet.table:
        #     if(device == comingFrom and packet.timestamp):
        #         self.rout_table[device] = (current_time - packet.timestamp, packet.link)
        #         updated = True

        #     else:
        #         if(packet.timestamp):
        #             dist = current_time - packet.timestamp + packet.table[device][0]
        #         else:
        #             dist = packet.latency + packet.table[device][0]

        #         if(device not in self.rout_table):
        #             self.rout_table[device] = (dist, packet.link)
        #             updated = True
        #         else:
        #             mindist = self.rout_table[device][0]
        #             if(dist < mindist):
        #                 self.rout_table[device] = (dist, packet.link)
        #                 updated = True

        # Router sends table to adjacent neighbors if recently updated or just updated
        temp = self.routing_table_recently_updated
        self.routing_table_recently_updated = updated
        return temp or updated

    def floodNeighbors(self, dynamic = False):
        '''Returns array of tuples (packet, link) to send'''

        # send current table to all neighbors
        res = []
        for link in self.links:
            otherDev = link.otherDevice(self)
            if(isinstance(otherDev, Host)):
                continue

            if(dynamic):
                routPacket = RoutingPacket(self, otherDev, link, constants.ROUTING_SIZE,
                                        self.rout_table, str(self.deviceID) + " ROUT", curr_loc = None,
                                        latency = link.calcExpectedLatency())
            else:
                routPacket = RoutingPacket(self, otherDev, link, constants.ROUTING_SIZE,
                                       self.rout_table, str(self.deviceID) + " ROUT", curr_loc = None)

            res.append((routPacket, link))
        return res

    def transferTo(self, packet):
        """ Returns the link that the packet will be forwarded to.

        :param packet: packet that will be transferred
        :type packet: Packet
        """
        prevLink = packet.currLink
        prevLink.decrRate(packet)

        nextLink = self.rout_table[packet.dest][1]
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
            link = packet.currLink
            link.decrRate(packet)
            print "Packet " + packet.packetID + " acknowledged by Host " + str(self.deviceID)

        elif(packet.data_type == "DATA"):
            # send an acknowledgment packet
            link = packet.currLink
            link.decrRate(packet)
            print "Packet " + packet.packetID + " received by Host" + str(self.deviceID)
        # if packet is ROUTING, do nothing

class Flow:

    def __init__(self, flowID, src, dest, data_amt, flow_start, theoRTT):
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

        :param window_size: Window size in packets
        :type window_size: int

        :param packets: List of all packet ID's generated by flow, aka needed to be sent.
        :type packets: List<int>

        :param theoRTT: The theoretical round trip time of a packet in this flow.
        :type theoRTT: int

        :param minRTT: The observed minimum rtt of a packet in this flow.
        :type minRTT: float
        """
        self.flowID = flowID
        self.src = src
        self.dest = dest
        self.data_amt = data_amt * constants.MB_TO_KB * constants.KB_TO_B
        self.flow_start = flow_start * constants.s_to_ms
        self.current_amt = 0
        self.flow_start = flow_start * constants.s_to_ms
        self.theoRTT = theoRTT
        self.actualRTT = 0
        self.minRTT = 9999999999;

        self.window_size = 1

        #keeps track of the first time a packet is acknowledged
        self.first_time = 0

        # Congestion Control Variables
        self.packets = []
        self.acksAcknowledged = [] # Array of bools that will go from false to true
                                   # when an ack is received.
        self.window_upper = 0
        self.packets_index = 0
        self.window_lower = 0
        self.window_counter = 0
        self.error_counter = 0
        self.slow = True
        self.slowThresh = 1000000
        self.resending = False

        # How much successfully sent.
        self.data_acknowledged = 0

        #whether it has received a packet or not in the last fast-tcp cycle
        self.received_packet = False

        # keeps track so that we can more accurately measure the RTT of non-returned packets
        self.last_received_packet_start_time = 0

        self.packet_delay = 0

    def __str__(self):
        s = "Flow ID is: " + str(self.flowID)
        s += "\nSource is: " + str(self.src)
        s += "\nDestination is: " + str(self.dest)
        s += "\nData amount in bytes is: " + str(self.data_amt)
        s += "\nFlow start time in ms is: " + str(self.flow_start)
        return s

    def flowComplete(self):
        """ Returns True if flow is done sending, False otherwise """
        for s in self.acksAcknowledged:
            if s == False:
                return False
        return True

    def initializePackets(self):
        """ We will create all the packets and put them into
            an array.
        """

        index = 0

        while(self.current_amt < self.data_amt):
            packetID = self.flowID + "token" + str(index)
            packet = DataPacket(index, self.src, self.dest, "DATA", constants.DATA_SIZE, packetID, None, flow = self)
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
        start_time = packet.start_time
        total_delay = packet.total_delay
        newPacket = DataPacket(packet.index, packet.dest, packet.src, "ACK", constants.ACK_SIZE,
                               packet.packetID, None, flow = self)
        newPacket.start_time = start_time
        newPacket.total_delay = packet.total_delay
        return newPacket

    # TODO: Gotta refactor this.
    def receiveAcknowledgement(self, packet, currentTime, tcp_type):
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

        print "currentTime: " + str(currentTime)
        print "packet.start_time: " + str(packet.start_time)
        print "self.actual-RTT: " + str(self.actualRTT)

        ##### IMPORTANT NOTE #####
        ### The way TCP-Fast is currently implemented, we
        # use the highest rtt in the 20-ms period as the RTT, not the
        # last rtt. I'm not sure if this is correct.
        # TODO: TODO: Check with TAs
        if currentTime - packet.start_time > self.actualRTT:
            self.actualRTT = currentTime - packet.start_time
            if self.actualRTT < self.minRTT:
                #print "minRTT: " + str(self.flowID) + " " + str(self.minRTT)
                print "old minRTT: " + str(self.flowID) + " " + str(self.minRTT)
                self.minRTT = self.actualRTT
                print "new minRTT: " + str(self.flowID) + " " + str(self.minRTT)

        #check if actualRTT is valid
        if self.actualRTT != 0 and self.actualRTT < self.theoRTT:
            raise Exception("Calculated RTT is less than theoretical RTT")


        if self.packets[self.window_lower].packetID == packet.packetID:
            # Change variable to show a packet was received in TCPFast Cycle!
            self.received_packet = True
            print "ACK Packet " + str(packet.packetID) + " acknowledged."
            self.last_received_packet_start_time = packet.start_time
            ##############################################################

            self.data_acknowledged = self.data_acknowledged + constants.DATA_SIZE
            self.acksAcknowledged[packet.index] = True

            print "Window Lower: " + str(self.window_lower)

            while (self.acksAcknowledged[self.window_lower] == True) and \
                  (self.window_lower != len(self.packets) - 1):

                if(self.acksAcknowledged[self.window_lower] == True):

                    if self.window_lower == len(self.packets) - 1:
                        pass
                    else:
                        self.window_lower = self.window_lower + 1


            self.error_counter = 0
            self.resending = False
            if tcp_type == 'Reno':
                self.TCPReno(True)

            elif tcp_type == 'FAST': #still have to update window bounds
                self.window_upper = floor(self.window_size) + self.window_lower - 1

                if(self.window_upper > len(self.packets) - 1):
                    self.window_upper = len(self.packets) - 1

        elif self.resending == True:
            # TODO: TODO:
            # NOTE: I think there's something buggy here, since
            # if we enter this loop as part of TCP-fast, something weird happens

            if self.acksAcknowledged[packet.index] == False:
                self.received_packet = True
                print "ACK Packet " + str(packet.packetID) + " acknowledged."
                self.last_received_packet_start_time = packet.start_time
                self.acksAcknowledged[packet.index] = True
                self.data_acknowledged = self.data_acknowledged + constants.DATA_SIZE
                if tcp_type == 'Reno':
                    self.TCPReno(True)

        else:
            self.error_counter = self.error_counter + 1

            if self.acksAcknowledged[packet.index] == False:
                self.acksAcknowledged[packet.index] = True
                self.data_acknowledged = self.data_acknowledged + constants.DATA_SIZE
                self.received_packet = True
                print "ACK Packet " + str(packet.packetID) + " acknowledged."
                self.last_received_packet_start_time = packet.start_time

            if(self.error_counter == 3):
                #self.threshIndex = self.packets_index
                if tcp_type == 'Reno':
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

        if(self.slowThresh > self.window_size):
            self.slow = True
        else:
            self.slow = False

        # If true, we increment window size slightly.
        if boolean == True and self.slow == True:
            self.window_size = self.window_size + 1
            self.window_upper = floor(self.window_size) + self.window_lower - 1

            if(self.window_upper > len(self.packets) - 1):
                self.window_upper = len(self.packets) - 1

        elif boolean == True and self.slow == False:
            self.window_size = self.window_size + float(1) / float(self.window_size)
            self.window_upper = floor(self.window_size) + self.window_lower - 1

            if(self.window_upper > len(self.packets) - 1):
                self.window_upper = len(self.packets) - 1

        # Else, we will halve the window size, and reset the index of the packet.
        elif boolean == False and self.slow == False:
            self.window_size = self.window_size / 2
            if(self.window_size < 2):
                self.window_size = 2
            self.window_upper = floor(self.window_size) + self.window_lower - 1

            if(self.window_upper > len(self.packets) - 1):
                self.window_upper = len(self.packets) - 1

        else:
            self.window_size = self.window_size / 2

            if(self.window_size < 2):
                self.window_size = 2

            self.slowThresh = self.window_size
            self.window_upper = floor(self.window_size) + self.window_lower - 1

            self.slow = True

            if(self.window_upper > len(self.packets) - 1):
                self.window_upper = len(self.packets) - 1

        print "Window size: " + str(self.flowID) + " " + str(self.window_size)
        print "Window Upper: " + str(self.window_upper)

    def TCPFast(self, alpha):
        """ The actualRTT is calculated by subtracting event.time
            by the start time of the packet. The theoretical RTT of the
            packet is denoted in the "packet.total_delay" attribute.

            :param alpha : A constant we add to window.
            :type alpha : int

            :param timeout : A constant we use to indicate if we bypass, 0 for no bypass, 1 for bypass
            :type timeout : int
        """

        print "theoRTT: " + str(self.theoRTT)
        print "actualRTT: " + str(self.actualRTT)


        if self.flowID == "F1":
            print "TCPFast flow1"

        if self.flowID == "F2":
            print "TCPFast flow2"

        if self.flowID == "F3":
            print "TCPFast flow3"        

        newWindowSize = (self.minRTT/self.actualRTT) * self.window_size + alpha
        self.window_size = newWindowSize

        self.window_upper = floor(self.window_size) + self.window_lower - 1

        if(self.window_upper > len(self.packets) - 1):
            self.window_upper = len(self.packets) - 1

        print "Window size: " + str(self.flowID) + " " + str(self.window_size)
        print "Window Upper: " + str(self.window_upper)


    def getWindowSize(self):
        return self.window_size

    def timeOut(self):
        self.window_size = 1
        self.slowThresh = 1000000

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
        self.maxRate = rate
        self.delay = delay
        self.device1 = device1
        self.device2 = device2
        self.current_byte_size = 0 #BYTES
        self.linkBuffer = bufferQueue(buffer_size * constants.KB_TO_B)

        self.device1.attachLink(self)
        self.device2.attachLink(self)

        self.isDropped = False


    def __str__(self):
        s = "Link ID is: " + str(self.linkID)
        s += "\nConnects devices: " + str(self.device1.deviceID) + " " + \
            str(self.device2.deviceID)
        s += "\nLink rate: " + str(self.maxRate)
        s += "\nLink delay: " +  str(self.delay)
        s += "\nLink buffer size: " +  str(self.linkBuffer.maxSize)
        s += "\n"
        return s

    def droppedPacket(self):
        if self.isDropped:
            # revert the boolean back because we've already dropped a packet
            self.isDropped = False
            return 1
        return 0

    def calcExpectedLatency(self):
        return self.delay + (self.linkBuffer.currentSize() * constants.QUEUE_DELAY)



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

        :param packet: packet potentially to be sent out
        :type packet: Packet
        """
        return (self.maxRate <= self.currentRateMbps(packet))

    def sendPacket(self):
        """Sends next packet in buffer queue corresponding to device along link.
        Returns packet if success, else None.
        Should only fail when there the link is at its maximum capacity.

        :param device: device packet should be sent to
        :type device: Device

        """
        packet = self.linkBuffer.peek()
        if(not self.rateFullWith(packet)):
            self.linkBuffer.get()
            self.incrRate(packet)
            return packet
        else:
            return None

    def putIntoBuffer(self, packet):
        """Puts packet into buffer.

        :param packet : Packet to be put into the buffer.
        :type packet : Packet
        """

        print "Link " + str(self.linkID) + " with buffer size " + str(self.linkBuffer.occupancy)
        if(packet.data_size + self.linkBuffer.occupancy >
           self.linkBuffer.maxSize):
            print "Packet dropped"
        else:
            self.linkBuffer.put(packet)


    def decrRate(self, packet):
        """Decrease current rate by packet size.

        :param packet : uses the size of the passed in packet.
        :type packet : Packet"""
        self.current_byte_size -= packet.data_size

    def incrRate(self, packet):
        """Increase current rate by packet size.

        :param packet : uses the size of the passed in packet.
        :type packet : Packet
        """
        self.current_byte_size += packet.data_size

    def currentRateMbps(self, packet):
        """Gets the link rate, in Mbps, if a packet were added.
        Used for logging. If the packet argument
        isn't specified, then it just returns the current rate.
        :param packet: Packet to be sent using this link
        :type packet: Packet
        """
        if packet:
            return (float(self.current_byte_size + packet.data_size) /
                (constants.MB_TO_KB * constants.KB_TO_B / constants.B_to_b) /
                (self.delay / constants.s_to_ms))

        else:
            return (float(self.current_byte_size) /
                (constants.MB_TO_KB * constants.KB_TO_B / constants.B_to_b) /
                (self.delay / constants.s_to_ms))


class Packet(object):
    def __init__(self, src, dest, data_type, data_size, packetID, curr_loc):
        self.src = src
        self.dest = dest
        self.data_type = data_type # ROUT, ACK, DATA
        self.data_size = data_size
        self.packetID = packetID
        self.currLink = curr_loc
        self.currDev = None
        self.nextDev = None
        self.start_time = 0
        self.total_delay = 0

        self.flow = None

    def updateLoc(self, newLoc):
        """ Updates the location of the packet.

        :param newLoc: New location of the packet.
        :type newLoc: Device, Link
        """
        self.currLink = newLoc

    def recallFlowID(self):
        return str(self.packetID)[:2]


class DataPacket(Packet):
    # Captures both acknowledgement packets and actual data packets
    # Differentiated from routing packets

    def __init__(self, index, src, dest, data_type, data_size, packetID, curr_loc, flow):
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

        :param data_type: type of packet, either ACK, DATA
        :type data_type: str

        :param curr_loc: Link where the packet is.
        :type curr_loc: Link

        :param time: time when the packet is created.
        We refer to 'creation time' as when the packet is selected
        from a list of initialized packets, i.e., the result of selectDataPacket().
        :type time: float
        """
        super(DataPacket, self).__init__(src, dest, data_type, data_size, packetID, curr_loc)
        self.index = index
        self.flow = flow

class RoutingPacket(Packet):

    def __init__(self, src, dest, link, data_size, table, packetID, curr_loc, latency = None):
        super(RoutingPacket, self).__init__(src, dest, "ROUT", constants.ROUTING_SIZE, packetID, curr_loc)
        if(latency):
            self.latency = latency
        else:
            self.latency = link.delay
        self.table = table

        # RoutingPackets only travel across one link before "dying"
        self.link = link
