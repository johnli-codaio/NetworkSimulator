import Queue
from event import *
import datetime
import time
from classes import *

# the global time. initialized to time 0
TIME = 0
class Simulator:
    def __init__(self):
        self.q = Queue.PriorityQueue()

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
            newEvent = Event(packet.dest, "receive", TIME + 10)
            self.insertEvent(newEvent)
        elif event.type == "receive":
            # this packet can be dequeued by the receiving device
            handler.logReceive()

        elif event.type == "generate":
            # the flow will generate a packet
            newPacket = event.handler.generateDataPacket()

            # and then, put this data packet into the outgoing
            # link buffer
            event.handler.getLink().putIntoBuffer(newPacket)

            # now, we have to enqueue a send packet,
            # becuase it might be ready for sending

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
        # as of now, the flow only generates packets.
        flow = Flow("F1", host1, host2)

        global TIME
        # now, insert into the queue a "generate packet" event
        event = Event(flow, "generate", TIME)
        self.insertEvent(event)

        # increment time
        TIME += 1

        while not self.q.empty():
            event = self.q.get()
            self.processEvent(event)


if __name__ == "__main__":
    s = Simulator()
    s.run()





