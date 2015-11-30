import Queue
import datetime
import time
import constants
import metrics
from classes import *



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

        :param EventHandler: Object associated with event request.
        :type EventHandler: Device, Link, or None

        :param EventType: The type of event that will be sent.
        :type EventType: str

        :param EventTime: The time of the particular event, in milliseconds.
        :type EventTime: int

        EventType               EventHandler        Packet Type
        PUT                     (Link, Device)      DATA, ACK
        SEND                    (Link, Device)      None
        RECEIVE                 Device              DATA, ACK
        GENERATEACK             None                None
        GENERATEPACK            None                None

        """

        self.packet = packet
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

        self.flow = flow

    def __cmp__(self, other):
        """Orders events by (in order of importance):
        1) The event's time.
        2) Which event contains a packet. The event without a packet is
            processed first, since these events are almost instantaneous.
        3) Which event's packetID is smaller. Smaller packetIDs
            were generated first, so process them first.

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
    def __init__(self, network, log):
        """ This will initialize the simulation with a Priority Queue
        that sorts based on time.

        :param network: Network system parsed from json
        :type network : Network

        :param log: Data can be logged in different frequencies.
            if 'less': data is to be logged once per
            LOG_TIME_INTERVAL (roughly average).
            if 'avg': data is to be collected over LOG_TIME_INTERVAL,
            and then averaged for that time interval
            if 'more': data is to be logged whenever relevant
        :type log: str
        """
        self.q = Queue.PriorityQueue()
        self.network = network

        if log:
            self.metrics = metrics.Metrics(log)
            # these constants are just indices
            # for the respective time intervals
            # of the data we want to log
            self.LOG_LINKRATE = 0
            self.LOG_BUFFERSIZE = 1
            self.LOG_PACKETLOSS = 2
            self.LOG_FLOWRATE = 3
            self.LOG_WINDOWSIZE = 4
            self.LOG_PACKETDELAY = 5

    def insertEvent(self, event):
        """ This will insert an event into the Priority Queue.

        :param event: This is the event we're adding into the queue.
        :type event: Event
        """
        self.q.put(event)

    def done(self):
        """ Called when the simulation is finished. If metrics
        were recorded, this closes
        the files that log data for the useful metrics (e.g. link rate),
        so the file ends with EOF.

        """
        if self.metrics:
            self.metrics.done()

    def processEvent(self):
        """Pops and processes event from queue."""

        if(self.q.empty()):
            print "No events in queue."
            return

        event = self.q.get()


        print "\n"
        print "Popped event type:", event.type, "at", event.time, "ms"
        if event.type == "INITIALIZEFLOW":

            event.flow.initializePackets()

            increment = 1
            while(event.flow.window_counter <= floor(event.flow.window_upper)):
                newEvent = Event(None, None, "SELECTPACK", event.time + increment * constants.EPSILON_DELAY, event.flow)
                event.flow.window_counter = event.flow.window_counter + 1
                self.insertEvent(newEvent)
                increment = increment + 1

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

                if self.metrics:
                    # log the size of the buffer. log in the number of packets, and in seconds
                    self.metrics.logMetric(event.time / constants.s_to_ms,
                            link.linkBuffer.occupancy / constants.DATA_SIZE, self.LOG_BUFFERSIZE)

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
                if self.metrics:
                    self.metrics.logMetric(event.time / constants.s_to_ms, 
                            link.currentRateMbps(None), self.LOG_LINKRATE)

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

                    host = event.handler
                    host.receive(event.packet)


                    isDropped = event.flow.receiveAcknowledgement(event.packet)
                    # log the current window size here, since the size
                    # may be updated
                    if self.metrics:
                        self.metrics.logMetric(event.time / constants.s_to_ms, 
                                event.flow.getWindowSize(), self.LOG_WINDOWSIZE)

                    print "HOST EXPECT: " + str(event.flow.window_lower) + \
                          " TIME: " + str(event.time)
                    #  ^ This will update the packet index that it will be
                    #    sending from. Thus, constantly be monitoring

                    # IF SO,
                    #######################################
                    ##### Push in new GENERATEPACKS... ####
                    #######################################


                    if isDropped == False:
                        increment = 1
                        print str(event.flow.packets_index)
                        print str(event.flow.window_upper)
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

            # logs when a new packet is created. This will be used
            # for packet delay
            newPacket.time = event.time

            print "Packet to be sent: " + newPacket.packetID
            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT",
                    event.time, event.flow)
            self.insertEvent(newEvent)

        elif event.type == "RESEND":
            newPacket = event.flow.packets[event.flow.window_lower]

            # Resetting this packet to the original attributes, except
            # the packet's time created.
            newPacket.data_size = constants.DATA_SIZE
            newPacket.type = "DATA"
            newPacket.curr = None
            newPacket.src = event.flow.src
            newPacket.dest = event.flow.dest
            newPacket.time = event.time

            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT",
                    event.time, event.flow)
            self.insertEvent(newEvent)


        elif event.type == "TIMEOUT":
            packetIdx = event.handler
            print "TIMEOUT FOR: " + str(packetIdx)

            isAcked = event.flow.checkIfAcked(packetIdx)

            if isAcked == False:
                newPacket = event.flow.packets[packetIdx]
                # Resetting this packet to the original attributes, except
                # the packet's time created.
                newPacket.data_size = constants.DATA_SIZE
                newPacket.type = "DATA"
                newPacket.curr = None
                newPacket.src = event.flow.src
                newPacket.dest = event.flow.dest
                newPacket.time = event.time

                host = newPacket.src
                link = host.getLink()

                newEvent = Event(newPacket, (link, host), "PUT", event.time , event.flow)
                self.insertEvent(newEvent)
