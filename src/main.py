import typer
from typing import List


def main(title: List[str]):
    typer.echo(f"Book title: {title}")


if __name__ == "__main__":
    typer.run(main)
