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
s_to_ms = 100

# some static constants:
#   DATA_SIZE: the size of a data packet (1024B)
#   ACK_SIZE: the size of an acknowledgment packet (64B)
DATA_SIZE = 1024
ACK_SIZE = 64

class bufferQueue:
    def __init__(self):
        self.items = []

    def empty(self):
        return self.items == []

    def put(self, item):
        self.items.insert(0,item)

    def get(self):
        if self.empty():
            raise BufferError("Tried to get element from empty bufferQueue")
        return self.items.pop()

    def size(self):
        return len(self.items)

    def peek(self):
        if self.empty():
            raise BufferError("Tried to peek element from empty bufferQueue")
        return self.items[len(self.items) - 1]

    def get_most_recent(self):
        return 0

    def qsize(self):
        return len(self.items)


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

    # we can think of this as a "queue" of packets currently being sent
    # enqueue a packet, send from
    # a particular link, into the device's 'receive queue', so that it
    # can process packets as they arrive
    def sending(self, link, packet):
        self.queue.put(packet)
        link.incrRate(packet)

    # the actual processing of the sent packets
    # we have to return the packet, so that we can update the total
    # amount of data sent
    def receiving(self, link):
        packet = self.queue.get()
        print "Received data of type: " + packet.type
        link.decrRate(packet)
        return packet


class Router(Device):

    # This will set a created routing table into the router's table.
    # The table will be decided using Bellman Ford.
    def createTable(self, table):
        self.table = table

    # Since I made the links hold the actual devices, instead of just
    # host numbers, the devices will be made separately first,
    # then the links, then the devices will attach the links.

class Host(Device):

    def getLink(self):
        return self.links[0]

    # logs sending packet
    # def logSend

    #processes the receiving packet
    def receiving(self):
        packet = Device.receiving(self, self.getLink())
        if packet.type == "acknowledgment":
            # do nothing
            # decrease the current link rate
            pass
        elif packet.type == "data":
            # send an acknowledgment packet
            # TODO
            pass
        return packet

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
        packet = Packet(self.src, self.dest, DATA_SIZE, "data")
        return packet

    # This method will generate acknowledgment packets for the flow.
    def generateAckPacket(self):
        packet = Packet(self.src, self.dest, ACK_SIZE, "acknowlegment")
        return packet

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
        """

        self.linkID = linkID
        self.rate = rate * MB_TO_KB * KB_TO_B / B_to_b
        self.delay = delay
        self.buffer_size = buffer_size * KB_TO_B
        self.device1 = device1
        self.device1.attachLink(self)
        self.device2 = device2
        self.device2.attachLink(self)

        self.current_buffer_occupancy = 0
        self.current_rate = 0

        self.linkBuffer = bufferQueue()

        
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

        if not self.rateFullWith(packet):
            print "sending..."
            packet.dest.sending(self, packet)

            self.popFromBuffer()
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
        print "popped off buffer!"
        popped_elem = self.linkBuffer.get()
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


    def __init__(self, src, dest, data_size, data_type):
    """ Instatiates a Packet.

    :param src: Source (device) of packet
    :type src: Device
    :param dest: Destination (device) of packet
    :type dest: Device
    :param data_size: data size (in bytes)
    :type data_size: int
    :param data_type: metadata, either ACK or DATA
    :type data_type: str
    """
        self.src = src
        self.dest = dest
        self.data_size = data_size
        self.type = data_type

