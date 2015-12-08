import Queue
import datetime
import time
import constants
import metrics
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

        # return cmp(self.time, other.time)

        if(isinstance(self.packet, RoutingPacket)):
            return cmp(self.time, other.time)

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
    def __init__(self, network, TCP_type, metric):
        """ This will initialize the simulation with a Priority Queue
        that sorts based on time.

        :param network: Network system parsed from json
        :type network : Network

        :param TCP_type: Which TCP congestion control to use.
        :type TCP_type : str

        :param metric: The class responsible for logging all metrics.
            Can be None, if no data is to be logged.
        :type metric: Metrics
        """
        self.q = Queue.PriorityQueue()
        self.network = network
        self.tcp_type = TCP_type



        self.metrics = metric
        # these constants are just indices
        # for the respective time intervals
        # of the data we want to log
        self.LOG_LINKRATE = 0
        self.LOG_BUFFERSIZE = 1
        self.LOG_PACKETLOSS = 2
        self.LOG_FLOWRATE = 0
        self.LOG_WINDOWSIZE = 1
        self.LOG_PACKETDELAY = 2

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

    def logData(self, time):
        for link_name in self.network.links:
            link = self.network.links[link_name]
            # log the size of the buffer. log in the number of packets, and in seconds
            self.metrics.logMetric(time / constants.s_to_ms,
                    link.linkBuffer.occupancy / constants.DATA_SIZE,
                    self.LOG_BUFFERSIZE, link.linkID)
            # log that a single packet has been dropped
            self.metrics.logMetric(time / constants.s_to_ms,
                    link.droppedPacket(), self.LOG_PACKETLOSS, link.linkID)
            # log the link rate. Log these in seconds, and in Mbps
            self.metrics.logMetric(time / constants.s_to_ms,
                    link.currentRateMbps(None),
                    self.LOG_LINKRATE, link.linkID)
        for flow_name in self.network.flows:
            flow = self.network.flows[flow_name]
            # log the current window size here, since the size
            # may be updated
            self.metrics.logMetric(time / constants.s_to_ms,
                    flow.getWindowSize(),
                    self.LOG_WINDOWSIZE, flow.flowID)
            # this is a packet delay, so log it
            self.metrics.logMetric(time / constants.s_to_ms,
                    flow.packet_delay,
                    self.LOG_PACKETDELAY, flow.flowID)
            # I think flow rate is really just the rate of the link
            # that is attached to the source of the flow. So
            # log the flow rate here.
            rate = flow.src.getLink().currentRateMbps(None)
            self.metrics.logMetric(time / constants.s_to_ms,
                    rate, self.LOG_FLOWRATE, flow.flowID)

    def processEvent(self):
        """Pops and processes event from queue."""

        if(self.q.empty()):
            result += "No events in queue."
            return

        event = self.q.get()

        # outputs what's happening as
        # we process events, if we want to have a verbose output
        result = ""

        result += "Popped event type: " \
                + str(event.type) + " at " +  str(event.time) + " ms\n"

        if event.type == "INITIALIZEFLOW":

            event.flow.initializePackets()

            increment = 1
            result += "event.flow.window_upper: " + str(event.flow.window_upper)
            result += "\n"
            while(event.flow.window_counter <= floor(event.flow.window_upper)):
                newEvent = Event(None, None, "SELECTPACK", event.time + increment * constants.EPSILON_DELAY, event.flow)
                event.flow.window_counter = event.flow.window_counter + 1
                self.insertEvent(newEvent)
                increment = increment + 1

        elif event.type == "REROUT":
            result += "Initializing REROUT at time " + str(event.time) + "\n"

            result += "CURRENT TABLES: \n"
            for deviceID in self.network.devices:
                if(isinstance(self.network.devices[deviceID], Router)):
                    result += str(self.network.devices[deviceID])

            for deviceID in self.network.devices:
                device = self.network.devices[deviceID]
                if(isinstance(device, Router)):
                    device.initializeRerout()

                    # Find what routing packets to send
                    routingPackets = device.floodNeighbors(dynamic = True)

                    for (pack, link) in routingPackets:
                        newEvent3 = Event(pack, (link, device), "PUT",
                                    event.time + constants.EPSILON_DELAY,
                                    flow = None)
                        self.insertEvent(newEvent3)

            if(not self.network.allFlowsComplete()):
                newEvent2 = Event(None, None, "REROUT",
                    event.time + constants.REROUT_TIME, None)
                self.insertEvent(newEvent2)


        elif event.type == "UPDATEWINDOW":
            #if no new packets were receieved between now and last
            #updatewindow, we have to make our RTT higher
            #(before, it was left as the last rtt received, which was deceiving)
            if event.flow.received_packet == False:
                result += "last_receieved_packet: " + str(event.flow.last_received_packet_start_time)
                #figure out the appropriate value
                event.flow.actualRTT = event.time - event.flow.last_received_packet_start_time


            event.flow.TCPFast(20)
            result += "tcp fast happened here\n"

            #reset the max RTT

            event.flow.actualRTT = event.flow.theoRTT

            #reset the received packet
            event.flow.received_packet = False

            # Add next updatewindow to queue
            if not event.flow.flowComplete():
                newEvent2 = Event(None, None, "UPDATEWINDOW", event.time + 20, event.flow)
                self.insertEvent(newEvent2)

        elif event.type == "PUT":
            # Tries to put packet into link buffer
            # This happens whenever a device receives a packet.
            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]

            result += str(event.packet.data_type) + " " + str(event.packet.packetID) + "\n"

            result += "Putting " + event.packet.data_type + str(event.packet.packetID) + " into link " + str(link.linkID) + \
                  " from Device " + str(device.deviceID) + " at time " + str(event.time) + str(event.flow) + "\n"


            # is the buffer full? you can put a packet in
            result +=  "Link " + str(link.linkID) + " with buffer size " + str(link.linkBuffer.occupancy) + "\n"
            if not link.linkBuffer.bufferFullWith(event.packet):
                device.sendToLink(link, event.packet)

                # a packet hasn't been dropped
                newEvent = Event(None, link, "SEND", event.time, event.flow)
                self.insertEvent(newEvent)
            else: # packet dropped!!
                link.isDropped = True
                result += "Packet " + str(event.packet.packetID) + " dropped"\
                        " at time " + str(event.time) + " by " + str(link) + "\n"


        elif event.type == "SEND":
            # Processes a link to send.
            assert(isinstance(event.handler, Link))
            link = event.handler


            # If you can send the packet, we check what buffer is currently in action.
            # If dev1->dev2, then we pop from device 1.
            # Else, we pop from device 2.
            # If we can't pop from the
            # link's buffer, then we call another send event 1 ms later.

            # If there is an empty buffer...
            if len(link.linkBuffer.packets) != 0:
                packet = link.sendPacket()
                # it's possible that there's a mismatch between
                # a sending event and the appropriate type of packet.
                # so check the packet's ID to see if originally
                # had a flow

                if(packet != None):
                    packetflowID = packet.recallFlowID()
                    for flow_name in self.network.flows:
                        if flow_name == packetflowID:
                            event.flow = self.network.flows[flow_name]
                    # propagation time.
                    propagationTime = (float(packet.data_size * constants.B_to_b) / (constants.KB_TO_B * constants.MB_TO_KB)) / link.maxRate

                    otherDev = packet.nextDev
                    result += "Sending " + packet.data_type + str(packet.packetID) + " into link " + str(link.linkID) + \
                      " to Device " + str(otherDev.deviceID) + " with destination " + str(packet.dest.deviceID) + " at time " + str(event.time) + str(event.flow)
                    newEvent = Event(packet, otherDev, "RECEIVE",
                                     event.time + propagationTime + link.delay, event.flow)
                    self.insertEvent(newEvent)



             #   else:

             #       result += "LINK " + str(link.linkID) + " FULL: Packet " + link.linkBuffer.peek().data_type + link.linkBuffer.peek().packetID + \
             #             " Window Size " + str(event.flow.window_size) + " from " + link.linkBuffer.peek().currDev.deviceID + " with destination " + str(link.linkBuffer.peek().dest.deviceID) + " at time " + str(event.time)
             #       newEvent = Event(None, link, "SEND",
             #               event.time + constants.QUEUE_DELAY, event.flow)
             #       self.insertEvent(newEvent)
             # else:
             #   result += "LINK " + str(link.linkID) + " BUFFER EMPTY:" + \
             #             " Window Size " + str(event.flow.window_size) '''

        elif event.type == "RECEIVE":

            # Processes a host/router action that would receive things.
            assert(isinstance(event.handler, Device))
            sendLink = event.packet.currLink

            # Router receives packet
            if isinstance(event.handler, Router):
                router = event.handler

                if(isinstance(event.packet, RoutingPacket)):
                    result += "Handling RoutingPacket at time " + str(event.time)

                    _continue = router.handleRoutingPacket(event.packet)
                    if(_continue):
                        # flood neighbors
                        newPackets = router.floodNeighbors()

                        for (pack, link) in newPackets:
                            newEvent = Event(pack, (link, router),
                                             "PUT", event.time,
                                             flow = None)
                            self.insertEvent(newEvent)

                elif(isinstance(event.packet, DataPacket)):

                    result += "Receiving " + event.packet.data_type + str(event.packet.packetID) + " to Router " + str(router.deviceID) + " at time " + str(event.time) + str(event.flow)

                    newLink = router.transferTo(event.packet)

                    newEvent = Event(event.packet, (newLink, router), "PUT",
                            event.time, event.flow)
                    self.insertEvent(newEvent)


            # Host receives packet
            elif isinstance(event.handler, Host):
                if(event.packet.data_type == "DATA"):
                    host = event.handler
                    host.receive(event.packet)

                    result += "Receiving " + event.packet.data_type + str(event.packet.packetID) + " to Host " + str(host.deviceID) + " at time " + str(event.time)

                    newEvent = Event(event.packet, None, "GENERATEACK",
                            event.time, event.flow)
                    self.insertEvent(newEvent)
                elif(event.packet.data_type == "ACK"):
                    host = event.handler
                    host.receive(event.packet)

                    result += "Receiving " + event.packet.data_type + str(event.packet.packetID) + " to Host " + str(host.deviceID) + " at time " + str(event.time)

                    isDropped = event.flow.receiveAcknowledgement(event.packet, event.time, self.tcp_type)
                    event.flow.packet_delay = event.time - event.packet.start_time


                    result += "HOST EXPECT: " + str(event.flow.window_lower) + \
                          " TIME: " + str(event.time) + "\n"
                    result += "Host received: " + str(event.packet.packetID)
                    result += "currentTime: " + str(event.time)
                    result += "packet.start_time: " + str(event.packet.start_time)
                    result += "self.actual-RTT: " + str(event.flow.actualRTT)
                    #  ^ This will update the packet index that it will be
                    #    sending from. Thus, constantly be monitoring

                    # IF SO,
                    ####################################### ????
                    ##### Push in new GENERATEPACKS... #### ???? is this done?
                    ####################################### ????

                    # If the packet was dropped, we will do SELECTIVE RESEND (Fast retransmit)
                    # and only resend the dropped packet. Otherwise, we send packets based on the
                    # updated window parameters (done in TCP Reno).
                    if isDropped == False:
                        result += "ACK Packet " + str(event.packet.packetID) + "acknowledged."


                        if event.flow.first_time == 0:
                            # TCP Fast initialization event, which should happen only the first time a packet is acknowledged
                            if self.tcp_type == 'FAST':
                                newEvent2 = Event(None, None, "UPDATEWINDOW", event.time + (2*event.flow.actualRTT), event.flow)
                                self.insertEvent(newEvent2)
                            event.flow.first_time = 1

                        increment = 1
                        result += "event.flow.packets_index: " + str(event.flow.packets_index) + "\n"
                        result += "event.flow.window_upper: " + str(event.flow.window_upper) + "\n"
                        while(event.flow.window_counter <= event.flow.window_upper):
                            result += str(event.flow.packets_index) + "\n"
                            newEvent = Event(None, None, "SELECTPACK", event.time + increment * constants.EPSILON_DELAY, event.flow)
                            timeoutEvent = Event(None, event.flow.window_counter, "TIMEOUT", event.time + constants.TIME_DELAY + increment * constants.EPSILON_DELAY, event.flow)
                            self.insertEvent(newEvent)
                            self.insertEvent(timeoutEvent)
                            event.flow.window_counter = event.flow.window_counter + 1
                            increment = increment + 1

                    else:
                        result += "DROPPED PACKET " + str(event.flow.packets[event.flow.window_lower].packetID)

                        newEvent = Event(None, None, "RESEND", event.time + constants.EPSILON_DELAY, event.flow)
                        self.insertEvent(newEvent)
                        timeoutEvent = Event(None, event.flow.window_lower, "TIMEOUT", event.time + constants.TIME_DELAY + constants.EPSILON_DELAY, event.flow)
                        self.insertEvent(timeoutEvent)
                    result += "Window counter: " + str(event.flow.window_counter)
                    result += "Window size: " + str(event.flow.flowID) + " " + str(event.flow.window_size)
                    result += "Window Upper: " + str(event.flow.window_upper)

            # Inserting another send event...
            newSendEvent = Event(None, sendLink, "SEND", event.time, event.flow)
            self.insertEvent(newSendEvent)


        elif event.type == "GENERATEACK":
            # Processes a flow to generate an ACK.

            # Generate the new Ack Packet
            result += event.packet.packetID

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


            result += "Packet to be sent: " + str(newPacket.data_type) + newPacket.packetID + " at time " + str(event.time)
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

            result += "Resending: " + str(newPacket.data_type) + str(newPacket.packetID) + " at time " + str(event.time)
            # Resetting this packet to the original attributes;
            # They may have been changed on its trip before
            # it was dropped.
            newPacket.start_time = event.time
            newPacket.total_delay = 0
            newPacket.data_size = constants.DATA_SIZE
            newPacket.data_type = "DATA"
            newPacket.currLink = None
            newPacket.currDev = None
            newPacket.nextDev = None
            newPacket.src = event.flow.src
            newPacket.dest = event.flow.dest
            newPacket.time = event.time

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
            result += "TIMEOUT FOR: " + str(packetIdx) + "\n"

            isAcked = event.flow.checkIfAcked(packetIdx)

            if isAcked == False:
                # A packet is dropped. We do the appropriate TCP window size
                # update.

                if self.tcp_type == 'Reno':
                    event.flow.TCPReno(False)
                    event.flow.timeOut()

                # Selecting the packet that has been timed out.
                newPacket = event.flow.packets[packetIdx]

                # Resetting this packet to the original attributes;
                # These attributes might have been altered before it
                # was dropped.
                newPacket.start_time = event.time
                newPacket.total_delay = 0
                newPacket.data_size = constants.DATA_SIZE
                newPacket.data_type = "DATA"
                newPacket.currLink = None
                newPacket.currDev = event.flow.src
                newPacket.nextDev = None
                newPacket.src = event.flow.src
                newPacket.dest = event.flow.dest
                newPacket.time = event.time

                host = newPacket.src
                link = host.getLink()

                newEvent = Event(newPacket, (link, host), "PUT", event.time , event.flow)
                self.insertEvent(newEvent)
        # log all data, every time an event is done being processed.
        if self.metrics:
            self.logData(event.time)
        return result


    def staticRouting(self):
        result = ""
        result += "Generating routing tables"

        for device in self.network.devices:
            result += str(device)
            device = self.network.devices[device]
            if(isinstance(device, Router)):
                device.initializeNeighborsTable()

                # Find what routing packets to send
                routingPackets = device.floodNeighbors()

                for pack, link in routingPackets:
                    newEvent = Event(pack, (link, device), "PUT", 0, flow = None)
                    self.insertEvent(newEvent)
        return result

