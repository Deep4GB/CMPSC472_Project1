# Advanced Process Manager with Process Synchronization

## Implemented Functionalities
1. **Process and Thread Management:** This program allows you to create and manage processes and threads. You can create new threads with custom names and terminate them when needed.

2. **Process Listing:** The tool provides the capability to list running processes and displays details about each process, such as the process ID, parent process ID, and its current state.

3. **Inter-Process Communication (IPC):** It enables communication between processes through IPC. You can send and receive messages between processes using pipes.

4. **Process Synchronization:** The tool demonstrates process synchronization using a mutex. It showcases how to use a mutex to synchronize access to shared resources and ensure that multiple processes or threads can safely access critical sections of code.

5. **Producer-Consumer Problem:** The program addresses the classic producer-consumer problem using semaphores. It creates a shared buffer, and multiple producer and consumer threads interact with the buffer, ensuring that producers don't produce when the buffer is full and consumers don't consume when it's empty.

## Installation
- To use this advanced process manager, simply import the necessary libraries and run the `main.py` file.
- The tool generates a process manager log file that contains comprehensive logs of the program's activities, helping you monitor the execution and diagnose issues effectively.

## Function Explanations / Design
### `process_function(process_name)`
- This function is executed within child processes.
- It logs the running state of a child process and allows you to create threads, list threads, and exit the process.

### `create_process(process_name)`
- Creates a new process with the given name.
- Uses `os.fork()` to fork a child process and `os.execlp()` to run the specified program.
- Manages the list of running processes and logs their creation.

### `list_processes()`
- Displays a menu to list running processes.
- Provides options to list processes created through your code and all processes on the computer.
- Retrieves process details, such as PID, parent PID, name, and status, using the `psutil` library.

### `create_thread(thread_name)`
- Creates a new thread within the current process.
- Uses the `ctypes` library to create a thread and logs the successful creation.

### `terminate_thread(thread_name)`
- Terminates a thread with the specified name.
- Sets an exit signal to indicate the thread should exit.
- Uses `ctypes` to call `pthread_join` to terminate the thread.

### `list_threads()`
- Lists threads within the current process.
- Retrieves thread IDs and names for display.

### `ipc_send_message(message)`
- Sends an Inter-Process Communication (IPC) message through a pipe.
- Encodes and writes the message to the pipe for communication.

### `ipc_receive_message()`
- Receives an IPC message from a pipe.
- Checks for available data in the pipe, reads and decodes the message, and logs it.

### `producer()`
- Represents the producer function for a producer-consumer example.
- Produces items, acquires semaphores for empty slots and mutex for buffer access, and adds items to the buffer.
- Logs the produced items and simulates work with random delays.

### `consumer()`
- Represents the consumer function for a producer-consumer example.
- Consumes items from the buffer, acquires semaphores for filled slots and mutex for buffer access.
- Logs the consumed items and simulates work with random delays.

### `process_synchronization()`
- Demonstrates process synchronization for the producer-consumer example.
- Creates producer and consumer threads and manages their execution.
- Ensures synchronization using semaphores for empty and filled slots.

### `clear_log_file()`
- Clears the log file named 'Advanced_Process_Manager.log'.
- Opens the file and truncates its content, effectively clearing the log.

### Main Entry Point
- Executes when the script is run.
- Displays a menu to interact with different functionalities, including creating processes, threads, terminating threads, monitoring processes, IPC messaging, process synchronization, clearing log files, and exiting the program.

### `process_function(process_name)`
- This function is executed within child processes.
- It logs the running state of a child process and allows you to create threads, list threads, and exit the process.

### `create_process(process_name)`
- Creates a new process with the given name.
- Uses `os.fork()` to fork a child process and `os.execlp()` to run the specified program.
- Manages the list of running processes and logs their creation.

### `list_processes()`
- Displays a menu to list running processes.
- Provides options to list processes created through your code and all processes on the computer.
- Retrieves process details, such as PID, parent PID, name, and status, using the `psutil` library.

### `create_thread(thread_name)`
- Creates a new thread within the current process.
- Uses the `ctypes` library to create a thread and logs the successful creation.

### `terminate_thread(thread_name)`
- Terminates a thread with the specified name.
- Sets an exit signal to indicate the thread should exit.
- Uses `ctypes` to call `pthread_join` to terminate the thread.

### `list_threads()`
- Lists threads within the current process.
- Retrieves thread IDs and names for display.

### `ipc_send_message(message)`
- Sends an Inter-Process Communication (IPC) message through a pipe.
- Encodes and writes the message to the pipe for communication.

### `ipc_receive_message()`
- Receives an IPC message from a pipe.
- Checks for available data in the pipe, reads and decodes the message, and logs it.

### `producer()`
- Represents the producer function for a producer-consumer example.
- Produces items, acquires semaphores for empty slots and mutex for buffer access, and adds items to the buffer.
- Logs the produced items and simulates work with random delays.

### `consumer()`
- Represents the consumer function for a producer-consumer example.
- Consumes items from the buffer, acquires semaphores for filled slots and mutex for buffer access.
- Logs the consumed items and simulates work with random delays.

### `process_synchronization()`
- Demonstrates process synchronization for the producer-consumer example.
- Creates producer and consumer threads and manages their execution.
- Ensures synchronization using semaphores for empty and filled slots.

### `clear_log_file()`
- Clears the log file named 'Advanced_Process_Manager.log'.
- Opens the file and truncates its content, effectively clearing the log.

### Main Entry Point
- Executes when the script is run.
- Displays a menu to interact with different functionalities, including creating processes, threads, terminating threads, monitoring processes, IPC messaging, process synchronization, clearing log files, and exiting the program.

## Results & Explanation
The advanced process manager, enhanced with synchronization mechanisms, offers an efficient solution for the management and monitoring of processes and threads. It plays a crucial role in ensuring synchronization to prevent data corruption and conflicts over shared resources. This tool serves as an invaluable resource for comprehending and implementing synchronization mechanisms, particularly in scenarios involving common challenges like producer-consumer and reader-writer problems.

By exploring the `Advanced_Process_Manager.log` file, you can gain insight into how the program logs its activities. The 'Results' folder contains illustrative images demonstrating the functionality of the various features. It's important to note that all functions within the program are equipped with robust error handling. In the event of warnings or errors, the program will both print and log these issues for your reference and troubleshooting.

## Discussion
The program showcases how synchronization mechanisms like semaphores and mutexes can be applied to solve common synchronization problems encountered in multi-process and multi-threaded applications. It offers a practical understanding of how to protect shared resources and coordinate the execution of multiple processes and threads.

## Conclusion
In conclusion, this advanced process manager with process synchronization is a valuable tool for both learning and practical implementation. It equips users with the knowledge and tools needed to manage processes and threads effectively, ensuring secure data access and minimizing conflicts. It's a valuable addition to any developer's toolkit when working with concurrent and parallel processing.
