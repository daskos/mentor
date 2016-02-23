from collections import deque


class Queue(deque):

    def put(self, value):
        self.append(value)

    def get(self):
        return self.popleft()

    def empty(self):
        return len(self) == 0
