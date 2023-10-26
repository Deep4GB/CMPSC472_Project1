import os
import sys
import threading
import time
import multiprocessing
import logging
import psutil
import tkinter as tk
from tkinter import scrolledtext
import signal

# Initialize logging
logging.basicConfig(filename='process_manager.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Track the previous choice
previous_choice = None

# Initialize the result variable as a global
result = ""

# Create a dictionary to keep track of running processes
running_processes = {}


# Function to create a new process
def create_process(process_name, command):
    pid = os.fork()
    if pid == 0:
        try:
            # Execute the specified command in the child process
            os.execlp(command, command)
        except Exception as e:
            logging.error(f"Child process '{process_name}' with PID {os.getpid()} failed to execute: {str(e)}")
            log_text.insert(tk.END,
                            f"Child process '{process_name}' with PID {os.getpid()} failed to execute: {str(e)}\n")
        os._exit(1)
    else:
        running_processes[pid] = process_name
        logging.info(f"Child process '{process_name}' with PID {pid} created.")
        log_text.insert(tk.END, f"Child process '{process_name}' with PID {pid} created.\n")


# Function to terminate a process
def terminate_process(process_pid):
    try:
        os.kill(process_pid, signal.SIGTERM)
        del running_processes[process_pid]
        logging.info(f"Terminated process with PID {process_pid}.")
        log_text.insert(tk.END, f"Terminated process with PID {process_pid}.\n")
    except ProcessLookupError:
        logging.error(f"Process with PID {process_pid} not found.")
        log_text.insert(tk.END, f"Process with PID {process_pid} not found.\n")


# Function to list running processes
def list_processes():
    process_list = "List of running processes:\n"
    logging.info("List of running processes:")
    for proc in psutil.process_iter(attrs=['pid', 'name', 'status']):
        process_info = proc.info
        process_list += f"Process with PID: {process_info['pid']}, Name: {process_info['name']}, Status: {process_info['status']}\n"
        logging.info(
            f"Process with PID: {process_info['pid']}, Name: {process_info['name']}, Status: {process_info['status']}")
    log_text.insert(tk.END, process_list)


# Function to create a new thread
def create_thread(thread_name):
    thread = threading.Thread(target=thread_function, args=(thread_name,))
    thread.start()
    log_text.insert(tk.END, f"Thread '{thread_name}' started.\n")


# Function for the thread's activity
def thread_function(thread_name):
    log_text.insert(tk.END, f"Thread '{thread_name}' running.\n")
    time.sleep(2)
    log_text.insert(tk.END, f"Thread '{thread_name}' finished.\n")


# Function for inter-process communication (IPC)
def ipc_message_passing(message):
    log_text.insert(tk.END, f"IPC: Sending message - '{message}'\n")


# Function to demonstrate process synchronization
def process_synchronization():
    global result
    result = "Demonstrating process synchronization using multiprocessing:\n"
    logging.info("Demonstrating process synchronization using multiprocessing:")

    # Producer function for the synchronization demonstration
    def producer(q):
        for item in range(5):
            q.put(item)
            log_text.insert(tk.END, f"Producing item {item}\n")
            logging.info(f"Producing item {item}")

    # Consumer function for the synchronization demonstration
    def consumer(q):
        for item in iter(q.get, None):
            log_text.insert(tk.END, f"Consuming item {item}\n")
            logging.info(f"Consuming item {item}")

    q = multiprocessing.Queue()
    producer_process = multiprocessing.Process(target=producer, args=(q,))
    consumer_process = multiprocessing.Process(target=consumer, args=(q,))

    producer_process.start()
    consumer_process.start()

    producer_process.join()
    q.put(None)
    consumer_process.join()

    result += "Process synchronization demonstration complete."
    log_text.insert(tk.END, result)


# Function to handle showing input fields based on the user's choice
def show_inputs():
    global previous_choice
    choice = choice_var.get()

    # Hide input fields for the previous choice
    if previous_choice == '1':
        process_name_label.grid_remove()
        process_name_entry.grid_remove()
        command_label.grid_remove()
        command_entry.grid_remove()
    elif previous_choice == '3':
        thread_name_label.grid_remove()
        thread_name_entry.grid_remove()
    elif previous_choice == '4':
        ipc_message_label.grid_remove()
        ipc_message_entry.grid_remove()

    # Show input fields for the current choice
    if choice == '1':
        process_name_label.grid()
        process_name_entry.grid()
        command_label.grid()
        command_entry.grid()
    elif choice == '3':
        thread_name_label.grid()
        thread_name_entry.grid()
    elif choice == '4':
        ipc_message_label.grid()
        ipc_message_entry.grid()

    previous_choice = choice


# Function to handle the user's option selection
def on_option_selected():
    choice = choice_var.get()
    logging.info(f"User selected choice: {choice}")
    show_inputs()

    if choice == '1':
        process_name = process_name_entry.get()
        command = command_entry.get()  # Get the command to run
        create_process(process_name, command)
    elif choice == '2':
        list_processes()
    elif choice == '3':
        thread_name = thread_name_entry.get()
        create_thread(thread_name)
    elif choice == '4':
        ipc_message = ipc_message_entry.get()
        ipc_message_passing(ipc_message)
    elif choice == '5':
        process_synchronization()
    elif choice == '6':
        root.destroy()


# Create the main application window
root = tk.Tk()
root.title("Process Manager")

# Create a frame for organizing the elements
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# Create a label for the options
choice_label = tk.Label(frame, text="Options:")
choice_label.grid(row=0, column=0, sticky="w")

# Create a variable to hold the choice
choice_var = tk.StringVar(value='1')

# Define the available choices
choices = [
    ("Create Process", '1'),
    ("List Processes", '2'),
    ("Create Thread", '3'),
    ("IPC: Send Message", '4'),
    ("Process Synchronization", '5'),
    ("Exit", '6')
]

row = 1
for text, val in choices:
    radio = tk.Radiobutton(frame, text=text, variable=choice_var, value=val, command=show_inputs)
    radio.grid(row=row, column=0, sticky="w")
    row += 1

# Create input fields for process creation
process_name_label = tk.Label(frame, text="Enter process name:")
process_name_entry = tk.Entry(frame)

command_label = tk.Label(frame, text="Enter command:")
command_entry = tk.Entry(frame)

# Create input field for thread creation
thread_name_label = tk.Label(frame, text="Enter thread name:")
thread_name_entry = tk.Entry(frame)

# Create input field for IPC message
ipc_message_label = tk.Label(frame, text="Enter IPC message:")
ipc_message_entry = tk.Entry(frame)

# Create a button to execute the selected action
process_button = tk.Button(frame, text="Execute", command=on_option_selected)
process_button.grid(row=row, column=0, columnspan=2)

# Create a text area for displaying log messages
log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
log_text.pack(padx=20, pady=20)

# Initially show/hide inputs based on the selected option
show_inputs()

# Start the main application loop
root.mainloop()
