import Queue
from event import *
import datetime
import time
from classes import *

class Simulator:
    # TODO
    def __init__(self, conditions):
        self.q = Queue.PriorityQueue()
        self.conditions = conditions
        self.current_state = [0]

    def insertEvent(self, event):
        self.q.put(event)

    def processEvent(self, event):
        if event.type == "send":
            # this packet is ready to be sent, handled by the link
            packet = handler.popFromBuffer()
            handler.sendPacket(packet)
            # so, we have to enqueue a receive event,
            # which should occur exactly after 10 ms
            # (specificed by link delay)
            newEvent = Event(packet.dest, "receive", event.time + 10)
            self.insertEvent(newEvent)
        elif event.type == "receive":
            # this packet can be dequeued by the receiving host
            packet = handler.receiving()
            # update the amount of data sent
            self.current_state += packet.data_size

        elif event.type == "generate":
            # the flow will generate a packet
            newPacket = event.handler.generateDataPacket()

            # and then, put this data packet into the outgoing
            # link buffer
            link = event.handler.getLink()
            link.putIntoBuffer(newPacket)

            # now, we have to enqueue a send packet,
            # becuase it might be ready for sending
            newEvent = Event(link, "send", event.time + 1)

    def run(self):
        # set up hosts, link, flow
        # host with address H1
        host1 = Host("H1")
        print "---------------DEVICE DETAILS-----------------"
        print "Host Address: " + str(host1.address)

        # host with address H1
        host2 = Host("H2")
        print "Host Address: " + str(host2.address)

        # With this host and router, we create a link.v
        # The link will have an id of L1, with a rate of 10 mbps
        # and a delay of 10 ms, with a buffer size of 64kb.
        # It will be attached to host and router
        testLink = Link("L1", 10, 10, 64, host1, host2)

        # creates a flow between host1 and host2.
        # currently, the amount of data sent through the flow is 0
        # as of now, the flow only generates packets.
        flow = Flow("F1", host1, host2, 0, 1.0)

        # now, insert into the queue a "generate packet" event
        # the flow starts at 1.0s = 1000 ms
        event = Event(flow, "generate", 1000)
        self.insertEvent(event)

        while not self.conditions_met():
            event = self.q.get()
            self.processEvent(event)

    # for test case 0: have we sent in 20MB of data yet?
    # TODO
    def conditions_met(self, flow):
        self.conditions[0] = flow.data_amt


if __name__ == "__main__":
    s = Simulator()
    s.run()





