import Queue
import datetime
import time
from classes import *
from math import *


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

        EventType               EventHandler        Packet
        PUT                     (Link, Device)
        SEND                    (Link, Device)      None
        RECEIVE                 Device
        GENERATEACK             None                None
        GENERATEPACK            None                None

        """

        self.packet = packet
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

        self.flow = flow

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
        self.q.put(event)

    def processEvent(self):
        """Pops and processes event from queue."""

        if(self.q.empty()):
            print "No events in queue."
            return

        event = self.q.get()

        print "Popped event type: ", event.type
        if event.type == "INITIALIZEFLOW":
    
            event.flow.initializePackets()

            while(event.flow.window_counter < floor(event.flow.window_size)):
                newEvent = Event(None, None, "SELECTPACK", event.time, event.flow)
                event.flow.window_counter = event.flow.window_counter + 1
                print "Window counter: " + str(event.flow.window_counter)
                self.insertEvent(newEvent)

        elif event.type == "PUT":
            # Tries to put packet into link buffer
            # This happens whenever a device receives a packet.

            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]

            if not link.rateFullWith(event.packet):
                device.sendToLink(link, event.packet)
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
                                     link.delay, event.flow)
                    self.insertEvent(newEvent)
                else:
                    newEvent = Event(packet, link.device1, "RECEIVE", event.time +
                                     link.delay, event.flow)
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
                if(event.packet.type == "DATA"):
                    host = event.handler
                    host.receive(event.packet)

                    newEvent = Event(event.packet, None, "GENERATEACK", event.time, event.flow)
                    self.insertEvent(newEvent)
                else:
                    ########################################
                    ####### TODO: Acknowledgement got ######
                    ########################################

                    host = event.handler
                    host.receive(event.packet)


                    event.flow.receiveAcknowledgement(event.packet)
                    #  ^ This will update the packet index that it will be
                    #    sending from. Thus, constantly be monitoring

                    # IF SO, 
                    #######################################
                    ##### Push in new GENERATEPACKS... ####
                    #######################################

        
                    increment = 0.1
                    while(event.flow.window_counter < floor(event.flow.window_size)):
                        newEvent = Event(None, None, "SELECTPACK", event.time + increment, event.flow)
                        event.flow.window_counter = event.flow.window_counter + 1
                        print "Window counter: " + str(event.flow.window_counter)
                        self.insertEvent(newEvent)
                        increment = increment + 0.1


        elif event.type == "GENERATEACK":
            # Processes a flow to generate an ACK.

            # Generate the new Ack Packet
            ackPacket = event.flow.generateAckPacket(event.packet)
            host = ackPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(ackPacket, (link, host), "PUT", event.time + 1, event.flow)
            self.insertEvent(newEvent)


        elif event.type == "SELECTPACK":
            # Processes a flow to generate a regular data packet.

            # Generate the new packet.
            newPacket = event.flow.selectDataPacket()
            if(newPacket == None):
                return

            print "Packet to be sent: " + newPacket.packetID
            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT", event.time + 1, event.flow)
            self.insertEvent(newEvent)




