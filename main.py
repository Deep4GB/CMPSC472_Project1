import os
import sys
import logging
import multiprocessing
import psutil
import ctypes
from queue import Queue
import threading


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

if sys.platform.startswith('win'):
    libc = ctypes.CDLL('msvcrt')
elif sys.platform.startswith('linux'):
    libc = ctypes.CDLL('libc')
elif sys.platform == 'darwin':
    libc = ctypes.CDLL('libc.dylib')
else:
    raise OSError("Unsupported platform")

# Create an event to signal thread exit
thread_exit_signal = threading.Event()

def create_thread(thread_name):
    process_pid = os.getpid()
    thread_id = threading.Thread(target=thread_wrapper, args=(thread_name,))
    thread_id.start()
    threads.append((thread_id, thread_name))
    process_threads.setdefault(process_pid, []).append((thread_id, thread_name))
    thread_exit_signal.clear()  # Clear the exit signal

def terminate_thread(thread_name):
    global threads, thread_exit_signal
    threads_to_remove = []
    for thread, name in threads:
        if name == thread_name:
            thread_exit_signal.set()  # Set the exit signal to terminate the thread
            thread.join()  # Wait for the thread to finish
            threads_to_remove.append((thread, name))
            print(f"Thread '{thread_name}' terminated.")
            logging.info(f"Thread '{thread_name}' terminated.")
    threads = [(t, n) for t, n in threads if (t, n) not in threads_to_remove]

def thread_wrapper(thread_name):
    if not thread_exit_signal.is_set():
        logging.info(f"Thread '{thread_name}' running")


def list_threads():
    process_pid = os.getpid()
    threads = process_threads.get(process_pid, [])

    if not threads:
        print("No threads in this process.")
    else:
        print("Threads in this process:")
        for thread_id, thread_name in threads:
            print(f"Thread ID: {thread_id.ident}, Name: {thread_name}")


def process_function(process_name):
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

def create_process(process_name):
    pid = os.fork()
    if pid == 0:
        try:
            os.execlp(process_name, process_name)
        except Exception as e:
            logging.error(f"Child process '{process_name}' with PID {os.getpid()} encountered an error: {str(e)}")
        os._exit(1)
    else:
        running_processes[pid] = process_name
        logging.info(f"Child process '{process_name}' with PID {pid} created.")
        process_function(process_name)

def list_processes():
    while True:
        print("\nList Processes Sub-Menu:")
        print("1. Processes created through your code")
        print("2. All processes on the computer")
        print("3. Back to the main menu")
        choice = input("Select an option: ")

        if choice == "1":
            process_log.info("Processes created through your code:")
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

def clear_log_file():
    with open('Advanced_Process_Manager.log', 'w'):
        pass
    print('\nLog file cleared.')

read_pipe, write_pipe = os.pipe()

def ipc_send_message(message):
    os.write(write_pipe, message.encode())
    process_log.info(f"Message sent: {message}")

def ipc_receive_message():
    message = os.read(read_pipe, 1024)
    return message.decode()

def process_synchronization():
    global mutex

    print("\nProcess Synchronization Sub-Menu:")
    print("1. Synchronize access to a shared resource")
    print("2. Back to the main menu")
    choice = input("Select an option: ")

    if choice == "1":
        print("Synchronizing access to a shared resource...")

        # Acquire the mutex for synchronized access
        mutex.acquire()

        # Simulate a critical section where access to a shared resource is synchronized
        print("Accessing the shared resource (mutex is acquired)...")
        print("Performing some work in the critical section...")

        # Release the mutex to allow other processes/threads to access the shared resource
        mutex.release()

        print("Released the mutex (end of critical section).")
    elif choice == "2":
        print("Returning to the main menu.")
    else:
        print("Invalid option. Try again.")

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
            if received_message:
                print(f"Received message: {received_message}")
            else:
                print("No message available")
        elif choice == "7":
            process_synchronization()
        elif choice == "8":
            clear_log_file()
        elif choice == "9":
            print("Exited successfully")
            exit(0)
        else:
            print("Invalid option. Try again.")
