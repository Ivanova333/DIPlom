import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from collections import Counter

class Analyzer:
    def __init__(self, model_checkpoint: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)
        if torch.cuda.is_available():
            self.model.cuda()

    def calculate_engagement_rate(self, row):
        if row['views_cnt'] == 0:
            return 0
        engagement = (row['likes_cnt'] + row['comment_cnt'] + row['reposts_cnt']) / row['views_cnt'] * 100
        return engagement

    def analyze_sentiment(self, text: str) -> str:
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True).to(self.model.device)
            proba = torch.sigmoid(self.model(**inputs).logits).cpu().numpy()[0]
            score = proba.dot([-1, 0, 1])
        if score < -0.2:
            return 'Негативный'
        elif score > 0.2:
            return 'Позитивный'
        else:
            return 'Нейтральный'

    def analyze_comments_sentiment_for_PDF(self, df: pd.DataFrame):
        """Анализирует тональность комментариев и возвращает метрики."""
        positive_comments = df[df['Тональность'] == 'Позитивный']
        negative_comments = df[df['Тональность'] == 'Негативный']
        neutral_comments = df[df['Тональность'] == 'Нейтральный']

        # Подсчитываем долю каждого типа
        total_comments = len(df)
        positive_ratio = len(positive_comments) / total_comments * 100
        negative_ratio = len(negative_comments) / total_comments * 100
        neutral_ratio = len(neutral_comments) / total_comments * 100

        # Проверяем, есть ли положительные комментарии, чтобы найти самый залайканный
        if not positive_comments.empty:
            most_liked_positive_comment = positive_comments.loc[positive_comments['likes_cnt'].idxmax()]
        else:
            most_liked_positive_comment = None

        # Проверяем, есть ли отрицательные комментарии, чтобы найти самый залайканный
        if not negative_comments.empty:
            most_liked_negative_comment = negative_comments.loc[negative_comments['likes_cnt'].idxmax()]
        else:
            most_liked_negative_comment = None

        # Проверяем, есть ли нейтральные комментарии, чтобы найти самый залайканный
        if not neutral_comments.empty:
            most_liked_neutral_comment = neutral_comments.loc[neutral_comments['likes_cnt'].idxmax()]
        else:
            most_liked_neutral_comment = None

        return positive_ratio, negative_ratio, neutral_ratio, most_liked_positive_comment, most_liked_negative_comment, most_liked_neutral_comment

    def run_full_sentiment_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        df['Тональность'] = df['cleaned_content'].apply(self.analyze_sentiment)
        return df

    def get_most_engaged_comment(self, df):
        """Возвращает комментарий с наибольшей вовлеченностью."""
        most_engaged_comment = df.loc[df['engagement_rate'].idxmax()]
        return most_engaged_comment

    def count_most_common_words(self, df):
        """Возвращает 3 самых часто встречающихся слов в комментариях."""
        # Собираем все слова из очищенных комментариев
        all_words = []
        for text in df["cleaned_content"]:
            words = text.split()
            all_words.extend(words)
        # Фильтруем слова длиной более 3 символов
        filtered_words = [word for word in all_words if len(word) > 3]
        # Подсчитываем частоту слов
        word_counts = Counter(filtered_words)
        most_common = word_counts.most_common(3)
        return most_common

    def count_most_sentiment(self, df):
        """Возвращает 5 самых часто встречающихся слов по типам комментариев."""
        # Разделяем комментарии по тональности
        positive_comments = df[df['Тональность'] == 'Позитивный']
        negative_comments = df[df['Тональность'] == 'Негативный']
        neutral_comments = df[df['Тональность'] == 'Нейтральный']
        # Собираем все слова для каждого типа комментария
        def get_common_words(comments_df):
            all_words = []
            for text in comments_df["cleaned_content"]:
                words = text.split()
                all_words.extend(words)
            filtered_words = [word for word in all_words if len(word) > 3]
            word_counts = Counter(filtered_words)
            return word_counts.most_common(3)

        # Получаем самые популярные слова по тональностям
        positive_words = get_common_words(positive_comments)
        negative_words = get_common_words(negative_comments)
        neutral_words = get_common_words(neutral_comments)

        return positive_words, negative_words, neutral_words