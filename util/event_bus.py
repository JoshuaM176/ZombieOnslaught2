from queue import Queue

class EventBus(): 
    def __init__(self):
        self.busses: dict [str: Queue] = {}
    
    def create_bus(self, name: str):
        q = Queue()
        self.busses[name] = q

    def add_event(self, bus: str, event: str):
        self.busses[bus].put(event)

    def get_events(self, name: str):
        q: Queue = self.busses[name]
        while not q.empty():
            yield q.get()

event_bus = EventBus()