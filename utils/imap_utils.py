import imaplib
import socket
import time

import threading

# Create locks for thread safety
output_lock = threading.Lock()
retry_lock = threading.Lock()  # Lock for retry attempts
retry_counts = {}  # Dictionary to store retry counts for each email

def get_imap_server(email, config):
    """Gets the IMAP server address for an email address.

    Args:
        email (str): The email address.
        config (dict): The configuration settings.

    Returns:
        str: The IMAP server address, or None if not found.
    """

    imap_providers = config["imap_providers"]

    domain = email.split('@')[1].lower()
    top_level_domain = ".".join(domain.split('.')[-2:])  # Extract top-level domain

    if domain in imap_providers:
        return imap_providers[domain]
    elif top_level_domain in imap_providers:  # Check for top-level domain
        return imap_providers[top_level_domain]
    else:
        return discover_imap_server(domain, config)

def discover_imap_server(domain, config):
    """Attempts to discover the IMAP server for a domain.

    Args:
        domain (str): The email domain.
        config (dict): The configuration settings.

    Returns:
        str: The discovered IMAP server address, or None if not found.
    """

    prefixes = ["imap.", "mail."]
    fallback_servers = ["outlook.live.com", "imap.gmail.com"] 

    for prefix in prefixes:
        server = f"{prefix}{domain}"
        if test_imap_connection(server, config):
            update_imap_providers(config, domain, server)
            return server

    # If prefixes fail, try fallback servers
    for server in fallback_servers:
        if test_imap_connection(server, config):
            update_imap_providers(config, domain, server)
            return server

    return None 

def test_imap_connection(server, config):
    """Tests the IMAP connection to a server.

    Args:
        server (str): The IMAP server address.
        config (dict): The configuration settings.

    Returns:
        bool: True if the connection is successful (login success or wrong credentials),
              False otherwise.
    """

    for attempt in range(config["retry_attempts"]):
        try:
            with imaplib.IMAP4_SSL(server,timeout=1) as imap:
                return True  # Connection successful, regardless of login
        except (imaplib.IMAP4.error, socket.gaierror, socket.timeout) as e:
            print(f"Connection error to {server}: {e}. Retrying (attempt {attempt}/{config['retry_attempts']})...")
            time.sleep(config["retry_timeout"])

    return False  # Connection failed after all retries

def update_imap_providers(config, domain, server):
    """Updates the imap_providers in the configuration and saves to file.

    Args:
        config (dict): The configuration settings.
        domain (str): The email domain.
        server (str): The discovered IMAP server address.
    """

    config["imap_providers"][domain] = server
    from utils.config import save_config
    save_config(config)
    print(f"IMAP server for {domain} updated to {server} in config file.")
    
def validate_email(email, password, imap_server, config):
    """Validates an email address by attempting to log in to the IMAP server."""
    for attempt in range(config["retry_attempts"]):
        try:
            with imaplib.IMAP4_SSL(imap_server,) as imap:
                imap.login(email, password)
                imap.logout()
                return True  # Login successful
        except (socket.gaierror, socket.timeout) as e: 
            print(f"Connection error for {email}: {e}. Retrying...")
            time.sleep(config["retry_timeout"])
        except imaplib.IMAP4.error as e:
            print(f"IMAP error for {email}: {e}. Not retrying.")
            return False # Stop if not connection error
    print(f"Max retry for {email}. Adding to bad.txt")
    return False