from rich.table import Table
from rich.text import Text
from urllib.parse import urlsplit

def print_result_table(results):
    table = Table(title="Sachi Results", safe_box=True)

    table.add_column("Path", no_wrap=True, style="cyan")
    table.add_column("Status Code", no_wrap=True)
    table.add_column("URL", no_wrap=True, style="blue")

    for result in results:
        status_code, url = result
        path = urlsplit(url).path
        if status_code in range(200, 300):
            success_status_code = Text(str(status_code), style="bold green")
            table.add_row(path, success_status_code, url)
            # print(f"[green]{status_code}[/green] - [blue]{url}[/blue]")
        if status_code in range(300, 400):
            redirect_status_code = Text(str(status_code), style="bold yellow")
            table.add_row(path, redirect_status_code, url)
            # print(f"[yellow]{status_code}[/yellow] - [blue]{url}[/blue]")
        if status_code in range(400, 600):
            error_status_code = Text(str(status_code), style="bold red")
            table.add_row(path, error_status_code, url)
            # print(f"[red]{status_code}[/red] - [blue]{url}[/blue]")

    return table