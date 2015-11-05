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

        # We have two buffers on the link, one for each side.
        # The current packet location is the temporary "Source"; 
        # if it is equal to the device 2 of the link, then the direction
        # is going from dev2->dev1 (so it's in buffer 2). Else, it will
        # be moving from dev1->dev2 (so it's in buffer 1).
        try:
            if packet.curr == link.device2:
                link.dev1todev2 = False
                link.linkBuffer2.put(packet)

            elif packet.curr == link.device1:
                link.dev1todev2 = True
                link.linkBuffer1.put(packet)

            # Update the location of the packet to the corresponding link.
            packet.updateLoc(link)

        except BufferError as e:
            print e

class Router(Device):

    def createTable(self, table):
        """Compute routing table via Bellman Ford.

        :param table: Routing table for the router
        :type Table: dict<(Device, Link)>
        """
        return table

    def transfer(self, packet):
        """ Instantaneous transfer from receiving a packet to sending a packet.

        :param packet: packet that will be transferred
        :type packet: Packet
        """
        prevLink = packet.curr
        prevLink.decrRate(packet)

        nextLink = table[packet.dest]
        packet.curr = self
        Device.sendToLink(self, nextLink, packet)

class Host(Device):

    def getLink(self):
        """ Will return the link attached to the host.
        """
        return self.links[0]


    def receive(self, packet):
        """ Will receive a packet and do two things:
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
            pass

        # What we can do:
        # We will send an acknowledgement from event handler:
        # IF packet.curr = packet.dest and packet.type = "DATA"
        packet.curr = self
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


    def generateDataPacket(self):
        """ This will produce aa data packet, heading the forward
        direction
        """
        packet = Packet(self.src, self.dest, DATA_SIZE, "DATA", self.src)
        return packet

    def generateAckPacket(self):
        """ This will produce an acknowledgment packet, heading the reverse
        direction
        """
        packet = Packet(self.dest, self.src, ACK_SIZE, "ACK", self.dest)
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

        self.current_rate = 0

        self.linkBuffer1 = bufferQueue(buffer_size * KB_TO_B)
        self.linkBuffer2 = bufferQueue(buffer_size * KB_TO_B)

        self.dev1todev2 = None

    def rateFullWith(self, packet):
        """Returns True if packet cannot be sent, False otherwise."""
        return (self.rate < self.current_rate + packet.data_size)

    def sendPacket(self):
        """Sends next packet in queue along link.

        Pops packet from queue, increase current link rate, modifies ...
        """

        try:
            if link.dev1todev2:
                packet = self.linkBuffer1.peek()
                if not self.rateFullWith(packet):
                    print "Sending a packet: dev1 -> dev2"
                    packet = self.linkBuffer1.get()
                    link.incrRate(packet)

            elif link.dev1todev2 == False:
                packet = self.linkBuffer2.peek()
                if not self.rateFullWith(packet):
                    print "Sending a packet: dev2 -> dev1"
                    packet = self.linkBuffer2.get()
                    link.incrRate(packet)

            # The destination for this packet will be found in the link
            # information; the boolean will give hints to the destination.
            # This destination will be the device that calls the receive event.
            return packet

        except BufferError as e:
            print e

        # If you cannot send, then don't return anything and wait.
        # We'll just send another SEND event.
        return None

    def decrRate(self, packet):
        """Decrease current rate by packet size."""
        self.current_rate -= packet.data_size

    def incrRate(self, packet):
        """Increase current rate by packet size."""
        self.current_rate += packet.data_size
            

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

