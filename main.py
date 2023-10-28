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

logging.basicConfig(filename='Advanced_Process_Manager.log', level=logging.INFO, format='%(asctime)s - %(message)s')

process_log = logging.getLogger('Advanced_Process_Manager')
process_log.setLevel(logging.INFO)

running_processes = {}
process_threads = {}
threads = []
pipe_conn, child_conn = multiprocessing.Pipe()
shared_queue = Queue()
mutex = multiprocessing.Lock()
process_threads = {}
shared_lock = Lock()
BUFFER_SIZE = 5

# Shared buffer
buffer = []

# Semaphores
mutex = threading.Semaphore(1)  # Mutex for buffer access
empty = threading.Semaphore(BUFFER_SIZE)  # Semaphore for empty slots
filled = threading.Semaphore(0)  # Semaphore for filled slots

if sys.platform.startswith('win'):
    libc = ctypes.CDLL('msvcrt')
elif sys.platform.startswith('linux'):
    libc = ctypes.CDLL('libc')
elif sys.platform == 'darwin':
    libc = ctypes.CDLL('libc.dylib')
else:
    raise OSError("Unsupported platform")

def process_function(process_name):
    try:
        process_log.info(f"Child process '{process_name}' with PID {os.getpid()} running")
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

def create_process(process_name):
    try:
        pid = os.fork()
        if pid == 0:
            try:
                os.execlp(process_name, process_name)
            except Exception as e:
                process_log.error(f"Child process '{process_name}' with PID {os.getpid()} encountered an error: {str(e)}")
            os._exit(1)
        else:
            running_processes[pid] = process_name
            process_log.info(f"Child process '{process_name}' with PID {pid} created.")
            process_function(process_name)
    except Exception as e:
        process_log.error(f"Error in create_process: {str(e)}")

def list_processes():
    try:
        while True:
            print("\nList Processes Sub-Menu:")
            print("1. Processes created through your code")
            print("2. All processes on the computer")
            print("3. Back to the main menu")
            choice = input("Select an option: ")

            if choice == "1":
                process_log.info("Processes created through your code:")
                if not running_processes:
                    print("No processes were created through your code.")
                    process_log.info("No processes were created through your code.")
                else:
                    for pid, process_name in running_processes.items():
                        process_info = psutil.Process(pid)
                        parent_pid = process_info.ppid()
                        state = process_info.status()
                        process_log.info(f"Process with PID: {pid}, Name: {process_name}, Parent PID: {parent_pid}, State: {state}")
                        print(f"Process with PID: {pid}, Name: {process_name}, Parent PID: {parent_pid}, State: {state}")
            elif choice == "2":
                process_log.info("All processes on the computer:")
                for process in psutil.process_iter(attrs=['pid', 'ppid', 'name', 'status']):
                    process_info = process.info
                    pid = process_info['pid']
                    ppid = process_info['ppid']
                    name = process_info['name']
                    status = process_info['status']
                    process_log.info(f"Process with PID: {pid}, Parent PID: {ppid}, Name: {name}, Status: {status}")
                    print(f"Process with PID: {pid}, Parent PID: {ppid}, Name: {name}, Status: {status}")
            elif choice == "3":
                print("Returning to the main menu.")
                break
            else:
                print("Invalid option. Try again.")
    except Exception as e:
        process_log.error(f"Error in list_processes: {str(e)}")


# Create an event to signal thread exit
thread_exit_signal = threading.Event()

def create_thread(thread_name):
    try:
        process_pid = os.getpid()
        thread_id = ctypes.c_long()

        def thread_func():
            process_log.info(f"Thread '{thread_name}' running")

        thread_func_ptr = ctypes.CFUNCTYPE(None)(thread_func)

        if libc.pthread_create(ctypes.byref(thread_id), None, thread_func_ptr, None) == 0:
            threads.append((thread_id, thread_name))
            process_threads.setdefault(process_pid, []).append((thread_id, thread_name))
            process_log.info(f"Thread '{thread_name}' created successfully")
        else:
            process_log.error("Failed to create thread")
    except Exception as e:
        process_log.error(f"Error in create_thread: {str(e)}")

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
            
        threads = [(t, n) for t, n in threads if (t, n) not in threads_to_remove]
    except Exception as e:
        process_log.error(f"Error in terminate_thread: {str(e)}")


def list_threads():
    process_pid = os.getpid()
    threads = process_threads.get(process_pid, [])

    if not threads:
        print("No threads in this process.")
    else:
        print("Threads in this process:")
        for thread_id, thread_name in threads:
            print(f"Thread ID: {thread_id}, Name: {thread_name}")

read_pipe, write_pipe = os.pipe()

def ipc_send_message(message):
    try:
        os.write(write_pipe, message.encode())
        process_log.info(f"Message sent: {message}")
    except Exception as e:
        process_log.error(f"Error in ipc_send_message: {str(e)}")

def ipc_receive_message():
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
        process_log.error(f"Error in ipc_receive_message: {str(e)}")


# Producer function
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

# Consumer function
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

def clear_log_file():
    try:
        with open('Advanced_Process_Manager.log', 'w'):
            pass
        print('\nLog file cleared.')
    except Exception as e:
        logging.error(f"Error in clear_log_file: {str(e)}")

if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("1. Create a process")
        print("2. Create a thread")
        print("3. Terminate a thread")
        print("4. Monitor all running processes on your device.")
        print("5. Send IPC message")
        print("6. Receive IPC message")
        print("7. Process Synchronization")
        print("8. Clear log file")
        print("9. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            process_name = input("Enter the process name: ")
            create_process(process_name)
        elif choice == "2":
            thread_name = input("Enter a name for the thread: ")
            create_thread(thread_name)
        elif choice == "3":
            thread_name = input("Enter thread name to terminate: ")
            terminate_thread(thread_name)
        elif choice == "4":
            list_processes()
        elif choice == "5":
            message = input("Enter message to send: ")
            ipc_send_message(message)
        elif choice == "6":
            received_message = ipc_receive_message()
        elif choice == "7":
            process_synchronization()
        elif choice == "8":
            clear_log_file()
        elif choice == "9":
            print("Exited successfully")
            exit(0)
        else:
            print("Invalid option. Try again.")
