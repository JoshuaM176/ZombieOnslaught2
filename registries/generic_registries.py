from py_doubly_linked_list import DoublyLinkedList

class GenericRegistry():
    def __init__(self, screen, alpha_screen):
        self.screen = screen
        self.alpha_screen = alpha_screen
        self.items = DoublyLinkedList()

    def add(self, item):
        self.items.append(item)

    def update(self, frame_time):
        for i in range(len(self.items)-1, 0, -1):
            if not self.items[i].update(frame_time, self.screen, self.alpha_screen):
                del self.items[i]