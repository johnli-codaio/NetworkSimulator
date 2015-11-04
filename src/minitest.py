from classes import *
import time
import random

# Just a few tests
if __name__ == "__main__":
    random.seed()

    # host with address H1
    host = Host("H1")
    print "---------------DEVICE DETAILS-----------------"
    print "Host Address: " + str(host.address)

    # host with address H1
    host = Host("H2")
    print "---------------DEVICE DETAILS-----------------"
    print "Host Address: " + str(host.address)

    # router with address R1
    router = Router("R1")
    print "Router Address: " + str(router.address) + "\n"

    # With this host and router, we create a link.v
    # The link will have an id of 1, with a rate of 10 mbps
    # and a delay of 1 second, with a buffer size of 10.
    # It will be attached to host and router

    testLink = Link(1, 10, 1, 10, host, router)

    print "----------------LINK DETAILS------------------"
    print "Link ID: " + str(testLink.linkId)
    print "Link Rate: " + str(testLink.rate) + " Mbps"
    print "Link Delay: " + str(testLink.delay)
    print "Link Device1: " + str(testLink.device1.address)
    print "Link Device2: " + str(testLink.device2.address) + "\n"

    print "----------------PACKET DETAILS----------------"
    for i in range(5):
        print "Making New Packet!!!"
        src = random.randint(1, 20)
        dest = random.randint(1, 20)
        flow = Flow(1, src, dest, int(time.time()))
        data = random.randint(10000, 20000)
        packet = flow.generatePacket(data)

        print "Packet Source: " + str(packet.src)
        print "Packet Destination: " + str(packet.dest)
        print "Packet Data: " + str(packet.data)

        print "Enqueing this Packet... \n"
        testLink.putIntoBuffer(packet)

    print "Now, to dequeue this link buffer...\n"

    while testLink.linkBuffer.empty() == False:
        print "Popped Off Packet!!!"
        popped_packet = testLink.popFromBuffer()
        print "Popped Packet Source: " + str(popped_packet.src)
        print "Popped Packet Destination: " + str(popped_packet.dest)
        print "Popped Packet Data: " + str(popped_packet.data) + "\n"

    print "Queue is now empty, test is over :). \n"


