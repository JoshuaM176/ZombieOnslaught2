import queue

class EventBus(): 
    def __init__(self):
        self.busses: dict [str: queue] = {}
    
    def create_bus(self, name: str):
        q = queue.Queue()
        self.busses[name] = q

    def add_event(self, bus: str, event: str):
        self.busses[bus].put(event)

    def get_events(self, name: str):
        q: queue.Queue = self.busses[name]
        while q.not_empty:
            yield q.get()

event_bus = EventBus()