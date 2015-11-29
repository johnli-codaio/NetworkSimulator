import Queue
import datetime
import time
import constants
from classes import *

# TODO: Need to update simulation's self.last_RTT value

class Event:
    """Events are enqueued into the Simulator priority queue by their time. Events
    have a type (PUT, SEND, RECEIVE, GENERATEACK, GENERATEPACK) describing what is
    done to the packet. Each type of event has an associated network handler
    (Link, Device, Flow, respectively).
    """

    def __init__(self, packet, EventHandler, EventType, EventTime, flow):
        """ This will initialize an event.

        :param packet: The packet associated with the event.
        :type packet: Packet/None (None for GENERATE...)

        :type EventHandler: Device, Link, or None

        :param EventType: The type of event that will be sent.
        :type EventType: str

        :param EventTime: The time of the particular event, in milliseconds.
        :type EventTime: int

        EventType               EventHandler        Packet
        PUT                     (Link, Device)
        SEND                    (Link, Device)      None
        RECEIVE                 Device
        GENERATEACK             None                None
        GENERATEPACK            None                None

        """

        self.packet = packet
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

        self.flow = flow

    def __cmp__(self, other):
        """Ordering by time.

        :param other: The other event we're comparing with.
        :type other: Event
        """
        if self.time != other.time:
            return cmp(self.time, other.time)
        else:
            if self.packet is None and other.packet is None:
                return 0
            elif self.packet is None:
                return -1
            elif other.packet is None:
                return 1
            elif len(other.packet.packetID) != len(self.packet.packetID):
                return cmp(len(self.packet.packetID), len(other.packet.packetID))
            else:
                return cmp(self.packet.packetID, other.packet.packetID)



