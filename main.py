import spacy
from modules.preprocessing import Preprocessor
from modules.analysis import Analyzer
from modules.plotting import Plotter
from modules.report_generator import ReportGenerator

if __name__=='__main__':
    nlp=spacy.load('ru_core_news_sm')
    bad_words = {'человек', 'сегодня', 'завтра', 'день', 'конечно', 'как', 'все', 'никогда', 'тем', 'со', 'им', 'такой',
                 'ним', 'три', 'того', 'от', 'чуть', 'будто', 'чем', 'эти', 'раз', 'меня', 'нельзя', 'на', 'еще',
                 'есть', 'нет', 'опять', 'кто', 'нибудь', 'она', 'этом', 'ее', 'даже', 'себя', 'впрочем', 'один', 'в',
                 'вот', 'этой', 'зачем', 'тогда', 'всю', 'под', 'всего', 'вы', 'у', 'были', 'через', 'за', 'ей',
                 'иногда', 'ну', 'уже', 'до', 'про', 'него', 'где', 'какая', 'вдруг', 'ведь', 'их', 'тебя', 'быть', 'с',
                 'и', 'по', 'они', 'вас', 'том', 'надо', 'куда', 'какой', 'хоть', 'мой', 'да', 'свою', 'а', 'потому',
                 'тут', 'моя', 'из', 'там', 'он', 'во', 'почти', 'для', 'ж', 'вам', 'к', 'без', 'была', 'будет', 'себе',
                 'но', 'теперь', 'то', 'не', 'нее', 'нас', 'над', 'при', 'после', 'об', 'можно', 'его', 'ни', 'мы',
                 'так', 'если', 'может', 'тоже', 'разве', 'было', 'этот', 'ты', 'о', 'мне', 'ли', 'перед', 'уж', 'сам',
                 'здесь', 'чего', 'ему', 'чтобы', 'всех', 'них', 'бы', 'этого', 'наконец', 'тот', 'когда', 'эту',
                 'только', 'сейчас', 'ней', 'был', 'между', 'же', 'потом', 'чтоб', 'что', 'я'}

    preprocessor=Preprocessor(bad_words, nlp)
    df=preprocessor.load_data('data/df.csv')
    df=preprocessor.preprocess(df)
    df['cleaned_content']=df['post_text'].apply(preprocessor.clean_text)

    analyzer=Analyzer('cointegrated/rubert-tiny-sentiment-balanced')
    df['engagement_rate']=df.apply(analyzer.calculate_engagement_rate,axis=1)
    df=analyzer.run_full_sentiment_analysis(df)

    plotter=Plotter('temp_plots')

    # генерация отчёта
    report = ReportGenerator(
        title='Аналитический отчёт',
        fonts_dir='fonts'
    )
    output_path = report.generate(df,analyzer, plotter, preprocessor)
    print(f"Отчёт сохранён в: {output_path}")