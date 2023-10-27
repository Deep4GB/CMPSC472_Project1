import threading
import time
import random

# Shared buffer with a limited capacity
buffer = []
buffer_capacity = 5

# Semaphore for controlling buffer access
empty = threading.Semaphore(buffer_capacity)
full = threading.Semaphore(0)
mutex = threading.Semaphore(1)

# Producer function
def producer():
    while True:
        item = random.randint(1, 100)  # Simulated item to produce
        empty.acquire()  # Wait for an empty slot
        mutex.acquire()  # Protect the buffer
        buffer.append(item)
        print(f"Produced: {item}, Buffer: {buffer}")
        mutex.release()
        full.release()

# Consumer function
def consumer():
    while True:
        full.acquire()  # Wait for a filled slot
        mutex.acquire()  # Protect the buffer
        item = buffer.pop(0)
        print(f"Consumed: {item}, Buffer: {buffer}")
        mutex.release()
        empty.release()
        time.sleep(1)  # Simulated consumption time

# Create producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

# Start the threads
producer_thread.start()
consumer_thread.start()

# Wait for the threads to finish (in a real scenario, you'd have a termination condition)
producer_thread.join()
consumer_thread.join()
