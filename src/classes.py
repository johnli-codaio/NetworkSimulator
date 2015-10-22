#TODO: Add some stuff to the classes...
import Queue

class Device:

    # Instantiating the Device.
    # Arguments:
    #   address : Indicates the name/address of the device.

    def __init__(self, address):
        self.address = address

class Router(Device):
    # This is the routing table for the router, though there isn't
    # much in it yet since we calculate that later.
    table = None

    # The list of links is also empty. We will update this with
    # a list of created links.
    links = None

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
    link = None

    # Instantiating the Host, inherits from Device
    # Arguments:
    #   address : Indicates the name/address of that host.
    #   link : The link that the host is connected to.

    def __init__(self, address):
        Device.__init__(self, address)

    def attachLink(self, link):
        self.link = link


class Flow:

    # Instantiating a Flow
    # Arguments:
    #   flowId : Indicates what flow we are referencing.
    #   src : Address of the source of the flow.
    #   dest : Address of the destination of the flow
    #   sendtime : Time that a packet is being sent.

    def __init__(self, flowId, src, dest, sendTime):
        self.flowId = flowId
        self.src = src
        self.dest = dest
        self.sendTime = sendTime

    # This method will generate packets for the flow.
    def generatePacket(self, data):
        packet = Packet(self.src, self.dest, data)
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
        self.linkBuffer = Queue.Queue(buffer_size)
        self.device1 = device1
        self.device2 = device2

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
        self.linkBuffer.put(packet)

class Packet:

    # Instantiating a Packet
    # Arguments:
    #   src : Indicates the source of the sending
    #   dest : Indicates the destination of the sending
    #   data : Either some of the data, or an acknowledgment

    def __init__(self, src, dest, data):
        self.src = src
        self.dest = dest
        self.data = data
		