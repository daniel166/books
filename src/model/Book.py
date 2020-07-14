import pandas as pd
import numpy as np
from Levenshtein import distance


class Book:
    def __init__(self):
        self._df_books = self._read_books()
        self._df_rating = self._read_ratings()

    def _read_books(self) -> pd.DataFrame:
        df = pd.read_csv(
            'data/raw/BX-Books.csv',
            encoding='cp1251',
            sep=';',
            error_bad_lines=False,
            usecols=['ISBN', 'Book-Title', 'Book-Author'],
            dtype={'ISBN': str, 'Book-Title': str, 'Book-Author': str},
        )
        df = df.apply(lambda x: x.astype(str).str.lower())
        df = df.set_index('ISBN')
        return df

    def _read_ratings(self) -> pd.DataFrame:
        df = pd.read_csv(
            'data/raw/BX-Book-Ratings.csv',
            encoding='cp1251',
            sep=';',
            dtype={'User-ID': int, 'ISBN': str, 'Book-Rating': float},
        )
        df = df[df['Book-Rating'] != 0]
        df['ISBN'] = df['ISBN'].str.lower()
        df = df.set_index('ISBN')
        return df

    def recommend(self, title: str):
        title = title.lower()

        # if title is not present in dataset, compute Levenshtein distance and print 10 most similar titles
        if title not in self._df_books['Book-Title'].unique():
            df_books = self._df_books.drop_duplicates(subset='Book-Title', keep="first")
            df_books['distance'] = df_books['Book-Title'].apply(lambda x: distance(x, title))
            print('Book not found')
            print(
                'Did you mean:',
                '\n',
                '\n'.join(df_books.sort_values(by=['distance']).head(10)['Book-Title'].tolist()),
                '\n'
                '?'
            )
            return

        dataset = pd.merge(self._df_rating, self._df_books, left_index=True, right_index=True)
