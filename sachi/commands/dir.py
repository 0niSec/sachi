import asyncio
import click
from httpx import Cookies
from rich.console import Console
from ..sachi import Sachi
from ..banner import print_banner, print_info
from ..utils import setup_console, validate_wordlist

def parse_blacklist(ctx, param, value) -> list[int]:
    """Parse the blacklist argument
    
    Parameters:
        ctx: The click context
        param: The click parameter
        value: The value of the blacklist argument

    Returns:
        list[int]: A list of integers representing the blacklist
    """
    if not value:
        return [404]
    return [int(v) for v in value.strip().split(',')]

def workers_callback(ctx, param, value) -> int:
    if value > 100:
        click.confirm("You are about to use a lot of workers that can negatively impact performance. Continue?", abort=True)
    return value

def headers_callback(ctx, param, value) -> dict:
    if not value:
        return {}
    headers = {}
    for header in value:
        key, value = header.split(':')
        headers[key.strip()] = value.strip()
    return headers

def cookies_callback(ctx, param, value) -> Cookies:
    if not value:
        return None
    cookies = Cookies()
    for cookie in value:
        key, value = cookie.split('=')
        cookies.set(key.strip(), value.strip())
    return cookies

async def dir_entrypoint(
        console: Console, 
        url: str, 
        wordlist: str, 
        workers: int, 
        timeout: int, 
        quiet: bool, 
        blacklist: list[int], 
        headers: dict, 
        add_slash: bool,
        cookies: Cookies,
        redirects: int
        ) -> None:
    """Entrypoint for the dir command

    Parameters:
        console: The console to use
        url: The URL to scan
        wordlist: The wordlist to use
        workers: The number of workers to use
        timeout: The timeout to use
        quiet: Whether to be quiet
        blacklist: The blacklist to use
        headers: The headers to use
        add_slash: Whether to add a trailing slash to the URL

    Returns:
        None
    """
    setup_console(console)
    sachi = Sachi(url, wordlist, blacklist, console, timeout, headers, add_slash, cookies, redirects)

    await sachi.validate_url(url)
    validate_wordlist(wordlist)

    if not quiet:
        print_banner()
        print_info(url, wordlist, blacklist, workers, timeout, redirects)

    try:
        await sachi.dirscan(workers)
    except asyncio.CancelledError:
        console.print("\n[bold red]Scan cancelled. Quitting...[/bold red]")
    finally:
        await sachi.close()
    

@click.command()
@click.option('-u', '--url', help='URL to enumerate', required=True)
@click.option('-w', '--wordlist', help='Wordlist to use', required=True)
@click.option('-k', '--workers', help='Number of concurrent workers', callback=workers_callback, type=int, default=10, show_default=True)
@click.option('-t', '--timeout', help='Timeout for requests', type=int, default=10, show_default=True)
@click.option('-H', '--headers', help='Headers to send with the request, -H "Header1: val1" -H "Header2: val2"', callback=headers_callback, multiple=True)
@click.option('-b', '--blacklist', help='Status codes to NOT return', callback=parse_blacklist)
@click.option('-f', '--add-slash', is_flag=True, help='Add a slash to the end of the URL')
@click.option('-c', '--cookies', help='Cookies to send with the request, -c "cookieName=cookieVal" -c "cookie2=val2"', multiple=True, callback=cookies_callback)
@click.option('-r', '--redirects', type=int, help='Follow redirects the specified number of times (maximum)', default=0, show_default=True) # TODO: Implement
@click.option('--no-color', is_flag=True, help='Disable color output')
@click.option('-q', '--quiet', is_flag=True, help='Don\'t print the banner and other information')
def dir(
    url: str,
    wordlist: str,
    workers: int,
    timeout: int, 
    blacklist: list[int], 
    no_color: bool, 
    quiet: bool, 
    headers: dict, 
    add_slash: bool,
    cookies: Cookies,
    redirects: int
    ) -> None:
    console: Console = setup_console(no_color)

    asyncio.run(dir_entrypoint(console, url, wordlist, workers, timeout, quiet, blacklist, headers, add_slash, cookies, redirects))

