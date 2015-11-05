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


class Device:

    ###################################################################
    ### TODO: Write what members each Device has, and its functions ###
    ###################################################################
    
    def __init__(self, deviceID):
        """Instantiates the Device.
         
        :param deviceID: Unique ID of device
        :type deviceID: str
        :param queue: a Queue data structure which keeps track of received packets for host, and moving packets for routers.
        :type queue: Queue.Queue()
        :param links: Stores all attached links to the device
        :type links: Array of links
        """
        self.deviceID = deviceID
        self.links = []
        self.queue = Queue.Queue()


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

        link.putIntoBuffer(packet)
        packet.updateLoc(link)

    def sendToHostBuffer(self, packet):
        """Attach the packet to the device queue.

        :param packet: packet that will be sent to the buffer.
        :type packet: Packet
        """
        self.queue.put(packet)

class Router(Device):

    # def createTable(self, table):
    #     """Compute routing table via Bellman Ford.
    #     :param table: Routing table for the router
    #     :type Table: Dictionary
    #    return table

    def receiving(self, link, packet):
        pass
        
class Host(Device):

    def getLink(self):
        return self.links[0]

    # TO FIX:
    # #processes the receiving packet
    # def receiving(self):
    #     packet = Device.receiving(self, self.getLink())
    #     if packet.type == "ACK":
    #         # do nothing
    #         # decrease the current link rate
    #         pass
    #     elif packet.type == "DATA":
    #         # send an acknowledgment packet
    #         # TODO
    #         pass
    #     return packet

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
        """
        self.flowID = flowID
        self.src = src
        self.dest = dest
        self.data_amt = data_amt
        self.flow_start = flow_start
        # self.sendTime = sendTime

    # This method will generate data packets for the flow.
    def generateDataPacket(self):
        packet = Packet(self.src, self.dest, DATA_SIZE, "data", self.src)
        return packet

    # This method will generate acknowledgment packets for the flow.
    def generateAckPacket(self):
        packet = Packet(self.src, self.dest, ACK_SIZE, "acknowlegment", self.src)
        return packet


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

        self.current_buffer_occupancy = 0
        self.current_rate = 0

        self.linkBuffer1 = bufferQueue(buffer_size * KB_TO_B)
        self.linkBuffer2 = bufferQueue(buffer_size * KB_TO_B)

        # Links are initially inactive.
        self.dev1todev2 = None

        
    def bufferFullWith(self, packet):
        """Returns True if packet cannot be added to the buffer queue, False otherwise."""
        return (self.buffer_size < self.current_buffer_occupancy + 
                packet.data_size)

    def rateFullWith(self, packet):
        """Returns True if packet cannot be sent, False otherwise."""
        return (self.rate < self.current_rate + packet.data_size)

    def sendPacket(self):
        """Sends next packet in queue along link.

        Pops packet from queue, increase current link rate, modifies ...
        """

        try:
            packet = self.peekFromBuffer()
        except BufferError as e:
            print e

        if not self.rateFullWith(packet):
            if link.dev1todev2:
                print "Sending a packet: dev1 -> dev2"
                packet = self.popFromBuffer()
                nextLocation = link.device2
                packet.updateLoc(nextLocation)
                nextLocation.sendToHostBuffer(packet)

            elif link.dev1todev2 == False:
                print "Sending a packet: dev2 -> dev1"
                packet = self.popFromBuffer()
                nextLocation = link.device1
                packet.updateLoc(nextLocation)
            return True
        return False

    def decrRate(self, packet):
        """Decrease current rate by packet size."""
        self.current_rate -= packet.data_size

    def incrRate(self, packet):
        """Increase current rate by packet size."""
        self.current_rate += packet.data_size

    def bufferEmpty(self):
        """Returns True if linkBuffer is empty, False otherwise"""
        return self.linkBuffer.empty()

    def peekFromBuffer(self):
        """Returns top element of linkBuffer without popping."""
        return self.linkBuffer.peek()

    def popFromBuffer(self):
        """Pops top element of linkBuffer and returns it.

        Modifies current buffer occupany"""
        if()
        popped_elem = self.linkBuffer.get()
        print "popped off buffer!"
        self.current_buffer_occupancy -= popped_elem.data_size
        return popped_elem


    def putIntoBuffer(self, packet):
        """Adds packet to linkBuffer. Returns True if added, else False.

        Modifies current buffer occupancy as well."""

        if not self.bufferFullWith(packet):
            print "putting into buffer..."
            self.linkBuffer.put(packet)
            self.current_buffer_occupancy += packet.data_size
            return True
        else:
            print "unable to put in buffer"
            return False



class Packet:


    def __init__(self, src, dest, data_size, data_type, curr_loc):
    """ Instatiates a Packet.

    :param src: Source (device) of packet
    :type src: Device

    :param dest: Destination (device) of packet
    :type dest: Device

    :param data_size: data size (in bytes)
    :type data_size: int

    :param data_type: metadata, either ACK or DATA
    :type data_type: str

    :param curr_loc: Device or Link where the packet is.
    :type curr_loc: Device or Link
    """
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