class Simulator:
    # TODO
    def __init__(self, network):
        """ This will initialize the simulation with a Priority Queue
        that sorts based on time.

        :param network: Network system parsed from json
        :type network : Network
        """
        self.q = Queue.PriorityQueue()
        self.network = network

        # file for logging
        # the current link rate
        self.linkRateLog = open('linkRateLog.txt', 'w')

        # the current buffer occupancy
        self.bufferLog = open('bufferLog.txt', 'w')

        # the current packet loss
        self.packetLog = open('packetLog.txt', 'w')

        # the current flow rate
        self.flowRateLog = open('flowRateLog.txt', 'w')

        # the current window size
        self.windowLog = open('windowLog.txt', 'w')

        # the current packet delay
        self.delayLog = open('delayLog.txt', 'w')

        self.counter = 0

        #keeps track of the first time a packet is acknowledged
        self.first_time = 0

    def insertEvent(self, event):
        """ This will insert an event into the Priority Queue.

        :param event: This is the event we're adding into the queue.
        :type event: Event
        """
        self.q.put(event)

    def done(self):
        self.linkRateLog.close()
        self.bufferLog.close()
        self.packetLog.close()
        self.flowRateLog.close()
        self.windowLog.close()
        self.delayLog.close()

    def processEvent(self, tcp_type):
        """Pops and processes event from queue.

        :param tcp_type: This tells us which tcp to use, 0 for Reno, 1 for fast.
        :type tcp_type: Integer
        """

        if(self.q.empty()):
            print "No events in queue."
            return

        event = self.q.get()


        print "\n"
        print "Popped event type:", event.type, "at", event.time, "ms"


        if event.type == "INITIALIZEFLOW":

            event.flow.initializePackets()

            increment = 1
            print "event.flow.window_upper: " + str(event.flow.window_upper)
            while(event.flow.window_counter <= floor(event.flow.window_upper)):
                newEvent = Event(None, None, "SELECTPACK", event.time + increment * constants.EPSILON_DELAY, event.flow)
                event.flow.window_counter = event.flow.window_counter + 1
                self.insertEvent(newEvent)
                increment = increment + 1

        
        elif event.type == "UPDATEWINDOW":
            event.flow.TCPFast(40, 0)
            print "tcp fast happened here"
            newEvent2 = Event(None, None, "UPDATEWINDOW", event.time + 20, event.flow)
            #could be an infinite loop here?
            # maybe instead do:
            #if self.p.size() == 1:
            if not self.q.empty():
                self.insertEvent(newEvent2)

        elif event.type == "PUT":
            # Tries to put packet into link buffer
            # This happens whenever a device receives a packet.

            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]

            print event.packet.type, event.packet.packetID

            # is the buffer full? you can put a packet in
            if not link.linkBuffer.bufferFullWith(event.packet):
                device.sendToLink(link, event.packet)
                newEvent = Event(None, (link, device), "SEND", event.time, event.flow)
                self.insertEvent(newEvent)
            else: # packet dropped!!
                print "Packet ", event.packet.packetID, " dropped"

        elif event.type == "SEND":
            # Processes a link to send.
            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]


            # If you can send the packet, we check what buffer is currently in action.
            # If dev1->dev2, then we pop from device 1.
            # Else, we pop from device 2.
            # If we can't pop from the
            # link's buffer, then we call another send event 1 ms later.

            packet = link.sendPacket(device)
            if packet:
                if(device == link.device1):
                    newEvent = Event(packet, link.device2, "RECEIVE", event.time +
                                     link.delay, event.flow)
                    self.insertEvent(newEvent)
                else:
                    newEvent = Event(packet, link.device1, "RECEIVE", event.time +
                                     link.delay, event.flow)
                    self.insertEvent(newEvent)

                # log the link rate. Log these in seconds, and in Mbps
                self.linkRateLog.write(str(event.time / constants.s_to_ms)
                        + " " + str(link.currentRateMbps(None)) + "\n")

            else:
                print "LINK FULL: Packet " + link.linkBuffer.peek().packetID + \
                      " Window Size " + str(event.flow.window_size)
                newEvent = Event(None, (link, device), "SEND",
                        event.time + constants.QUEUE_DELAY, event.flow)
                self.insertEvent(newEvent)

        elif event.type == "RECEIVE":
            # Processes a host/router action that would receive things.
            assert(isinstance(event.handler, Device))

            # Router.
            if isinstance(event.handler, Router):
                router = event.handler
                newLink = router.transfer(event.packet)

                newEvent = Event(event.packet, (newLink, router), "PUT",
                        event.time, event.flow)
                self.insertEvent(newEvent)

            # Host

            elif isinstance(event.handler, Host):
                if(event.packet.type == "DATA"):
                    host = event.handler
                    host.receive(event.packet)

                    newEvent = Event(event.packet, None, "GENERATEACK",
                            event.time + constants.EPSILON_DELAY, event.flow)
                    self.insertEvent(newEvent)
                else:
                    ########################################
                    ####### TODO: Acknowledgement got ######
                    ########################################

                    # If an acknowledgment is received, we check it through
                    # the receiveAcknowledgment method.
                    host = event.handler
                    host.receive(event.packet)

                    # If the packet is dropped (more than three errors in the error counter)
                    # then this bool is true. Else, it's false.

                    isDropped = event.flow.receiveAcknowledgement(event.packet, event.time, tcp_type)
                    print "HOST EXPECT: " + str(event.flow.window_lower) + \
                          " TIME: " + str(event.time)
                    #  ^ This will update the packet index that it will be
                    #    sending from. Thus, constantly be monitoring

                    # IF SO,
                    #######################################
                    ##### Push in new GENERATEPACKS... ####
                    #######################################

                    
                    # If the packet was dropped, we will do SELECTIVE RESEND (Fast retransmit)
                    # and only resend the dropped packet. Otherwise, we send packets based on the
                    # updated window parameters (done in TCP Reno).
                    if isDropped == False:

                        if self.first_time == 0:
                            # TCP Fast initialization event, which should happen only the first time a packet is acknowledged
                            if tcp_type == 1:
                                newEvent2 = Event(None, None, "UPDATEWINDOW", event.time + 20, event.flow)
                                self.insertEvent(newEvent2)
                            self.first_time = 1

                        increment = 1
                        print "event.flow.packets_index: " + str(event.flow.packets_index)
                        print "event.flow.window_upper: " + str(event.flow.window_upper)
                        while(event.flow.window_counter <= event.flow.window_upper):
                            print str(event.flow.packets_index)
                            newEvent = Event(None, None, "SELECTPACK", event.time + increment * constants.EPSILON_DELAY, event.flow)
                            timeoutEvent = Event(None, event.flow.window_counter, "TIMEOUT", event.time + constants.TIME_DELAY + increment * constants.EPSILON_DELAY, event.flow)
                            self.insertEvent(newEvent)
                            self.insertEvent(timeoutEvent)
                            event.flow.window_counter = event.flow.window_counter + 1
                            increment = increment + 1

                    else:
                        newEvent = Event(None, None, "RESEND", event.time + constants.EPSILON_DELAY, event.flow)
                        self.insertEvent(newEvent)
                        timeoutEvent = Event(None, event.flow.window_lower, "TIMEOUT", event.time + constants.TIME_DELAY + constants.EPSILON_DELAY, event.flow)
                        self.insertEvent(timeoutEvent)



        elif event.type == "GENERATEACK":
            # Processes a flow to generate an ACK.

            # Generate the new Ack Packet
            ackPacket = event.flow.generateAckPacket(event.packet)
            host = ackPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(ackPacket, (link, host), "PUT",
                    event.time, event.flow)
            self.insertEvent(newEvent)


        elif event.type == "SELECTPACK":
            # Processes a flow to generate a regular data packet.

            # Generate the new packet.
            newPacket = event.flow.selectDataPacket()
            if(newPacket == None):
                return

            # Setting the "sent time" for the packet.
            newPacket.start_time = event.time

            print "Packet to be sent: " + newPacket.packetID
            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT",
                    event.time, event.flow)
            self.insertEvent(newEvent)

        # In the case of dropped packets, this will start. 
        # We are only resending the dropped packet.
        elif event.type == "RESEND":
            newPacket = event.flow.packets[event.flow.window_lower]

            # Resetting this packet to the original attributes;
            # They may have been changed on its trip before
            # it was dropped.
            newPacket.start_time = event.time
            newPacket.total_delay = 0
            newPacket.data_size = constants.DATA_SIZE 
            newPacket.type = "DATA"
            newPacket.curr = None
            newPacket.src = event.flow.src
            newPacket.dest = event.flow.dest

            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT",
                    event.time, event.flow)
            self.insertEvent(newEvent)

        # This is the last resort option to detect dropped packets.
        # If an acknowledgment hasn't been received for a long time
        # then we will resend that packet only.
        # This event will be put into the queue every time a data
        # packet is selected to be sent.
        elif event.type == "TIMEOUT":
            packetIdx = event.handler
            print "TIMEOUT FOR: " + str(packetIdx)

            isAcked = event.flow.checkIfAcked(packetIdx)

            if isAcked == False:
                # A packet is dropped. We do the appropriate TCP window size
                # update.

                if tcp_type == 0:
                    event.flow.TCPReno(False)
                
                # IMPORTANT: TODO: TODO: How do we call TCPFast if a packet is dropped?? I don't think we can.
                elif tcp_type == 1:
                    #use 1 for bypass, just called to update window bounds accordingly
                    event.flow.TCPFast(40, 1)
                
                else:
                    raise Exception('Wrong input for tcp_type!!')

                # Selecting the packet that has been timed out.
                newPacket = event.flow.packets[packetIdx]

                # Resetting this packet to the original attributes;
                # These attributes might have been altered before it
                # was dropped.
                newPacket.start_time = event.time
                newPacket.total_delay = 0
                newPacket.data_size = constants.DATA_SIZE 
                newPacket.type = "DATA"
                newPacket.curr = None
                newPacket.src = event.flow.src
                newPacket.dest = event.flow.dest

                host = newPacket.src
                link = host.getLink()

                newEvent = Event(newPacket, (link, host), "PUT", event.time , event.flow)
                self.insertEvent(newEvent)
