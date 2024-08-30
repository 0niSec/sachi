from rich import print
from rich.table import Table

def print_banner() -> None:
    banner = """[blue]
   _____               __     _ 
  / ___/ ____ _ _____ / /_   (_)
  \__ \ / __ `// ___// __ \ / / 
 ___/ // /_/ // /__ / / / // /  
/____/ \__,_/ \___//_/ /_//_/ [red]サーチ[/red][/blue]

[gold1]:laptop_computer: https://github.com/0niSec/sachi[/gold1]                               
    """
    print(banner)

def print_info(url, wordlist, blacklist, workers, timeout, redirects=0):
    """Prints the information about the scan.
    
    Parameters:
        url (str): The URL to scan.
        wordlist (str): The wordlist to use.
        blacklist (list): The blacklist to use.
        workers (int): The number of workers to use.
        timeout (int): The timeout to use.

    Returns:
        None
    """
    table = Table(show_header=False, expand=False, box=None, padding=(0, 2), pad_edge=False)
    table.add_row("[+] URL:", f"{url}")
    table.add_row("[+] Wordlist:", f"{wordlist}")
    table.add_row("[+] Blacklist:", ", ".join(str(v) for v in blacklist))
    table.add_row("[+] Workers:", f"{workers}")
    table.add_row("[+] Timeout:", f"{timeout}")
    if redirects > 0:
        table.add_row("[+] Max Redirects:", f"{redirects}")

    print("=" * 120)
    print(table)
    print("=" * 120)

