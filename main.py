import os
import random
import sys
import logging
import multiprocessing
import psutil
import ctypes
from queue import Queue
import threading
from multiprocessing import Lock
import time

# Set up logging to create a log file
logging.basicConfig(filename='Advanced_Process_Manager.log',
                    level=logging.INFO, format='%(asctime)s - %(message)s')

# Create a logger for the process manager
process_log = logging.getLogger('Advanced_Process_Manager')
process_log.setLevel(logging.INFO)

# Dictionary to keep track of running processes
running_processes = {}

# Dictionary to store threads for each process
process_threads = {}

# List to store information about threads
threads = []

# Multiprocessing Pipe for inter-process communication
pipe_conn, child_conn = multiprocessing.Pipe()

# Queue for shared data
shared_queue = Queue()

# Lock for process synchronization
mutex = multiprocessing.Lock()

# Shared Lock
shared_lock = Lock()

# Size of the shared buffer
BUFFER_SIZE = 5

# Shared buffer for producer-consumer example
buffer = []

# Semaphores for producer-consumer example
mutex = threading.Semaphore(1)  # Mutex for buffer access
empty = threading.Semaphore(BUFFER_SIZE)  # Semaphore for empty slots
filled = threading.Semaphore(0)  # Semaphore for filled slots

# Load the appropriate C library based on the platform
if sys.platform.startswith('win'):
    libc = ctypes.CDLL('msvcrt')
elif sys.platform.startswith('linux'):
    libc = ctypes.CDLL('libc')
elif sys.platform == 'darwin':
    libc = ctypes.CDLL('libc.dylib')
else:
    raise OSError("Unsupported platform")

# Function to run within child processes
def process_function(process_name):
    try:
        process_log.info(
            f"Child process '{process_name}' with PID {os.getpid()} running")
        process_threads[os.getpid()] = []

        while True:
            print("\nOptions within the process:")
            print("1. Create a thread")
            print("2. List threads")
            print("3. Exit process")
            choice = input("Select an option: ")

            if choice == "1":
                thread_name = input("Enter a name for the thread: ")
                create_thread(thread_name)
            elif choice == "2":
                list_threads()
            elif choice == "3":
                print("Exited process.")
                break
            else:
                print("Invalid option. Try again.")
    except Exception as e:
        process_log.error(f"Error in process_function: {str(e)}")

# Function to create a new process
def create_process(process_name):
    try:
        pid = os.fork()
        if pid == 0:  # This code runs in the child process
            try:
                os.execlp(process_name, process_name)
            except Exception as e:
                process_log.error(
                    f"Child process '{process_name}' with PID {os.getpid()} encountered an error: {str(e)}")
            os._exit(1)
        else:  # This code runs in the parent process
            running_processes[pid] = process_name
            process_log.info(
                f"Child process '{process_name}' with PID {pid} created.")
            process_function(process_name)
    except Exception as e:
        process_log.error(f"Error in create_process: {str(e)}")

# Function to list running processes
def list_processes():
    try:
        while True:
            print("\nList Processes Sub-Menu:")
            print("1. Processes created through your code")
            print("2. All processes on the computer")
            print("3. Back to the main menu")
            choice = input("Select an option: ")

            if choice == "1":
                # Display a list of processes created through your code
                process_log.info("Processes created through your code:")
                if not running_processes:
                    print("No processes were created through your code.")
                    process_log.info(
                        "No processes were created through your code.")
                else:
                    for pid, process_name in running_processes.items():
                        process_info = psutil.Process(pid)
                        parent_pid = process_info.ppid()
                        state = process_info.status()
                        process_log.info(
                            f"Process with PID: {pid}, Name: {process_name}, Parent PID: {parent_pid}, State: {state}")
                        print(
                            f"Process with PID: {pid}, Name: {process_name}, Parent PID: {parent_pid}, State: {state}")
            elif choice == "2":
                # Display a list of all processes on the computer
                process_log.info("All processes on the computer:")
                for process in psutil.process_iter(attrs=['pid', 'ppid', 'name', 'status']):
                    process_info = process.info
                    pid = process_info['pid']
                    ppid = process_info['ppid']
                    name = process_info['name']
                    status = process_info['status']
                    process_log.info(
                        f"Process with PID: {pid}, Parent PID: {ppid}, Name: {name}, Status: {status}")
                    print(
                        f"Process with PID: {pid}, Parent PID: {ppid}, Name: {name}, Status: {status}")
            elif choice == "3":
                # Return to the main menu
                print("Returning to the main menu.")
                break
            else:
                # Handle invalid menu options
                print("Invalid option. Try again.")
    except Exception as e:
        # Log an error if an exception occurs
        process_log.error(f"Error in list_processes: {str(e)}")


# Create an event to signal thread exit
thread_exit_signal = threading.Event()

# Function to create a new thread
def create_thread(thread_name):
    try:
        # Get the process ID of the current process
        process_pid = os.getpid()

        # Create a variable to store the thread ID
        thread_id = ctypes.c_long()

        # Define the function to be executed by the thread
        def thread_func():
            # Log that the thread is running
            process_log.info(f"Thread '{thread_name}' running")

        # Create a pointer to the thread function
        thread_func_ptr = ctypes.CFUNCTYPE(None)(thread_func)

        # Attempt to create a new thread
        if libc.pthread_create(ctypes.byref(thread_id), None, thread_func_ptr, None) == 0:
            # If the thread is created successfully, add it to the list of threads
            threads.append((thread_id, thread_name))
            # Store the thread in the dictionary of process threads
            process_threads.setdefault(process_pid, []).append(
                (thread_id, thread_name))
            # Log that the thread was created successfully
            process_log.info(f"Thread '{thread_name}' created successfully")
        else:
            # Log an error if the thread creation fails
            process_log.error("Failed to create thread")
    except Exception as e:
        # Log an error if an exception occurs during thread creation
        process_log.error(f"Error in create_thread: {str(e)}")


