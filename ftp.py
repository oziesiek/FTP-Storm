import tkinter as tk  # Import tkinter for GUI components
from tkinter import Text  # Import Text widget for displaying output
import threading  # Import threading for concurrent execution
import sys  # Import sys for system-specific parameters and functions
from wordlist import wordlist_attack  # Import the wordlist_attack function for brute force attacks
from bruteforce import brute_force_attack  # Import the brute_force_attack function for brute force attacks
from ddos import perform_ddos  # Import the perform_ddos function for DDoS attacks

# Create a stop event to signal when to stop attacks
stop_event = threading.Event()

def bruteforce_attack_ui(hostname, port, username):
    """Start the brute force attack using the provided hostname, port, and username."""
    output_text.insert(tk.END, f"Starting Bruteforce Attack on {hostname}:{port} as {username}...\n")  # Log the start of the attack

    # Function to run the brute force attack in a separate thread
    def run_bruteforce():
        try:
            brute_force_attack(hostname, username, output_text, stop_event)  # Call the brute force attack function
        except Exception as e:
            output_text.insert(tk.END, f"[X] An error occurred during the brute force attack: {e}\n")  # Log any errors

    # Start the brute force attack in a new thread
    threading.Thread(target=run_bruteforce).start()

def wordlist_attack_ui(hostname, port, username, wordlist):
    """Start the wordlist attack using the provided hostname, port, username, and wordlist."""
    output_text.delete(1.0, tk.END)  # Clear previous output

    try:
        port = int(port)  # Convert port to integer
    except ValueError:
        output_text.insert(tk.END, "[!] Invalid port number. Please enter a valid integer.\n")  # Log invalid port error
        return  # Exit the function if the port is invalid

    def capture_output():
        """Capture output from the wordlist attack and redirect it to the output_text widget."""
        original_stdout = sys.stdout  # Save the original stdout
        original_stderr = sys.stderr  # Save the original stderr
        sys.stdout = TextRedirector(output_text, "stdout")  # Redirect stdout to the output_text widget
        sys.stderr = TextRedirector(output_text, "stderr")  # Redirect stderr to the output_text widget
        
        try:
            wordlist_attack(hostname, port, username, wordlist)  # Call the wordlist attack function
        except Exception as e:
            output_text.insert(tk.END, f"[X] An error occurred: {e}\n")  # Log any errors
        finally:
            sys.stdout = original_stdout  # Restore original stdout
            sys.stderr = original_stderr  # Restore original stderr

    # Start the wordlist attack in a new thread
    threading.Thread(target=capture_output).start()

def ddos_attack_ui(hostname, port, username, password):
    """Start the DDoS attack using the provided hostname, port, username, and password."""
    output_text.insert(tk.END, f"Starting DDOS Attack on {hostname}:{port} as {username}...\n")  # Log the start of the attack

    # Start the DDoS attack in a separate thread
    threading.Thread(target=perform_ddos, args=(hostname, port, username, password, output_text, stop_event)).start()

class TextRedirector:
    """Class to redirect output to a tkinter Text widget."""
    def __init__(self, widget, tag):
        self.widget = widget  # Store the Text widget
        self.tag = tag  # Store the tag for text formatting

    def write(self, str):
        """Write a string to the Text widget."""
        self.widget.insert(tk.END, str, (self.tag,))  # Insert the string with the specified tag
        self.widget.see(tk.END)  # Scroll to the end of the Text widget

    def flush(self):
        """Flush method for compatibility with file-like objects."""
        pass  # No action needed for flush

