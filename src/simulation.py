import Queue

class Simulator:
    def __init__(self):
        q = Queue.PriorityQueue()
        length = len(q)

    def insertEvent(event):
        q.put(event)

    def processEvent():
        event = q.get()
        if event.type == send:
            print event.packet.src
        elif event.type == receive:
            print event.packet.dest
        elif event.type == generate:
            print event.packet.src


