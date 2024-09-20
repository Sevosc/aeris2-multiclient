import subprocess
import os
import time
import pyuac
import psutil
import logging

# Set the working directory where the game expects to be launched
WORKING_DIR = r"C:\Games\Aeris2Client"

# Set up logging
logging.basicConfig(filename='game_launcher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_hard_link(target_name, link_name):
    """Creates a hard link in the working directory if it does not already exist."""
    target_path = os.path.join(WORKING_DIR, target_name)
    link_path = os.path.join(WORKING_DIR, link_name)

    if not os.path.exists(link_path):
        try:
            os.link(target_path, link_path)
            logging.info(f"Created hard link: {link_name} -> {target_name}")
        except Exception as e:
            logging.error(f"Failed to create hard link {link_name}: {str(e)}")
    else:
        logging.info(f"Hard link {link_name} already exists.")


def launch_game(binary_name):
    """Launches the game binary in a new console window."""
    binary_path = os.path.join(WORKING_DIR, binary_name)

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        subprocess.Popen(
            ["cmd", "/c", binary_path],
            cwd=WORKING_DIR,
            startupinfo=startupinfo
        )
        logging.info(f"Game launched: {binary_name}")
    except Exception as e:
        logging.error(f"Failed to launch the game: {str(e)}")


def list_available_clients():
    """Lists available client binaries and marks those currently running."""
    client_binaries = [
        f for f in os.listdir(WORKING_DIR)
        if f.startswith("metin2client") and f.endswith(".bin")
    ]

    client_numbers = sorted(
        int(f[len("metin2client"):].split(".")[0]) for f in client_binaries if f[len("metin2client"):].split(".")[0].isdigit()
    )

    running_clients = set()
    for proc in psutil.process_iter(attrs=['name']):
        proc_name = proc.info.get('name', '')
        if proc_name.startswith("metin2client"):
            number_part = proc_name.split("metin2client")[-1].split(".")[0]
            if number_part.isdigit():
                running_clients.add(int(number_part))

    normal_client_running = any(proc.name() == "metin2client.bin" for proc in psutil.process_iter(attrs=['name']))

    print(f"- 1 (Normal client) {'(Running)' if normal_client_running else ''}")
    
    for number in client_numbers:
        print(f"- {number} {'(Running)' if number in running_clients else ''}")


def start_single_client():
    """Prompts for and starts a single specific client or the normal client."""
    print("Available clients:")
    list_available_clients()

    client_number = input("\nTo start the normal client, enter 1.\nEnter the number of the specific client to start: ").strip()

    if client_number == "1":
        client_name = "metin2client.bin"
    else:
        try:
            client_name = f"metin2client{int(client_number)}.bin"
        except ValueError:
            logging.error("Invalid number entered.")
            print("Invalid number entered.")
            return

    if not os.path.isfile(os.path.join(WORKING_DIR, client_name)):
        logging.error(f"File {client_name} does not exist in the working directory.")
        print(f"File {client_name} does not exist.")
        return

    launch_game(client_name)


def start_multiple_clients():
    """Prompts for and starts multiple normal and proxy clients."""
    try:
        num_normal_clients = int(input("Enter the number of normal clients to start: "))
        num_proxy_clients = int(input("Enter the number of proxy clients to start: "))
    except ValueError:
        logging.error("Invalid number entered.")
        print("Invalid input, please enter a valid number.")
        return

    for _ in range(num_normal_clients):
        launch_game("metin2client.bin")

    for i in range(2, num_proxy_clients + 2):  # Proxy clients start from 2
        link_name = f"metin2client{i}.bin"
        create_hard_link("metin2client.bin", link_name)
        launch_game(link_name)
        time.sleep(1)


def main():
    """Main function to choose between starting single or multiple clients."""
    print("Choose an option:")
    print("1. Start a single specific client")
    print("2. Start multiple normal and proxy clients")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        start_single_client()
    elif choice == "2":
        start_multiple_clients()
    else:
        logging.error("Invalid choice.")
        print("Invalid choice, please select 1 or 2.")

    logging.info("Script running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Exiting script.")


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        main()  # Already an admin
