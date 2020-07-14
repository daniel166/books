import typer
from typing import List
from model.Book import Book


def main(title: List[str]):
    typer.echo(f"Book title: {title}")
    books = Book()
    books.recommend(' '.join(title))


if __name__ == "__main__":
    typer.run(main)
