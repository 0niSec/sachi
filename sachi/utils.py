from rich.console import Console
import os

def collect_words(wordlist_file):
    """Collect the words from the wordlist file and yield the words
    
    Parameters:
        wordlist_file (str): The wordlist file to read from.

    Yields:
        str: The word from the wordlist file.
    """
    with open(wordlist_file, 'r') as f:
        for line in f:
            if line.startswith('#'): # Ignore commented lines
                continue
            word = line.strip()
            
            if word:
                yield word
            else:
                yield '/'

def validate_wordlist(wordlist) -> bool:
    """Validate the wordlist argument
    
    Parameters:
        wordlist (str): The wordlist file to read from.

    Raises:
        FileNotFoundError: If the wordlist file does not exist.
        PermissionError: If the wordlist file is not readable.
        ValueError: If the wordlist file is empty.

    Returns:
        bool: True if the wordlist file is valid, False otherwise.
    """
    if not os.path.exists(wordlist):
        raise FileNotFoundError(f"Wordlist file '{wordlist}' not found.")
    
    if not os.access(wordlist, os.R_OK):
        raise PermissionError(f"Permission denied to read '{wordlist}'.")
    
    if os.path.getsize(wordlist) == 0:
        raise ValueError(f"Wordlist file '{wordlist}' is empty.")
    
    return True

def setup_console(no_color) -> Console:
    """Setup the console
    
    Parameters:
        no_color (bool): Whether to disable color output.

    Returns:
        Console: The console object.
    """
    return Console(color_system=None if no_color else "auto")

    