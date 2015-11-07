import Queue
import datetime
import time
from classes import *


class Event:
    """Events are enqueued into the Simulator priority queue by their time. Events
    have a type (PUT, SEND, RECEIVE, GENERATEACK, GENERATEPACK) describing what is 
    done to the packet. Each type of event has an associated network handler 
    (Link, Device, Flow, respectively).
    """

    def __init__(self, packet, EventHandler, EventType, EventTime, FlowID):
        """ This will initialize an event.

        :param packet: The packet associated with the event.
        :type packet: Packet/None (None for GENERATE...)

        :param EventHandler: Object associated with event request.
        :type EventHandler: Device, Link, or None

        :param EventType: The type of event that will be sent.
        :type EventType: str

        :param EventTime: The time of the particular event, in milliseconds.
        :type EventTime: int

        EventType               EventHandler        Packet
        PUT                     (Link, Device)
        SEND                    (Link, Device)      None
        RECEIVE                 (Device)
        GENERATEACK             (None)              None
        GENERATEPACK            (None)              None

        """

        self.packet = packet
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

        self.flow = flowID

    def __cmp__(self, other):
        """Ordering by time.

        :param other: The other event we're comparing with.
        :type other: Event
        """
        return cmp(self.time, other.time)


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

    def insertEvent(self, event):
        """ This will insert an event into the Priority Queue.

        :param event: This is the event we're adding into the queue.
        :type event: Event
        """
        self.q.push(event)

    def processEvent(self):
        """Pops and processes event from queue."""

        if(self.q.empty()):
            print "No events in queue."
            return

        event = self.q.pop()

        print event.type
        if event.type == "PUT":
            # Tries to put packet into link buffer
            # This happens whenever a device receives a packet.

            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]

            if not link.rateFullWith(event.packet):
                host.sendToLink(link, event.packet)
                newEvent = Event(None, (link, device), "SEND", event.time, event.flow)
                self.insertEvent(newEvent)

        elif event.type == "SEND":
            # Processes a link to send.
            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]
            
            # If you can send the packet, we check what buffer is currently in action.
            # If dev1->dev2, then we pop from device 1.
            # Else, we pop from device 2.
            # If we can't pop, then we call another send event 1 ms later.

            packet = link.sendPacket(device)

            if packet:
                if(device == link.device1):
                    newEvent = Event(packet, link.device2, "RECEIVE", event.time + 
                                     link.delay, self.flow)
                    self.insertEvent(newEvent)
                else:
                    newEvent = Event(packet, link.device1, "RECEIVE", event.time +
                                     link.delay, self.flow)
                    self.insertEvent(newEvent)

            else:
                newEvent = Event(None, (link, device), "SEND", event.time + 1, event.flow)
                self.q.insert(newEvent)

        elif event.type == "RECEIVE":
            # Processes a host/router action that would receive things.
            assert(isinstance(event.handler, Device))

            # Router.
            if isinstance(event.handler, Router):
                router = event.handler
                newLink = router.transfer(event.packet)

                newEvent = Event(event.packet, (newLink, router), "PUT", event.time, event.flow)
                self.insertEvent(newEvent)

            # Host

            elif isinstance(event.handler, Host):
                if(packet.type == "DATA"):
                    host = event.handler
                    host.receive(event.packet)

                    newEvent = Event(event.packet, None, "GENERATEACK", event.time, event.flow)
                    self.insertEvent(newEvent)
                else:
                    ########################################
                    ####### TODO: Acknowledgement got ######
                    ########################################

                    host = event.handler
                    host.receive(packet)


                    sendMore = self.flow.receiveAcknowledgement(packet)
                    # boolean = ^ which tells us whether window is completed or not

                    # IF SO, 
                    #######################################
                    ##### Push in new GENERATEPACKS... ####
                    #######################################

                    if(sendMore):
                        for i in range(flow.window_size):
                            newEvent = Event(None, None, "GENERATEPACK", event.time, event.flow)



        elif event.type == "GENERATEACK":
            # Processes a flow to generate an ACK.

            # Generate the new Ack Packet
            ackPacket = flow.generateAckPacket(event.packet)
            host = ackPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(ackPacket, (link, host), "PUT", event.time, event.flow)
            self.insertEvent(newEvent)


        elif event.type == "GENERATEPACK":
            # Processes a flow to generate a regular data packet.

            # Generate the new packet.
            newPacket = flow.generateDataPacket()
            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT", event.time, event.flow)
            self.insertEvent(newEvent)


    # def run(self):
    #     # set up hosts, link, flow
    #     # host with address H1
    #     host1 = Host("H1")
    #     print "---------------DEVICE DETAILS-----------------"
    #     print "Host Address: " + str(host1.deviceID)

    #     # host with address H1
    #     host2 = Host("H2")
    #     print "Host Address: " + str(host2.deviceID)

    #     # With this host and router, we create a link.v
    #     # The link will have an id of L1, with a rate of 10 mbps
    #     # and a delay of 10 ms, with a buffer size of 64kb.
    #     # It will be attached to host and router
    #     testLink = Link("L1", 10, 10, 64, host1, host2)

    #     # attach a link to the two hosts


    #     # creates a flow between host1 and host2.
    #     # currently, the amount of data sent through the flow is 0
    #     # as of now, the flow only generates packets.
    #     flow = Flow("F1", host1, host2, 0, 1.0)

    #     # now, insert into the queue a "generate packet" event
    #     # the flow starts at 1.0s = 1000 ms
    #     event = Event(flow, "generate", flow.flow_start * s_to_ms)
    #     self.insertEvent(event)

    #     while not self.conditions_met():
    #         try:
    #             event = self.q.get()
    #         except BufferError:
    #             pass
    #         self.processEvent(event)


