# Types of events:
# when a flow generates a packet (type = generate)
# when a device sends a packet (type = send)
# when a device receives a packet (type = receive)
# but the only events here are the packets being moved around
class Event:
    def __init__(self, Packet, EventType, EventTime):
        self.packet = Packet
        self.type = EventType
        self.time = EventTime


    def __cmp__(self, other):
        return cmp(self.time, other.time)


