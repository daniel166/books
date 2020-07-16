import typer
from typing import List
from model.Books import Books


def main(title: List[str]):
    typer.echo(f'Book title: {title}')
    title = ' '.join(title).lower()
    books = Books()

    # if title is not present in dataset, compute Levenshtein distance and print 10 most similar titles
    if title not in books.titles():
        raise ValueError(books.similar_titles(title))

    # book name can be ambiguous, same title different authors
    authors = books.authors(title)
    if len(authors) > 1:
        author = typer.prompt(f'{title} is ambiguous. Please specify author surname. Possibilities are: {authors}')
        if author.lower() not in authors:
            raise ValueError('Invalid author')
    else:
        author = list(authors)[0].lower()

    books.recommend(title, author)


if __name__ == "__main__":
    typer.run(main)
