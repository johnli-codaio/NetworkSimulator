from classes import *
import time
import random
import event


# Just a few tests
if __name__ == "__main__":
    random.seed()

    # host with address H1
    host1 = Host("H1")
    print "---------------DEVICE DETAILS-----------------"
    print "Host Address: " + str(host1.address)

    # host with address H1
    host2 = Host("H2")
    print "Host Address: " + str(host2.address)

    # router with address R1
    # router = Router("R1")
    # print "Router Address: " + str(router.address) + "\n"

    # With this host and router, we create a link.v
    # The link will have an id of L1, with a rate of 10 mbps
    # and a delay of 10 ms, with a buffer size of 64kb.
    # It will be attached to host and router

    testLink = Link("L1", 10, 10, 64, host1, host2)

    print "----------------LINK DETAILS------------------"
    print "Link ID: " + str(testLink.linkId)
    print "Link Rate: " + str(testLink.rate) + " Mbps"
    print "Link Delay: " + str(testLink.delay) + " ms"
    print "Link Buffer: " + str(testLink.buffer_size) + " B"
    print "Link Device1: " + str(testLink.device1.address)
    print "Link Device2: " + str(testLink.device2.address) + "\n"

    print "----------------PACKET DETAILS----------------"

    src = host1.address
    dest = host2.address
    flow = Flow("F1", src, dest)

    while True:
        # print "Making New Packet!!!"
        packet = flow.generateDataPacket()
        # print "Packet Source: " + str(packet.src)
        # print "Packet Destination: " + str(packet.dest)
        # print "Packet Data: " + str(packet.type)
        # print "Enqueing this Packet... \n"
        testLink.putIntoBuffer(packet)
        print testLink.current_buffer
        print testLink.buffer_size
        willBeFull = testLink.isFullWith(packet)
        if willBeFull:
            break
    print testLink.linkBuffer.qsize()

    print "Now, to dequeue this link buffer...\n"

    while testLink.linkBuffer.empty() == False:
        popped_packet = testLink.popFromBuffer()
        print "Popped Packet Source: " + str(popped_packet.src)
        print "Popped Packet Destination: " + str(popped_packet.dest)
        print "Popped Packet Data: " + str(popped_packet.type) + "\n"
        print "Popped Packet Data Size: " + str(popped_packet.data_size)

    print "Queue is now empty, test is over :). \n"