def create_menu():
    """Create the main GUI menu for the FTP attack application."""
    global output_text  # Declare output_text as a global variable
    root = tk.Tk()  # Create the main window
    root.title("FTP Attack Menu")  # Set the window title

    # Set the background color of the main window
    root.configure(bg="#778899")

    # Banner
    banner = r"""      
____ ___ ___     ____ ___ ____ ____ _  _ 
|___  |  |__]    [__   |  |  | |__/ |\/| 
|     |  |       ___]  |  |__| |  \ |  |                                          
                            by Oziesiek
    """

    # Banner Text Widget
    banner_text = Text(root, font=("Courier", 20), fg="#2C3E50", bg="#778899", wrap="word", height=6, width=40)
    banner_text.insert(tk.END, banner)  # Insert the banner text
    banner_text.config(state=tk.DISABLED)  # Make it read-only
    banner_text.pack(pady=10)  # Add padding

    # Input Fields
    tk.Label(root, text="Hostname:", fg="white", bg="#778899").pack(pady=5)  # Label for hostname
    hostname_entry = tk.Entry(root, width=30)  # Entry for hostname
    hostname_entry.pack(pady=5)  # Add padding

    tk.Label(root, text="Port:", fg="white", bg="#778899").pack(pady=5)  # Label for port
    port_entry = tk.Entry(root, width=30)  # Entry for port
    port_entry.pack(pady=5)  # Add padding

    tk.Label(root, text="Username:", fg="white", bg="#778899").pack(pady=5)  # Label for username
    username_entry = tk.Entry(root, width=30)  # Entry for username
    username_entry.pack(pady=5)  # Add padding

    tk.Label(root, text="Wordlist:", fg="white", bg="#778899").pack(pady=5)  # Label for wordlist
    wordlist_entry = tk.Entry(root, width=30)  # Entry for wordlist
    wordlist_entry.pack(pady=5)  # Add padding
    
    tk.Label(root, text="Password:", fg="white", bg="#778899").pack(pady=5)  # Label for password
    password_entry = tk.Entry(root, width=30)  # Entry for password
    password_entry.pack(pady=5)  # Add padding

    # Frame for Buttons
    button_frame = tk.Frame(root, bg="#778899")  # Create a frame for buttons
    button_frame.pack(pady=10)  # Add padding

    # Buttons
    btn_wordlist = tk.Button(button_frame, text="Wordlist Attack", command=lambda: wordlist_attack_ui(hostname_entry.get(), port_entry.get(), username_entry.get(), wordlist_entry.get()), bg="#778899", fg="white")  # Button for wordlist attack
    btn_wordlist.pack(side=tk.LEFT, padx=5)  # Add padding

    btn_bruteforce = tk.Button(button_frame, text="Bruteforce Attack", command=lambda: bruteforce_attack_ui(hostname_entry.get(), port_entry.get(), username_entry.get()), bg="#778899", fg="white")  # Button for brute force attack
    btn_bruteforce.pack(side=tk.LEFT, padx=5)  # Add padding

    btn_ddos = tk.Button(button_frame, text="DDOS Attack", command=lambda: ddos_attack_ui(hostname_entry.get(), port_entry.get(), username_entry.get(), password_entry.get()), bg="#778899", fg="white")  # Button for DDoS attack
    btn_ddos.pack(side=tk.LEFT, padx=5)  # Add padding

    # Button to stop attacks
    stop_button = tk.Button(button_frame, text="Stop Attack", command=lambda: stop_attacks(), bg="#778899", fg="red")  # Button to stop attacks
    stop_button.pack(side=tk.LEFT, padx=5)  # Add padding

    # Output Text Widget
    output_text = Text(root, height=20, width=80, bg="#2C3E50", fg="white", wrap="word")  # Create a Text widget for output
    output_text.pack(pady=10)  # Add padding

    root.mainloop()  # Start the GUI event loop

def stop_attacks():
    """Signal to stop all ongoing attacks."""
    stop_event.set()  # Set the stop event to signal all threads to stop

def start_bruteforce():
    """Start the brute force attack using the provided credentials."""
    host = hostname_entry.get()  # Get hostname from entry
    user = username_entry.get()  # Get username from entry
    password = password_entry.get()  # Get password from entry
    threading.Thread(target=brute_force_attack, args=(host, user, output_text, stop_event)).start()  # Start the brute force attack in a new thread

# Entry point of the program
if __name__ == "__main__":
    create_menu()  # Create the GUI menu