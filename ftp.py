import tkinter as tk
from tkinter import Text
import threading
import sys
from wordlist import wordlist_attack  # Import the wordlist_attack function
from bruteforce import brute_force_attack  # Import the brute_force_attack function
from ddos import perform_ddos  # Import the perform_ddos function

# Create a stop event
stop_event = threading.Event()

def bruteforce_attack_ui(hostname, port, username):
    output_text.insert(tk.END, f"Starting Bruteforce Attack on {hostname}:{port} as {username}...\n")

    # Function to run the brute force attack in a separate thread
    def run_bruteforce():
        try:
            brute_force_attack(hostname, username, output_text, stop_event)  # Pass the output_text widget and stop_event
        except Exception as e:
            output_text.insert(tk.END, f"[X] An error occurred during the brute force attack: {e}\n")

    # Start the brute force attack in a new thread
    threading.Thread(target=run_bruteforce).start()

def wordlist_attack_ui(hostname, port, username, wordlist):
    output_text.delete(1.0, tk.END)  # Clear previous output

    try:
        port = int(port)  # Convert port to integer
    except ValueError:
        output_text.insert(tk.END, "[!] Invalid port number. Please enter a valid integer.\n")
        return

    def capture_output():
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = TextRedirector(output_text, "stdout")
        sys.stderr = TextRedirector(output_text, "stderr")
        
        try:
            wordlist_attack(hostname, port, username, wordlist) 
        except Exception as e:
            output_text.insert(tk.END, f"[X] An error occurred: {e}\n")
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    threading.Thread(target=capture_output).start()

def ddos_attack_ui(hostname, port, username, password):
    output_text.insert(tk.END, f"Starting DDOS Attack on {hostname}:{port} as {username}...\n")

    # Start the DDoS attack in a separate thread
    threading.Thread(target=perform_ddos, args=(hostname, port, username, password, output_text, stop_event)).start()

class TextRedirector:
    def __init__(self, widget, tag):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass

def create_menu():
    global output_text
    root = tk.Tk()
    root.title("FTP Attack Menu")

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
    banner_text.insert(tk.END, banner)
    banner_text.config(state=tk.DISABLED)  # Make it read-only
    banner_text.pack(pady=10)

    # Input Fields
    tk.Label(root, text="Hostname:", fg="white", bg="#778899").pack(pady=5)
    hostname_entry = tk.Entry(root, width=30)
    hostname_entry.pack(pady=5)

    tk.Label(root, text="Port:", fg="white", bg="#778899").pack(pady=5)
    port_entry = tk.Entry(root, width=30)
    port_entry.pack(pady=5)

    tk.Label(root, text="Username:", fg="white", bg="#778899").pack(pady=5)
    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)

    tk.Label(root, text="Wordlist:", fg="white", bg="#778899").pack(pady=5)
    wordlist_entry = tk.Entry(root, width=30)
    wordlist_entry.pack(pady=5)
    
    tk.Label(root, text="Password:", fg="white", bg="#778899").pack(pady=5)
    password_entry = tk.Entry(root, width=30) 
    password_entry.pack(pady=5)

    # Frame for Buttons
    button_frame = tk.Frame(root, bg="#778899")
    button_frame.pack(pady=10)

    # Buttons
    btn_wordlist = tk.Button(button_frame, text="Wordlist Attack", command=lambda: wordlist_attack_ui(hostname_entry.get(), port_entry.get(), username_entry.get(), wordlist_entry.get()), bg="#778899", fg="white")
    btn_wordlist.pack(side=tk.LEFT, padx=5)

    btn_bruteforce = tk.Button(button_frame, text="Bruteforce Attack", command=lambda: bruteforce_attack_ui(hostname_entry.get(), port_entry.get(), username_entry.get()), bg="#778899", fg="white")
    btn_bruteforce.pack(side=tk.LEFT, padx=5)

    btn_ddos = tk.Button(button_frame, text="DDOS Attack", command=lambda: ddos_attack_ui(hostname_entry.get(), port_entry.get(), username_entry.get(), password_entry.get()), bg="#778899", fg="white")
    btn_ddos.pack(side=tk.LEFT, padx=5)

    # Button to stop attacks
    stop_button = tk.Button(button_frame, text="Stop Attack", command=lambda: stop_attacks(), bg="#778899", fg="red")
    stop_button.pack(side=tk.LEFT, padx=5)

    # Output Text Widget
    output_text = Text(root, height=20, width=80, bg="#2C3E50", fg="white", wrap="word")
    output_text.pack(pady=10)

    root.mainloop()

def stop_attacks():
    stop_event.set()  # Signal to stop the attacks

def start_bruteforce():
    host = hostname_entry.get()
    user = username_entry.get()
    password = password_entry.get()
    threading.Thread(target=brute_force_attack, args=(host, user, output_text, stop_event)).start()  # Include stop_event

if __name__ == "__main__":
    create_menu()