# Function to terminate a thread
def terminate_thread(thread_name):
    try:
        global threads, thread_exit_signal
        threads_to_remove = []
        thread_terminated = False

        for thread, name in threads:
            if name == thread_name:
                thread_exit_signal.set()  # Set the exit signal to terminate the thread
                # To terminate the thread, use ctypes to call pthread_join
                libc.pthread_join(thread, None)
                threads_to_remove.append((thread, name))
                thread_terminated = True
                print(f"Thread '{thread_name}' terminated.")
                process_log.info(f"Thread '{thread_name}' terminated.")

        if not thread_terminated:
            print(f"Thread '{thread_name}' not found.")
            process_log.error(f"Thread '{thread_name}' not found.")

        threads = [(t, n)
                   for t, n in threads if (t, n) not in threads_to_remove]
    except Exception as e:
        process_log.error(f"Error in terminate_thread: {str(e)}")

# Function to list threads within the current process
def list_threads():
    process_pid = os.getpid()
    threads = process_threads.get(process_pid, [])

    if not threads:
        print("No threads in this process.")
    else:
        print("Threads in this process:")
        for thread_id, thread_name in threads:
            print(f"Thread ID: {thread_id}, Name: {thread_name}")


# Create pipes for inter-process communication (IPC)
read_pipe, write_pipe = os.pipe()

# Function to send an IPC message
def ipc_send(message):
    try:
        os.write(write_pipe, message.encode())
        process_log.info(f"Message sent: {message}")
    except Exception as e:
        process_log.error(f"Error in ipc_send: {str(e)}")

# Function to receive an IPC message
def ipc_receive():
    try:
        # Check if there is any data available to read from the pipe
        if os.fstat(read_pipe).st_size > 0:
            message = os.read(read_pipe, 1024)
            print(f"Received message: {message.decode()}")
            process_log.info(f"Received message: {message.decode()}")
            return message.decode()
        else:
            print("No message available")
            process_log.warning("No message available")
    except Exception as e:
        process_log.error(f"Error in ipc_receive: {str(e)}")

# Similar to Homework 6
# Producer function for the producer-consumer example 
def producer(*args):
    for i in range(10):
        item = f"Item-{i}"  # You can generate your items here
        empty.acquire()  # Wait for an empty slot
        mutex.acquire()  # Get exclusive access to the buffer
        buffer.append(item)  # Add item to the buffer
        print(f"Produced {item}. Buffer: {buffer}")
        process_log.info(f"Produced {item}. Buffer: {buffer}")
        mutex.release()  # Release the mutex
        filled.release()  # Notify that a slot is filled
        time.sleep(random.uniform(0.1, 0.5))  # Simulate work

# Consumer function for the producer-consumer example
def consumer(*args):
    for i in range(10):
        filled.acquire()  # Wait for a filled slot
        mutex.acquire()  # Get exclusive access to the buffer
        item = buffer.pop(0)  # Remove and consume the first item
        print(f"Consumed {item}. Buffer: {buffer}")
        process_log.info(f"Consumed {item}. Buffer: {buffer}")
        mutex.release()  # Release the mutex
        empty.release()  # Notify that a slot is empty
        time.sleep(random.uniform(0.1, 0.5))  # Simulate work

# Function for process synchronization (producer-consumer example)
def process_synchronization():
    producers = [threading.Thread(target=producer) for _ in range(2)]
    consumers = [threading.Thread(target=consumer) for _ in range(2)]

    for producer_thread in producers:
        producer_thread.start()
    for consumer_thread in consumers:
        consumer_thread.start()

    time.sleep(5)  # Allow the threads to run for some time

    for producer_thread in producers:
        producer_thread.join()
    for consumer_thread in consumers:
        consumer_thread.join()

# Function to clear the log file
def Clear_Log():
    try:
        with open('Advanced_Process_Manager.log', 'w'):
            pass
        print('\nLog file cleared.')
    except Exception as e:
        logging.error(f"Error in Clear_Log: {str(e)}")


# Main entry point of the program
if __name__ == "__main__":
    options = {
        "1": lambda: create_process(input("Enter the process name: ")),
        "2": lambda: create_thread(input("Enter a name for the thread: ")),
        "3": lambda: terminate_thread(input("Enter thread name to terminate: ")),
        "4": list_processes,
        "5": lambda: ipc_send(input("Enter message to send: ")),
        "6": ipc_receive,
        "7": process_synchronization,
        "8": Clear_Log,
        "9": lambda: (print("Exited successfully"), exit(0))
    }

    while True:
        print("\nOptions:")
        print("1. Create A Process")
        print("2. Create A Thread")
        print("3. Terminate A Thread")
        print("4. Monitor Running Processes")
        print("5. Send IPC Message")
        print("6. Receive IPC Message")
        print("7. Process Synchronization")
        print("8. Clear Log File")
        print("9. Exit")
        choice = input("Select an option: ")

        function = options.get(choice)
        if function:
            function()
        else:
            print("Invalid option. Try again.")
