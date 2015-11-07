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

    def __init__(self, packet, EventHandler, EventType, EventTime):
        """ This will initialize an event.

        :param packet: The packet associated with the event.
        :type packet: Packet/None (None is usually reserved for flows)

        :param EventHandler: The object that sent the event request.
        :type EventHandler: Device, Packet, Flow, Link.

        :param EventType: The type of event that will be sent.
        :type EventType: Str

        :param EventTime: The time of the particular event, in milliseconds.
        :type EventTime: Int
        """

        self.packet = packet
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

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
        event = self.q.pop()

        print event.type
        if event.type == "PUT":
            # Tries to put packet into link buffer
            # This happens whenever a device receives a packet.
            # The event handler will take in a tuple, first index
            # is the device, and second index is the link.
            assert(isinstance(event.handler, Device))
            host = event.handler[0]
            link = event.handler[1]

            if not link.rateFullWith(event.packet):
                host.sendToLink(link, event.packet)
                newEvent = Event(None, link, "SEND", event.time)
                self.q.insert(newEvent)

        elif event.type == "RECEIVE":
            # Processes a host/router action that would receive things.
            assert(isinstance(event.handler, Device))

            # First, the issue with the router.
            if isinstance(event.handler, Router):
                router = event.handler
                newLink = router.transfer(event.packet)

                newEvent = Event(event.packet, (router, newLink), "PUT", event.time)
                self.q.insert(newEvent)

            # The packet reaches it's host destination...
            elif isinstance(event.handler, Host):
                host = event.handler
                host.receive(packet)

                for i in range(len(self.network.flows)):
                    tempFlow = self.network.flows[i]
                    if tempFlow.src == event.packet.src and tempFlow.dest == event.packet.dest:
                        eventFlow = tempFlow
                newEvent = Event(None, eventFlow, "GENERATEACK", event.time)
                self.q.insert(newEvent)

        elif event.type == "SEND":
            # Processes a link to send.
            assert(isinstance(event.handler, Link))

            link = event.handler
            
            # If you can send the packet, we check what buffer is currently in action.
            # If dev1->dev2, then we pop from device 1.
            # Else, we pop from device 2.
            # If we can't pop, then we call another send event 1 ms later.
            if link.sendPacket(event.packet, event.handler):
                if link.dev1todev2:
                    newEvent = Event(event.packet, link.device2, "RECEIVE", event.time + 10)
                else:
                    newEvent = Event(event.packet, link.device1, "RECEIVE", event.time + 10)
                self.q.insert(newEvent)

            else:
                newEvent = Event(None, link, "SEND", event.time + 1)
                self.q.insert(newEvent)

        elif event.type == "GENERATEACK":
            # Processes a flow to generate an ACK.

            assert(isinstance(event.handler, Flow))
            flow = event.handler

            # Generate the new Ack Packet
            ackPacket = flow.generateAckPacket()
            host = ackPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(ackPacket, (host, link), "PUT", event.time)
            self.q.insert(newEvent)

        elif event.type == "GENERATEPACK":
            # Processes a flow to generate a regular data packet.

            assert(isinstance(event.handler, Flow))
            flow = event.handler

            # Generate the new packet.
            newPacket = flow.generateDataPacket()
            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (host, link), "PUT", event.time)
            self.q.insert(newEvent)


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


