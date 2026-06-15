"""
Problem 1: Next in Queue
Each user on a music app should have a queue of songs to play next. Implement the class Queue using a singly linked list. Recall that a queue is a First-In-First-Out (FIfO) data structure where elements are added to the end (the tail) and removed from the front (the head).

Your queue must have the following methods:

__init()__: Initializes an empty queue (provided)
enqueue(): Accepts a tuple of two strings (song, artist) and adds the element with the specified tuple to the end of the queue.
dequeue(): Removes and returns the element at the front of the queue. If the queue is empty, returns None.
peek(): Returns the value of the element at the front of the queue without removing it. If the queue is empty, returns None.
is_empty(): Returns True if the queue is empty, and False otherwise.
"""
from typing import Tuple, Optional

class Node:
	def __init__(self, value, next=None):
		self.value = value
		self.next = next

# For testing
def print_queue(head):
    current = head.front
    while current:
        print(current.value, end=" -> " if current.next else "")
        current = current.next
    print()

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
    
    def is_empty(self):
        # [Node1] -> [Node2].... -> [Node n]
        if not self.front:
            return True
        return False

    def enqueue(self, value) -> None:
        new_node = Node(value)
        if not self.rear:
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        
    def dequeue(self) -> Optional[Tuple[str, str]]:
        if not self.front:
            return None
        else:
            deque_val = self.front.value
            self.front = self.front.next
            return deque_val
    
    def peek(self):
        if not self.front:
            return None
        else:
            deque_val = self.front.value
            return deque_val
   
    
    
# Create a new Queue
q = Queue()

# Add elements to the queue
q.enqueue(('Love Song', 'Sara Bareilles'))
q.enqueue(('Ballad of Big Nothing', 'Elliot Smith'))
q.enqueue(('Hug from a Dinosaur', 'Torres'))
print_queue(q)

# View the front element
print("Peek: ", q.peek()) 

# Remove elements from the queue
print("Dequeue: ", q.dequeue()) 
print("Dequeue: ", q.dequeue()) 

# Check if the queue is empty
print("Is Empty: ", q.is_empty()) 

# Remove the last element
print("Dequeue: ", q.dequeue()) 

# Check if the queue is empty
print("Is Empty:", q.is_empty())# 