import os
import sys
import threading
import time
import multiprocessing
import logging
import psutil
import signal
import subprocess

logging.basicConfig(filename='Advanced_Process_Manager.log', level=logging.INFO, format='%(asctime)s - %(message)s')

previous_choice = None
result = ""
running_processes = {}
pipe_conn, child_conn = multiprocessing.Pipe()

# Flag to indicate if a thread should terminate
terminate_flags = {}

# List to track created processes and threads
created_processes_threads = []

choices = {
    "1": "Create Process",
    "2": "List Processes",
    "3": "Create Thread",
    "4": "Terminate Thread",
    "5": "Enter IPC Message",
    "6": "Receive IPC Message",
    "7": "Process Synchronization",
    "8": "Clear Log",
    "9": "Exit"
}

# Producer function
def producer(q):
    for item in range(5):
        q.put(item)
        print(f"Producing item {item}")
        logging.info(f"Producing item {item}")

# Consumer function
def consumer(q):
    for item in iter(q.get, None):
        print(f"Consuming item {item}")
        logging.info(f"Consuming item {item}")

# Function to create a process and add it to the tracking list
def create_process(process_name):
    pid = os.fork()
    if pid == 0:
        try:
            pass
        except Exception as e:
            logging.error(f"Child process '{process_name}' with PID {os.getpid()} encountered an error: {str(e)}")
        os._exit(0)
    else:
        running_processes[pid] = process_name
        created_processes_threads.append((pid, process_name)) 
        print(f"Child process '{process_name}' with PID {pid} created.")
        logging.info(f"Child process '{process_name}' with PID {pid} created.")

# Function to create a thread and add it to the tracking list
def create_thread(thread_name):
    terminate_flags[thread_name] = False  # Initialize the terminate flag
    thread = threading.Thread(target=thread_function, args=(thread_name,))
    logging.info(f"Thread '{thread_name}' started.") 
    thread.start()
    created_processes_threads.append((thread, thread_name))  
    print(f"Thread '{thread_name}' started.") 

def thread_function(thread_name):
    logging.info(f"Thread '{thread_name}' running.") 
    print(f"Thread '{thread_name}' running.")
    time.sleep(1)  # Simulate some work

    if terminate_flags[thread_name] == True:
        print(f"Thread '{thread_name}' is terminating gracefully.")
        logging.info(f"Thread '{thread_name}' is terminating gracefully.")

def terminate_thread(thread_name):
    if thread_name in terminate_flags:
        terminate_flags[thread_name] = True
        print(f"Terminating thread '{thread_name}'...")
        logging.info(f"Terminating thread '{thread_name}'...")
    else:
        print(f"Thread '{thread_name}' not found.")
        logging.info(f"Thread '{thread_name}' not found.")

def list_processes():
    print("List of running processes:")
    for proc in psutil.process_iter(attrs=['pid', 'ppid', 'name', 'status']):
        process_info = proc.info
        print(f"Process with PID: {process_info['pid']}, PPID: {process_info['ppid']}, Name: {process_info['name']}, Status: {process_info['status']}")
        logging.info(f"Process with PID: {process_info['pid']}, PPID: {process_info['ppid']}, Name: {process_info['name']}, Status: {process_info['status']}")

    # Display created processes and threads from the tracking list
    print("Created processes and threads:")
    for item in created_processes_threads:
        if isinstance(item[0], int):
            print(f"Created Process with PID: {item[0]}, Name: {item[1]}")
        elif isinstance(item[0], threading.Thread):
            print(f"Created Thread with Name: {item[1]}")

def ipc_send_message(message):
    child_conn.send(message)
    print(f"Message sent: {message}")
    logging.info(f"Message sent: {message}")


def ipc_receive_message():
    log_file_path = 'Advanced_Process_Manager.log'
    received_messages = []

    if not os.path.exists(log_file_path):
        print("Log file not found")
        return

    with open(log_file_path, 'r') as log_file:
        lines = log_file.readlines()
        for line in lines:
            if "Message sent: " in line:
                message = line.split("Message sent: ")[1].strip()
                received_messages.append(message)

    if received_messages:
        print("Received Messages:")
        for message in received_messages:
            print(message)
    else:
        print("No message available")


def process_synchronization():
    print("Demonstrating process synchronization using multiprocessing:")
    logging.info("Demonstrating process synchronization using multiprocessing:")

    q = multiprocessing.Queue()
    producer_process = multiprocessing.Process(target=producer, args=(q,))
    consumer_process = multiprocessing.Process(target=consumer, args=(q,))

    producer_process.start()
    consumer_process.start()

    producer_process.join()
    q.put(None)
    consumer_process.join()

    print("Process synchronization demonstration complete.")
    logging.info("Process synchronization demonstration complete.")

def clear_log():
    # Add code to clear the log file here
    with open('Advanced_Process_Manager.log', 'w') as log_file:
        log_file.truncate()
    print("Log file cleared.")
    logging.info("Log file cleared.")

if __name__ == '__main__':
    while True:
        print("Options:")
        for key, value in choices.items():
            print(f"{key}) {value}")

        choice = input("Enter choice: ")

        if choice == "1":
            process_name = input("Enter process name: ")
            create_process(process_name)

        elif choice == "2":
            list_processes()

        elif choice == "3":
            thread_name = input("Enter thread name: ")
            create_thread(thread_name)

        elif choice == "4":
            thread_name = input("Enter the name of the thread to terminate: ")
            terminate_thread(thread_name)

        elif choice == "5":
            message = input("Enter IPC message: ")
            ipc_send_message(message)

        elif choice == "6":
            ipc_receive_message()

        elif choice == "7":
            process_synchronization()

        elif choice == "8":
            clear_log()

        elif choice == "9":
            print("Exited successfully")
            exit(0)
