import Queue
import datetime
import time
from classes import *

# Types of events:
# when a flow generates a packet (type = generate)
# when a device sends a packet (type = send)
# when a device receives a packet (type = receive)
# but the only events here are the packets being moved around
class Event:
    """Events are enqueued into the Simulator priority queue by their time. Events
    have a type (SENDTOLINK, SENDTODEVICE, RECEIVE, GENERATE) describing what is 
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
        :type EventType: String

        :param EventTime: The time of the particular event, in milliseconds.
        :type EventTime: Integer
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
    def __init__(self):
        """ This will initialize the simulation with a Priority Queue
        that sorts based on time.
        """
        self.q = Queue.PriorityQueue()

    def insertEvent(self, event):
        """ This will insert an event into the Priority Queue.

        :param event: This is the event we're adding into the queue.
        :type event: Event
        """
        self.q.put(event)

    def processEvent(self):
        """Pops and processes event from queue."""
        event = self.q.get()

        print event.type
        if(event.type == "SENDTOLINK"):
            # Tries to put packet into link buffer
            # This only happens initially, when a host is moving a packet
            # into the link buffer. Routers will instantenously receive 
            # and transmit.
            assert(isinstance(event.handler, Host))
            link = event.handler.getLink()
            host = event.handler
            if not link.rateFullWith(event.packet):
                host.sendToLink(link, event.packet)
            else:
                # If link buffer is full, we wait until it's not full.
                newEvent = Event(event.packet, host, "SENDTOLINK", event.time + 1)
                self.q.insert(newEvent)

        elif(event.type == "RECEIVE"):
            # Processes a host/router action that would receive things.
            assert(isinstance(event.handler, Device))

            # First, the issue with the router.
            if isinstance(event.handler, Router):
                router = event.handler
                router.transfer(event.packet)

                # Transfer will update the current location of the packet to the new
                # link.
                newLink = packet.curr
                newEvent = Event(event.packet, newLink, "SENDTODEVICE", event.time)

            elif isinstance(event.handler, Host):
                host = event.handler
                if(event.packet.dest == host)








    def processEvent(self, event):
        print event.type
        if event.type == "SEND":
            
            assert(isinstance(event.handler, Link))

            packet = event.handler.peekFromBuffer()

            # here, event.handler is a link
            try:
                packet = event.handler.peekFromBuffer()
            # no packets in the buffer
            except BufferError:
                return

            # it's not ready to be sent, because the current link
            # rate is too full
            # so, requeue it as an event later in time
            if not event.handler.sendPacket(packet):
                sameEvent = Event(event.handler, "send", event.time + 1)
                self.insertEvent(newEvent)
            else:
                # this packet is ready to be sent, handled by the link
                # so, we have to enqueue a receive event,
                # which should occur exactly after (specificed by link delay)
                newEvent = Event(packet.dest, "receive", event.time + event.handler.delay)
                self.insertEvent(newEvent)

                # TODO read this
                # also, check to see if there's more packets to be sent
                # from the buffer!
                # if the link rate is not full, then we should be
                # able to send multiple packets simultaneously?
                if not event.handler.linkBuffer.empty():
                    newEvent = Event(event.handler, "send", event.time)
                    self.insertEvent(newEvent)

        elif event.type == "RECEIVE":
            # here, event.handler is a host
            # this packet can be dequeued by the receiving host
            packet = event.handler.receiving()
            # update the amount of data sent
            self.current_state[0] += packet.data_size
            print "Current Memory Sent: " + str(self.current_state[0])

        elif event.type == "GENERATE":
            # here, event.handler is a flow
            # the flow will generate a packet
            newPacket = event.handler.generateDataPacket()

            # and then, put this data packet into the outgoing
            # link buffer
            link = event.handler.src.getLink()
            link.putIntoBuffer(newPacket)

            # now, we have to enqueue a send event,
            # becuase it might be ready for sending
            newEvent = Event(link, "SEND", event.time + 1)
            self.insertEvent(newEvent)

            # also, generate more packets to be sent!
            generateEvent = Event(event.handler, "GENERATE", event.time + 1)
            self.insertEvent(generateEvent)


    def run(self):
        # set up hosts, link, flow
        # host with address H1
        host1 = Host("H1")
        print "---------------DEVICE DETAILS-----------------"
        print "Host Address: " + str(host1.deviceID)

        # host with address H1
        host2 = Host("H2")
        print "Host Address: " + str(host2.deviceID)

        # With this host and router, we create a link.v
        # The link will have an id of L1, with a rate of 10 mbps
        # and a delay of 10 ms, with a buffer size of 64kb.
        # It will be attached to host and router
        testLink = Link("L1", 10, 10, 64, host1, host2)

        # attach a link to the two hosts


        # creates a flow between host1 and host2.
        # currently, the amount of data sent through the flow is 0
        # as of now, the flow only generates packets.
        flow = Flow("F1", host1, host2, 0, 1.0)

        # now, insert into the queue a "generate packet" event
        # the flow starts at 1.0s = 1000 ms
        event = Event(flow, "generate", flow.flow_start * s_to_ms)
        self.insertEvent(event)

        while not self.conditions_met():
            try:
                event = self.q.get()
            except BufferError:
                pass
            self.processEvent(event)


