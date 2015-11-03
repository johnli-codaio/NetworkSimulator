#TODO: Add some stuff to the classes...
import Queue

# four conversion constants:
#   KB_TO_B: converts kilobytes to bytes.
#   B_to_b: converts bytes to bits
#   MB_TO_KB: converts megabytes to kilobytes
#   s_to_ms: converts seconds to milliseconds
KB_TO_B = 1000
B_to_b = 8
MB_TO_KB = 1000
s_to_ms = 1000

# some static constants:
#   DATA_SIZE: the size of a data packet (1024B)
#   ACK_SIZE: the size of an acknowledgment packet (64B)
DATA_SIZE = 1024
ACK_SIZE = 64

class Device:

    # Instantiating the Device.
    # Arguments:
    #   address : Indicates the name/address of the device.
    def __init__(self, address):
        self.address = address
        self.links = []

    def attachLink(linkz):
        # should be a for loop
        for link in linkz:
            self.links.append(link)

class Router(Device):
    # Instantiating the Router, inherits from Device
    # Arguments:
    #   address : Indicates the name/address of the router.
    #   links : A list of all the links that the router is attached to.

    def __init__(self, address):
        Device.__init__(self, address)

    # This will set a created routing table into the router's table.
    # The table will be decided using Bellman Ford.
    def createTable(self, table):
        self.table = table

    # Since I made the links hold the actual devices, instead of just
    # host numbers, the devices will be made separately first,
    # then the links, then the devices will attach the links.
    def attachLinks(self, links):
        self.links = links

class Host(Device):
    # At first, since we make all the devices first, then
    # the links, and then we will then attach that link to the
    # proper host.

    # Instantiating the Host, inherits from Device
    # Arguments:
    #   address : Indicates the name/address of that host.
    #   link : The link that the host is connected to.
    def __init__(self, address):
        Device.__init__(self, address)

    def attachLink(self, link):
        Device.attachLink(link)

    # logs sending packet
    # def logSend

    #logs receiving packet
    # def logReceive


class Flow:

    # Instantiating a Flow
    # Arguments:
    #   flowId : Indicates what flow we are referencing.
    #   src : Address of the source of the flow.
    #   dest : Address of the destination of the flow

    def __init__(self, flowId, src, dest):
        self.flowId = flowId
        self.src = src
        self.dest = dest
        # self.sendTime = sendTime

    # This method will generate data packets for the flow.
    def generateDataPacket(self):
        packet = Packet(self.src, self.dest, DATA_SIZE, "data")
        return packet

    # This method will generate acknowledgment packets for the flow.
    def generateAckPacket(self):
        packet = Packet(self.src, self.dest, ACK_SIZE, "data")
        return packet


class Link:

    # Instantiating a Link
    # Arguments:
    #   linkId : Indicates what link we're referencing
    #   rate : Indicates how fast packets are being sent
    #   delay : How much delay there is for packet to arrive to destination
    #           (Do we need this?)
    #
    #   buffer_size : Size of buffer. We crate the buffer
    #                 from the Python queue library.
    #   device1: One device connected to the link
    #   device2: The other device connected to the link

    def __init__(self, linkId, rate, delay, buffer_size, device1, device2):
        self.linkId = linkId
        self.rate = rate
        self.delay = delay
        self.buffer_size = buffer_size

        # initially, the queue has no packets in it.
        self.current_buffer = 0

        self.linkBuffer = Queue.Queue()
        self.device1 = device1
        self.device2 = device2

    # the rate is given in Mbps. We have to convert that to bytes per sec
    # so we know many packets (given in bytes) can fit into that rate
    def rateInBytes(self, rate):
        return self.rate / B_to_b * MB_TO_KB * KB_TO_B;

    # since the buffer_size is in KB, and packets are in bytes,
    # just convert buffer_size into bytes as well
    def bufferInBytes(self, buffer_size):
        return buffer_size * KB_TO_B;


    # is the buffer full, if we add the new packet?
    # we just check if the current data in the buffer and the to-be-added
    # packet will exceed the buffer capacity
    def isFullWith(self, added_packet):
        return (self.buffer_size >
            self.current_buffer + added_packet.data_size)

    # Method to calculate round trip time
    # (TBH, links themselves manage delay? I thought that was something
    #  we calculate...)
    def roundTripTime(self,rate, delay):
        #TODO
        pass

    # This will pop off a packet from the linked buffer. I will then return
    # it so that it could be sent.
    def popFromBuffer(self):
        popped_elem = self.linkBuffer.get()
        return popped_elem

    # This will put in a packet into the queue.
    def putIntoBuffer(self, packet):
        if not self.isFullWith(packet):
            self.linkBuffer.put(packet)
            self.buffer_size += packet.data_size
            return True
        return False

class Packet:

    # Instantiating a Packet
    # Arguments:
    #   src : Indicates the source of the sending
    #   dest : Indicates the destination of the sending
    #   type : Either an actual data packet, or an acknowledgment packet
    #   We shouldn't really care about what is actually is in the data
    #   data_size : pretty straightforward
    def __init__(self, src, dest, data_size, type):
        self.src = src
        self.dest = dest
        self.data_size = data_size
        self.type = type

