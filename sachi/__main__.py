from .cli import cli

if __name__ == "__main__":
    try:
        cli(max_content_width=120)
    except KeyboardInterrupt:
        pass