# FTP Attack Suite 🚀

Welcome to the **FTP Attack Suite**! This is a collection of tools designed for testing the security of FTP and SFTP servers. Please note that this is still a **pre-release version 0.9** and is not intended for production use.

## Functionality 🛠️

The suite includes the following modules:

1. **ftp.py**: 
   - Provides a graphical user interface (GUI) for initiating various types of attacks on FTP and SFTP servers.
   - Supports brute force attacks and wordlist attacks.

2. **bruteforce.py**: 
   - Implements a brute force attack mechanism to guess passwords for SFTP servers.
   - Utilizes a character set to generate password combinations.

3. **ddos.py**: 
   - Conducts a DDoS attack by uploading random files to the target SFTP server.
   - Designed to simulate high load on the server.

4. **wordlist.py**: 
   - Performs a wordlist attack using a provided list of passwords.
   - Requires a wordlist file to function.

## Requirements 📋

To run this project, you will need the following:

- Python 3.x
- Required libraries:
  - `paramiko`
  - `tkinter`
  - `itertools`
  - `string`
  - `threading`
  - `queue`

You can install the required libraries using pip.

## Features to be Implemented 🔧

- **Dynamic Port Input**: The port number is currently hardcoded. Future versions will allow users to input the port number (defaulting to 22).
- **Variable Password Length**: Currently, the brute force attack only supports a fixed password length of 4 characters. Future versions will allow users to specify the length of character strings.

## Future Plans 🚀

- **Compiled Code**: A compiled version of the code will be introduced in version **1.1** for easier distribution and usage.

## Disclaimer ⚠️

This tool is intended for educational purposes only. Use it responsibly and only on systems you own or have explicit permission to test. Unauthorized access to computer systems is illegal.

---

Feel free to contribute to this project or report any issues you encounter. Happy hacking! 🐾
