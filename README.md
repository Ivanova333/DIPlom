# DIPlom

## Установка зависимостей
```bash
pip install -r requirements.txt
python -m spacy download ru_core_news_sm

## На всякий случай:

!pip install razdel
!pip install torch
!pip install transformers
!pip install matplotlib
!pip install scipy
!pip install emoji
!pip install fpdf
!pip install -U spacy
!python -m spacy download ru_core_news_sm

## Структура проекта

my_project/
├── data/                       # исходный датасет
│   └── df.csv
├── fonts/                      # шрифты DejaVu для отчёта
│   ├── DejaVuSans.ttf
│   ├── DejaVuSans-Bold.ttf
│   └── DejaVuSans-Oblique.ttf
├── modules/                    # модули с классами
│   ├── preprocessing.py        # класс Preprocessor
│   ├── analysis.py             # класс Analyzer
│   ├── plotting.py             # класс Plotter
│   └── report_generator.py     # класс ReportGenerator
├── outputs/                    # папка для финального отчёта (PDF)
├── main.py                     # входной скрипт
├── requirements.txt            # зависимости
└── .gitignore                  # исключения для Git
