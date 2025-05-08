import pandas as pd
import re
import emoji
from razdel import sentenize
from datetime import datetime

class Preprocessor:
    def __init__(self, bad_words: set, nlp):
        self.bad_words = bad_words
        self.nlp = nlp

    def load_data(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, delimiter=',')
        return df

    def basic_text_cleanup(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        text = emoji.replace_emoji(text, replace='')
        text = text.replace("—", "-")
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("«", '"').replace("»", '"')
        text = text.replace("\xa0", " ").replace("\u200b", "")
        text = ''.join(c for c in text if ord(c) < 65535)
        return text.strip()

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        text = re.sub(r'[^\w\s]', '', self.basic_text_cleanup(text.lower()))
        doc = self.nlp(text)
        cleaned = [token.lemma_ for token in doc
                   if token.lemma_ not in self.bad_words
                   and not token.is_stop
                   and not token.is_punct]
        return " ".join(cleaned)

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates().copy()
        for col in df.select_dtypes(include='object'):
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].mode()[0])
        for col in df.select_dtypes(include='int64'):
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        for metric in ['likes_cnt', 'comment_cnt', 'reposts_cnt']:
            if metric in df.columns:
                df.loc[df[metric] < 0, metric] = df[metric].median()
        if 'creation_date' in df.columns:
            df['creation_date'] = pd.to_datetime(df['creation_date'], errors='coerce')
            df = df.dropna(subset=['creation_date'])
            df['day_of_week'] = df['creation_date'].dt.dayofweek
            df['hour_of_day'] = df['creation_date'].dt.hour
        return df

    def save_processed(self, df: pd.DataFrame, path: str) -> None:
        df.to_csv(path, index=False)