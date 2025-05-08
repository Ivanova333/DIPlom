import time
import uuid
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

from torch.utils.hipify.hipify_python import preprocessor

class ReportGenerator:
    def __init__(self, title: str, fonts_dir: str='fonts'):
        self.pdf=FPDF()
        self.title=title
        #self.author=author
        self.pdf.add_font('DejaVu','',os.path.join(fonts_dir,'DejaVuSans.ttf'),uni=True)
        self.pdf.add_font('DejaVuBold','',os.path.join(fonts_dir,'DejaVuSansBold.ttf'),uni=True)
        self.pdf.add_font('DejaVuOblique','',os.path.join(fonts_dir,'DejaVuSansOblique.ttf'),uni=True)
    def generate(self, df_1, analyzer, plotter, preprocessor):
        pdf = self.pdf
        pdf.add_page()

        # Добавляем шрифты: DejaVuSans для текста, DejaVuSans-Bold для заголовков и DejaVuSans-Oblique для курсива
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)  # Шрифт для текста
        pdf.add_font("DejaVuBold", "", "DejaVuSansBold.ttf", uni=True)  # Шрифт для заголовков
        pdf.add_font("DejaVuOblique", "", "DejaVuSansOblique.ttf", uni=True)  # Шрифт для курсива

        # Устанавливаем шрифт для заголовка
        pdf.set_font("DejaVuBold", size=16)
        pdf.cell(200, 10, txt="Аналитический отчет", ln=True, align='C')
        pdf.ln(6)
        # Общий анализ данных
        pdf.set_font("DejaVuBold", size=12)
        pdf.cell(200, 10, txt="1. Общий анализ данных:", ln=True, align='L')

        # Устанавливаем шрифт для основного текста
        pdf.set_font("DejaVu", size=12)

        # Вычисляем средние значения
        average_likes = df_1["likes_cnt"].mean()  # Среднее количество лайков
        average_comments = df_1["comment_cnt"].mean()  # Среднее количество комментариев
        average_reposts = df_1["reposts_cnt"].mean()  # Среднее количество репостов
        average_text_length = df_1["post_text"].apply(len).mean()  # Средняя длина текста
        average_engagement = df_1["engagement_rate"].mean()

        # Название секции "Соотношение эмоций в текстах"
        pdf.cell(200, 10, txt="1) Основные показатели:", ln=True, align='L')
        # Вставляем данные в отчет
        pdf.multi_cell(0, 10, txt=f"    - Среднее количество лайков: {average_likes:.2f}\n"
                                  f"    - Среднее количество комментариев: {average_comments:.2f}\n"
                                  f"    - Среднее количество репостов: {average_reposts:.2f}\n"
                                  f"    - Средняя длина текста: {average_text_length:.2f} символов\n")
        pdf.ln(3)

        pdf.cell(200, 10, txt="2) Анализ вовлеченности пользователей:", ln=True, align='L')
        # Средняя вовлеченность
        pdf.multi_cell(0, 10, txt=f"  - Средняя вовлеченность: {average_engagement:.2f}%\n")

        most_engaged_comment = analyzer.get_most_engaged_comment(df_1)
        pdf.cell(200, 10, txt="  - Пост с самой высокой вовлеченностью:", ln=True, align='L')
        pdf.set_font("DejaVu", size=12)

        if most_engaged_comment is not None:
            pdf.multi_cell(0, 10, txt=f"    Вовлеченность: {most_engaged_comment['engagement_rate']:.2f}%\n")
            pdf.multi_cell(0, 10, txt=f"    Автор: {most_engaged_comment['post_id']}\n")
            pdf.set_font("DejaVuOblique", size=12)  # Курсив для комментария
            # pdf.multi_cell(0, 10, txt=f"    {most_engaged_comment['post_text']}\n")
            text = preprocessor.basic_text_cleanup(most_engaged_comment['post_text'])
            pdf.multi_cell(0, 10, txt=f"{text}\n")
            # pdf.multi_cell(0, 10, txt=f"    {most_engaged_comment['post_text']}\n")
            pdf.set_font("DejaVu", size=12)
        else:
            pdf.multi_cell(0, 10, txt="    Нет постов с наибольшей вовлеченностью.\n")

        pdf.ln(3)

        pdf.cell(200, 10, txt="  - Зависимость вовлеченности пользователей от дня недели:", ln=True, align='L')

        # График вовлеченности по дням недели
        engagement_day_chart = plotter.plot_engagement_by_day(df_1)
        # Рассчитываем координаты для центрального выравнивания графика
        pdf_width = 210  # Ширина страницы PDF (мм)
        chart_width = 130  # Ширина изображения графика (мм)
        x_position = (pdf_width - chart_width) / 2  # Центрируем график по горизонтали

        pdf.image(engagement_day_chart, x=x_position, w=chart_width)
        plt.close()  # Закрываем график после его добавления в PDF
        os.remove(engagement_day_chart)  # Удаляем файл из папки
        pdf.ln(3)

        # Зависимость вовлеченности от времени суток
        pdf.cell(200, 10, txt="  - Зависимость вовлеченности пользователей по часам суток:", ln=True, align='L')
        # График вовлеченности по часам суток
        engagement_hour_filename = plotter.plot_engagement_by_hour(df_1)
        pdf.image(engagement_hour_filename, x=40, w=130)
        plt.close()  # Закрываем график после его добавления в PDF
        os.remove(engagement_hour_filename)  # Удаляем файл из папки
        pdf.ln(3)

        pdf.cell(200, 10, txt="3) Часто встречающиеся слова:", ln=True, align='L')
        most_common_words = analyzer.count_most_common_words(df_1)
        positive_words, negative_words, neutral_words = analyzer.count_most_sentiment(df_1)

        # Самые часто встречающиеся слова в комментариях
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(0, 10, txt="Самые часто встречающиеся слова в постах:")
        most_common_words_text = ", ".join([f"{word} ({count})" for word, count in most_common_words])
        pdf.multi_cell(0, 10, txt=f"    - {most_common_words_text}")

        # В позитивных комментариях
        pdf.multi_cell(0, 10, txt="+    В позитивных постах:")
        positive_words_text = ", ".join([f"{word} ({count})" for word, count in positive_words])
        pdf.multi_cell(0, 10, txt=f"    - {positive_words_text}")

        # В негативных комментариях
        pdf.multi_cell(0, 10, txt="-    В негативных постах:")
        negative_words_text = ", ".join([f"{word} ({count})" for word, count in negative_words])
        pdf.multi_cell(0, 10, txt=f"    - {negative_words_text}")

        # В нейтральных комментариях
        pdf.multi_cell(0, 10, txt="=    В нейтральных постах:")
        neutral_words_text = ", ".join([f"{word} ({count})" for word, count in neutral_words])
        pdf.multi_cell(0, 10, txt=f"    - {neutral_words_text}")
        pdf.ln(3)

        # Заголовок для анализа тональности
        pdf.set_font("DejaVuBold", size=12)
        pdf.cell(200, 10, txt="2. Анализ эмоциональной реакции пользователей:", ln=True, align='L')

        # Устанавливаем шрифт для основного текста
        pdf.set_font("DejaVu", size=12)

        # Даем подробности по тональности
        positive_ratio, negative_ratio, neutral_ratio, most_liked_positive_comment, most_liked_negative_comment, most_liked_neutral_comment = analyzer.analyze_comments_sentiment_for_PDF(
            df_1)

        # Название секции "Соотношение эмоций в текстах"
        pdf.cell(200, 10, txt="1) Динамика постов:", ln=True, align='L')

        # Перечисляем доли положительных, отрицательных и нейтральных комментариев
        pdf.multi_cell(0, 10, txt=f"    - Доля положительных постов: {positive_ratio:.2f}%\n"
                                  f"    - Доля отрицательных постов: {negative_ratio:.2f}%\n"
                                  f"    - Доля нейтральных постов: {neutral_ratio:.2f}%\n")
        # pdf.ln(3)

        # Добавляем график
        chart_filename = plotter.plot_sentiment_distribution(df_1)
        pdf.image(chart_filename, x=40, w=130)  # Вставляем изображение в отчет
        plt.close()  # Закрываем график после его добавления в PDF
        os.remove(chart_filename)  # Удаляем файл из папки
        pdf.ln(5)

        # Добавляем самые залайканные комментарии
        pdf.cell(200, 10, txt="2) Топ постов: положительные, негативные и нейтральные", ln=True, align='L')

        # Положительный комментарий (курсив)
        pdf.set_font("DejaVu", size=12)  # Обычный шрифт для заголовка
        if most_liked_positive_comment is not None:
            pdf.multi_cell(0, 10, txt=f"+ Самый популярный положительный пост:\n")
            pdf.set_font("DejaVu", size=12)  # Обычный шрифт для лайков
            pdf.multi_cell(0, 10, txt=f"Лайков: {most_liked_positive_comment['likes_cnt']}\n")
            pdf.set_font("DejaVuOblique", size=12)  # Курсив для комментария
            pdf.cell(10)  # Добавляем табуляцию (отступ) перед текстом
            # pdf.multi_cell(0, 10, txt=f"{most_liked_positive_comment['post_text']}\n")
            pdf.multi_cell(0, 10, txt=f"{preprocessor.basic_text_cleanup(most_liked_positive_comment['post_text'])}\n")
        else:
            pdf.multi_cell(0, 10, txt="Нет положительных постов.\n")

        # Отрицательный комментарий (курсив)
        pdf.set_font("DejaVu", size=12)  # Обычный шрифт для заголовка
        if most_liked_negative_comment is not None:
            pdf.multi_cell(0, 10, txt=f"- Самый популярный отрицательный пост:\n")
            pdf.set_font("DejaVu", size=12)  # Обычный шрифт для лайков
            pdf.multi_cell(0, 10, txt=f"Лайков: {most_liked_negative_comment['likes_cnt']}\n")
            pdf.set_font("DejaVuOblique", size=12)  # Курсив для комментария
            pdf.cell(10)  # Добавляем табуляцию (отступ) перед текстом
            # pdf.multi_cell(0, 10, txt=f"{most_liked_negative_comment['post_text']}\n")
            cleaned_negative_text = preprocessor.basic_text_cleanup(most_liked_negative_comment['post_text'])
            pdf.multi_cell(0, 10, txt=f"{cleaned_negative_text}\n")
        else:
            pdf.multi_cell(0, 10, txt="Нет отрицательных постов.\n")

        # Нейтральный комментарий (курсив)
        pdf.set_font("DejaVu", size=12)  # Обычный шрифт для заголовка
        if most_liked_neutral_comment is not None:
            pdf.multi_cell(0, 10, txt=f"= Самый популярный нейтральный пост:\n")
            pdf.set_font("DejaVu", size=12)  # Обычный шрифт для лайков
            pdf.multi_cell(0, 10, txt=f"Лайков: {most_liked_neutral_comment['likes_cnt']}\n")
            pdf.set_font("DejaVuOblique", size=12)  # Курсив для комментария
            pdf.cell(10)  # Добавляем табуляцию (отступ) перед текстом
            # pdf.multi_cell(0, 10, txt=f"{most_liked_neutral_comment['post_text']}\n")
            neutral_text = preprocessor.basic_text_cleanup(most_liked_neutral_comment['post_text'])
            pdf.multi_cell(0, 10, txt=f"{neutral_text}\n")
        else:
            pdf.multi_cell(0, 10, txt="Нет нейтральных постов.\n")

        pdf.ln(3)
        # Заголовок для спадов
        pdf.set_font("DejaVuBold", size=12)
        pdf.cell(200, 10, txt="3. Динамика активности пользователей:", ln=True, align='L')

        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt="1) Самый активный пользователь:", ln=True, align='L')
        most_active_user = df_1['post_id'].value_counts().idxmax()
        pdf.multi_cell(0, 10, txt=f"    - Самый активный пользователь: {most_active_user}")
        pdf.ln(3)

        # 2) Самый популярный день недели для публикаций:
        pdf.cell(200, 10, txt="2) Самый популярный день недели для публикаций:", ln=True, align='L')

        # Анализируем день недели с наибольшей активностью
        day_counts = df_1['day_of_week'].value_counts().sort_index()  # Считаем посты по дням недели
        day_counts = day_counts[sorted(day_counts.index)]  # Сортируем по порядку дней недели
        #day_counts.index = [days_of_week[i] for i in day_counts.index]  # Переименовываем индексы на дни недели
        day_counts.index = [plotter.days[i] for i in day_counts.index]
        # График активности по дням недели
        day_chart_filename = plotter.plot_activity_by_day(df_1)
        pdf.multi_cell(0, 10,
                       txt=f"    - День недели, когда пользователи публикуют больше всего контента: {day_counts.idxmax()}")
        pdf.image(day_chart_filename, x=40, w=130)  # Вставляем изображение в отчет
        plt.close()  # Закрываем график после его добавления в PDF
        os.remove(day_chart_filename)  # Удаляем файл из папки
        pdf.ln(3)

        # 3) Самое активное время суток для публикаций:
        pdf.cell(200, 10, txt="3) Самое активное время суток для публикаций:", ln=True, align='L')

        # Анализируем активность по часам суток
        hour_counts = df_1['hour_of_day'].value_counts().sort_index()  # Считаем посты по часам суток
        hour_counts.index = [plotter.hours[i] for i in hour_counts.index]
        #hour_counts.index = [hours_of_day[i] for i in hour_counts.index]  # Переименовываем индексы на часы суток
        # График активности по часам суток
        hour_chart_filename = plotter.plot_activity_by_hour(df_1)
        pdf.multi_cell(0, 10, txt=f"    - Время суток, когда пользователи наиболее активны: {hour_counts.idxmax()}")
        pdf.image(hour_chart_filename, x=40, w=130)  # Вставляем изображение в отчет
        plt.close()  # Закрываем график после его добавления в PDF
        os.remove(hour_chart_filename)  # Удаляем файл из папки
        pdf.ln(3)

        pdf_filename = plotter.generate_unique_filename("social_media_analysis", "pdf")
        pdf.output(pdf_filename)
        # print(f"Отчет создан и сохранен в файл '{pdf_filename}'")
        return pdf_filename
