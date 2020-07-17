import pandas as pd
from Levenshtein import distance
import sys


class Books:
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
        df['Book-Title'] = df['Book-Title'].str.lower()
        df['Book-Author'] = df['Book-Author'].str.lower()
        df['Author-Surname'] = df['Book-Author'].str.split(' ').str[-1]
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
        df = df.set_index('ISBN')
        return df

    def titles(self) -> set:
        return set(self._df_books['Book-Title'].tolist())

    def similar_titles(self, title: str) -> str:
        df_books_dedup = self._df_books.drop_duplicates(subset='Book-Title')
        df_books_dedup['distance'] = df_books_dedup['Book-Title'].apply(lambda x: distance(x, title))
        similar_titles = '\n'.join(df_books_dedup.sort_values(by=['distance']).head(10)['Book-Title'].tolist())
        titles = f'Book not found.\nDid you mean:\n{similar_titles}\n?'
        return titles

    def authors(self, title: str) -> set:
        return set(self._df_books[self._df_books['Book-Title'] == title]['Author-Surname'].tolist())

    def recommend(self, title: str, author: str) -> list:
        # TODO maybe there is better way to transform initial df to df for correlation
        try:
            df = pd.merge(self._df_rating, self._df_books, left_index=True, right_index=True)
            df_readers = df[df['User-ID'].isin(df['User-ID'][(df['Book-Title'] == title)
                                                             & (df['Author-Surname'] == author)])]
            number_of_rating_per_book = df_readers.groupby(['Book-Title']).agg('count')
            books_to_compare = number_of_rating_per_book[number_of_rating_per_book['User-ID'] >= 8].index
            ratings_data_raw = df_readers[['User-ID', 'Book-Rating', 'Book-Title']][
                df_readers['Book-Title'].isin(books_to_compare)]
            ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()
            ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()
            dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')
            my_df = dataset_for_corr.corrwith(dataset_for_corr[title])
            if dataset_for_corr.shape[1] == 1:
                print('Sorry, there is not enough books for recommendation')
                sys.exit(1)
            return my_df.sort_values(ascending=False).head(11).index[1:].tolist()
        except KeyError:
            print('Sorry, not enough ratings')
            sys.exit(1)
