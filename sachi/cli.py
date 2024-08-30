import click
from .commands.dir import dir

@click.group()
@click.version_option(version='0.1.0', prog_name='sachi')
def cli():
    """Sachi - The web enumeration tool...in Python (yes, another one!)"""
    pass

cli.add_command(dir)