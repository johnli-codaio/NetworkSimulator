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


