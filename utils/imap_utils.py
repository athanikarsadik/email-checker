import imaplib
import socket
import time
import socks

def get_imap_server(email, config):
    """Gets the IMAP server address for an email address.

    Args:
        email (str): The email address.
        config (dict): The configuration settings.

    Returns:
        str: The IMAP server address, or None if not found.
    """

    domain = email.split('@')[1]
    imap_providers = config["imap_providers"]

    if domain in imap_providers:
        return imap_providers[domain]
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
    fallback_server = "imap.gmail.com"

    for prefix in prefixes:
        server = f"{prefix}{domain}"
        if test_imap_connection(server, config):
            update_imap_providers(config, domain, server)
            return server

    if test_imap_connection(fallback_server, config):
        update_imap_providers(config, domain, fallback_server)
        return fallback_server

    return None

def test_imap_connection(server, config):
    """Tests the IMAP connection to a server using a rotating proxy."""

    proxy_host, proxy_port, proxy_user, proxy_pass = config["proxy"].split(":")
    print("test_imap_connection")
    for attempt in range(config["retry_attempts"]):
        try:
            # Create a custom socket
            proxy_type = socks.HTTP  # Use socks.SOCKS4 or socks.SOCKS5 if needed
            s = socks.socksocket()
            s.set_proxy(proxy_type, proxy_host, int(proxy_port), True, proxy_user, proxy_pass)
            s.connect((server, 993))  # Connect to the IMAP server on port 993

            # Create the IMAP object 
            imap = imaplib.IMAP4_SSL(server, ssl_context=None) 

            # Replace the IMAP's socket with the custom socket
            imap.sock = s

            return True  # Connection successful
        except (imaplib.IMAP4.error, socket.gaierror, socket.timeout) as e:
            print(f"Connection error to {server}: {e}. Retrying...")
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
    """Validates an email address using a rotating proxy."""
    proxy_host, proxy_port, proxy_user, proxy_pass = config["proxy"].split(":")

    for attempt in range(config["retry_attempts"]):
        print(attempt)
        try:
            # Create a custom socket (same as in test_imap_connection)
            proxy_type = socks.HTTP  # Use socks.SOCKS4 or socks.SOCKS5 if needed
            s = socks.socksocket()
            s.set_proxy(proxy_type, proxy_host, int(proxy_port), True, proxy_user, proxy_pass)
            s.connect((imap_server, 993))  # Connect to the IMAP server on port 993

            # Create the IMAP object 
            imap = imaplib.IMAP4_SSL(imap_server, ssl_context=None) 

            # Replace the IMAP's socket with the custom socket
            imap.sock = s

            imap.login(email, password)
            imap.logout()
            return True  # Login successful

        except imaplib.IMAP4.error as e:
            if "Invalid credentials" in str(e):
                return False  # Invalid credentials, no need to retry
            else:
                print(f"Login error for {email}: {e}. Retrying...")
                time.sleep(config["retry_timeout"])
        except (socket.gaierror, socket.timeout) as e:
            print(f"Connection error for {email}: {e}. Retrying...")
            time.sleep(config["retry_timeout"])

    return False

    # """Validates an email address by attempting to log in to the IMAP server.

    # Args:
    #     email (str): The email address.
    #     password (str): The password for the email account.
    #     imap_server (str): The IMAP server address.
    #     config (dict): The configuration settings.

    # Returns:
    #     bool: True if the email is valid (login successful), False otherwise.
    # Validates an email address using a rotating proxy."""

    # proxy_host, proxy_port, proxy_user, proxy_pass = config["proxy"].split(":")

    # for attempt in range(config["retry_attempts"]):
    #     try:
    #         with imaplib.IMAP4_SSL(imap_server) as imap:
    #             imap.socket.setproxy(
    #                 socket.PROXY_TYPE_HTTP, proxy_host, int(proxy_port), proxy_user, proxy_pass
    #             )
    #             imap.login(email, password)
    #             imap.logout()
    #             return True  # Login successful
    #     except imaplib.IMAP4.error as e:
    #         if "Invalid credentials" in str(e):
    #             return False  # Invalid credentials, no need to retry
    #         else:
    #             print(f"Login error for {email}: {e}. Retrying...")
    #             time.sleep(config["retry_timeout"])
    #     except (socket.gaierror, socket.timeout) as e:
    #         print(f"Connection error for {email}: {e}. Retrying...")
    #         time.sleep(config["retry_timeout"])

    # return False  # Login failed after all retries