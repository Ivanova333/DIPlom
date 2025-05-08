import matplotlib.pyplot as plt
import time, uuid
import os
from datetime import datetime

class Plotter:
    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.days = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье']
        self.hours = [f"{i}:00" for i in range(24)]

    def generate_unique_filename(self, prefix: str, extension: str) -> str:
        ts = int(time.time())
        uid = uuid.uuid4().hex[:8]
        return f"{self.output_dir}/{prefix}_{ts}_{uid}.{extension}"

    def plot_activity_by_day(self, df):
        counts = df['day_of_week'].value_counts().sort_index()
        counts.index = [self.days[i] for i in counts.index]
        plt.figure(figsize=(10,6))
        counts.plot(kind='bar', color='skyblue')
        plt.xlabel('День недели')
        plt.ylabel('Количество постов')
        plt.xticks(rotation=45)
        fn = self.generate_unique_filename('day_activity','png')
        plt.savefig(fn, dpi=150, bbox_inches='tight')
        plt.close()
        return fn

    def plot_activity_by_hour(self, df):
        counts = df['hour_of_day'].value_counts().sort_index()
        counts.index = [self.hours[i] for i in counts.index]
        plt.figure(figsize=(10,6))
        counts.plot(kind='bar', color='lightgreen')
        plt.xlabel('Час суток')
        plt.ylabel('Количество постов')
        plt.xticks(rotation=45)
        fn = self.generate_unique_filename('hour_activity','png')
        plt.savefig(fn, dpi=150, bbox_inches='tight')
        plt.close()
        return fn

    def plot_engagement_by_day(self, df):
        eng = df.groupby('day_of_week')['engagement_rate'].mean().sort_index()
        eng.index = [self.days[i] for i in eng.index]
        plt.figure(figsize=(10,6))
        eng.plot(kind='bar', color='orange')
        plt.xlabel('День недели')
        plt.ylabel('Средний уровень вовлеченности (%)')
        plt.xticks(rotation=45)
        fn = self.generate_unique_filename('engagement_by_day','png')
        plt.savefig(fn, dpi=150, bbox_inches='tight')
        plt.close()
        return fn

    def plot_engagement_by_hour(self, df):
        eng = df.groupby('hour_of_day')['engagement_rate'].mean().sort_index()
        eng.index = [self.hours[i] for i in eng.index]
        plt.figure(figsize=(10,6))
        eng.plot(kind='bar', color='lightcoral')
        plt.xlabel('Час суток')
        plt.ylabel('Средний уровень вовлеченности (%)')
        plt.xticks(rotation=45)
        fn = self.generate_unique_filename('engagement_by_hour','png')
        plt.savefig(fn, dpi=150, bbox_inches='tight')
        plt.close()
        return fn

    def plot_sentiment_distribution(self, df):
        positive_comments = df[df['Тональность'] == 'Позитивный']
        negative_comments = df[df['Тональность'] == 'Негативный']
        neutral_comments = df[df['Тональность'] == 'Нейтральный']

        sizes = [len(positive_comments), len(neutral_comments), len(negative_comments)]
        labels = ['Положительные', 'Нейтральные', 'Отрицательные']
        colors = ['#99ff99', '#66b3ff', '#ff6666']

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140,
                wedgeprops={'edgecolor': 'black'})
        # Генерируем уникальное имя для графика
        image_filename = self.generate_unique_filename("sentiment_chart", "png")
        plt.savefig(image_filename, dpi=150, bbox_inches='tight')
        plt.close()

        return image_filename