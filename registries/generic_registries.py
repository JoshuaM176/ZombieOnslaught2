from llist import dllist

class GenericRegistry():
    def __init__(self, screen, alpha_screen):
        self.screen = screen
        self.alpha_screen = alpha_screen
        self.items = dllist()

    def add(self, item):
        self.items.append(item)

    def update(self, frame_time):
        current_node = self.items.first
        while current_node is not None:
            next_node = current_node.next
            if not current_node.value.update(frame_time, self.screen, self.alpha_screen):
                self.items.remove(current_node)
            current_node = next_node