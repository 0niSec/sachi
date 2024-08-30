from urllib.parse import urljoin
from .utils import collect_words
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, track
from rich.text import Text
import httpx
import asyncio
from asyncio import Queue

def get_status_style(status_code):
    if status_code in range(200, 300):
        return "bold green"
    elif status_code in range(300, 400):
        return "bold yellow"
    elif status_code in range(400, 600):
        return "bold red"
    else:
        return None
    
# Define the Sachi object
class Sachi:
    def __init__(self, url, wordlist_path, blacklist, console, timeout: int, headers: dict, add_slash: bool, cookies: httpx.Cookies, redirects: int):
        self.url: str = url
        self.wordlist_path: str = wordlist_path
        self.blacklist: list = blacklist
        self.client: httpx.Client = httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            cookies=cookies,
            max_redirects=redirects,
        )
        self.console = console
        self.add_slash: bool = add_slash
        self.redirects: int = redirects

        # Create Progress and Table using the passed console
        self.progress: Progress = Progress(
            SpinnerColumn(spinner_name="dots", finished_text="Done!"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(style="white", complete_style="green", finished_style="green", pulse_style="yellow"),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=True,
        )
        self.status: Progress = self.progress.add_task("[bold green]Scanning...[/bold green]", total=len(list(collect_words(self.wordlist_path))))

    async def close(self) -> None:
        await self.client.aclose()

    async def handle_redirect(self, response) -> httpx.Response:
        for _ in range(self.redirects):
            if response.is_redirect:
                next_url = response.headers.get("Location")
                response = await self.client.get(next_url)
            else:
                break
        return response

    async def validate_url(self, url: str) -> bool:
        """Validates the URL and returns True if the URL is valid, False otherwise.
        
        Parameters:
            url (str): The URL to validate.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        try:
            if self.add_slash:
                url = urljoin(url, "/")
            response: httpx.Response = await self.client.get(url)
            if response.status_code == 200:
                return True
        except httpx.RequestError as e:
            self.console.print(f"Error making request to {url}:  {str(e)}")
        return False

    async def scan_path(self, word: str) -> httpx.Response:
        """Scans a single path and returns the response object.

        Parameters:
            word (str): The word to scan.

        Returns:
            httpx.Response: The response object.

            https://www.python-httpx.org/api/#response
        """
        # Join the word with the URL
        url: str = urljoin(self.url, word)

        # If add_slash option is passed, add the slash to the end of the URL
        if self.add_slash:
            url = urljoin(url, word + "/")

        try:
            # Get the response object
            response: httpx.Response = await self.client.get(url)

            # If the response is a redirect, handle it
            if response.is_redirect and self.redirects > 0:
                original_status = response.status_code
                final_response = await self.handle_redirect(response)

                # Create a custom response object
                custom_response = httpx.Response(
                    status_code=original_status,
                    headers=response.headers,
                    content=final_response.content,
                    request=response.request,
                )
                custom_response.final_url = str(final_response.url)
                custom_response.final_status = final_response.status_code

                return custom_response
            return response
        
        # If anything goes wrong with the request, print out the error
        except httpx.RequestError as e:
            return self.console.print(f"Error requesting '{word}': {str(e)}")
        
    async def process_word(self, word: str) -> None:
            """Process a single word and print the results.
            
            Parameters:
                word (str): The word to process from the wordlist.

            Returns:
                None
            """
            # Scan the path
            response = await self.scan_path(word)

            response_size: bytes = len(response.content)
            status_code: int = response.status_code
            url: str = str(response.url)

            if not status_code or status_code in self.blacklist:
                return

             # Print the results
            formatted_results: Text = Text()
            formatted_results.append(f"{word:<30}", style="cyan")
            formatted_results.append(f"{status_code} [{response_size} bytes]".ljust(30), style=get_status_style(status_code))
            if hasattr(response, 'final_status'):
                formatted_results.append(f"{url} -> {response.final_url}", style="blue")
                # formatted_results.append(f"({response.final_status})", style=get_status_style(response.final_status))
            else:
                formatted_results.append(f"{url:<50}", style="blue")

            self.console.print(formatted_results)
            self.progress.update(self.status, advance=1)

    async def worker(self, queue: asyncio.Queue[str], shutdown: asyncio.Event) -> None:
        """Creates a worker to perform work
        
        Parameters:
            queue (asyncio.Queue[str]): The queue to process.
            shutdown (asyncio.Event): The shutdown event.

        Returns:
            None
        """
        while not queue.empty() and not shutdown.is_set():
            word: str = await queue.get()
            try:
                await self.process_word(word)
                # FIXME: This should be more specific to the exception type
            except Exception as e:
                self.console.print(f"Error processing '{word}': {str(e)}")
            finally:
                queue.task_done()
    
    async def dirscan(self, num_workers: int) -> None:
        """Performs a web directory scan with a given number of concurrent async workers
        
        Parameters:
            num_workers (int): The number of concurrent async workers.

        Returns:
            None
        """
        words: list = list(collect_words(self.wordlist_path))
        queue: asyncio.Queue = Queue()
        shutdown: asyncio.Event = asyncio.Event()
        for word in words:
            await queue.put(word)

        workers: asyncio.Task = [asyncio.create_task(self.worker(queue, shutdown=shutdown)) for _ in range(int(num_workers))]

        try:
            with Live(self.progress, refresh_per_second=30, console=self.console, vertical_overflow="visible", transient=True):
                await asyncio.gather(*workers)
        except asyncio.CancelledError:
            self.console.print("\n[bold red]Scan cancelled. Exiting...[/bold red]")
        finally:
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            await self.close()


