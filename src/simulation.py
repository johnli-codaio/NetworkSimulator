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

    #   EventHandler: the device(?) that is interacting with the packet
    #   (generating, sending, or receiving it)
    #   Packet: the packet 
    #   EventType: generating, sending, or receiving
    #   EventTime: the time at which the particular event is occurring
    def __init__(self, EventHandler, EventType, EventTime):
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

    def __cmp__(self, other):
        return cmp(self.time, other.time)


class Simulator:
    # TODO
    def __init__(self, conditions):
        self.q = Queue.PriorityQueue()
        self.conditions = conditions
        self.current_state = [0]

    def insertEvent(self, event):
        self.q.put(event)

    def processEvent(self, event):
        print event.type
        if event.type == "send":
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

        elif event.type == "receive":
            # here, event.handler is a host
            # this packet can be dequeued by the receiving host
            packet = event.handler.receiving()
            # update the amount of data sent
            self.current_state[0] += packet.data_size
            print "Current Memory Sent: " + str(self.current_state[0])

        elif event.type == "generate":
            # here, event.handler is a flow
            # the flow will generate a packet
            newPacket = event.handler.generateDataPacket()

            # and then, put this data packet into the outgoing
            # link buffer
            link = event.handler.src.getLink()
            link.putIntoBuffer(newPacket)

            # now, we have to enqueue a send event,
            # becuase it might be ready for sending
            newEvent = Event(link, "send", event.time + 1)
            self.insertEvent(newEvent)

            # also, generate more packets to be sent!
            generateEvent = Event(event.handler, "generate", event.time + 1)
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




    # for test case 0: have we sent in 20MB of data yet?
    # TODO
    def conditions_met(self):
        return self.conditions[0] == self.current_state[0]


if __name__ == "__main__":
    s = Simulator([20 * MB_TO_KB])
    s.run()





