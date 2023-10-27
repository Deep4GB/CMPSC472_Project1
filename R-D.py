import threading

resource = 0  # Shared resource
readers = 0  # Number of active readers

# Semaphores
mutex = threading.Semaphore(1)
write_mutex = threading.Semaphore(1)

# Reader function
def reader():
    global readers
    while True:
        mutex.acquire()
        readers += 1
        if readers == 1:
            write_mutex.acquire()
        mutex.release()
        # Read from the resource
        print(f"Reader reads: {resource}")
        mutex.acquire()
        readers -= 1
        if readers == 0:
            write_mutex.release()
        mutex.release()

# Writer function
def writer():
    while True:
        write_mutex.acquire()
        # Write to the resource
        global resource
        resource += 1
        print(f"Writer writes: {resource}")
        write_mutex.release()

# Create reader and writer threads
reader_thread1 = threading.Thread(target=reader)
reader_thread2 = threading.Thread(target=reader)
writer_thread = threading.Thread(target=writer)

# Start the threads
reader_thread1.start()
reader_thread2.start()
writer_thread.start()

# Wait for the threads to finish (in a real scenario, you'd have a termination condition)
reader_thread1.join()
reader_thread2.join()
writer_thread.join()
