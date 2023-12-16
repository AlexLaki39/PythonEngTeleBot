Telegram-bot для изучения английского языка
=
Файлы:
-
1. db_classes.py - классы Sqlalchemy, описывающие таблицы для базы данных PostgreSQL, в которой хранится информация о работе бота с пользоваетелем;\

2. funClasses.py - содержит классы с начальными параметрами работы (названия кнопок, первый набор базоывх слов, описание команд), а также функции для работы с БД;
3. tg_bot_funcs.py - содержит класс и функции работы c Telegram ботом с использованием библиотеки Telebot;
4. API_funcs.py - функция для получения примера использования слова на английском языке от сервися FREE DICTIONARY https://github.com/meetDeveloper/freeDictionaryAPI;
5. main.py - основной файл для запуска бота. На строчках 68, 71, 76, 77 закомментирован код. Он актуален только для первого запуска программы на новом сервере, и нужен для создания БД и всех таблиц, а также для заполнения таблицы BasicWords набором базовых слов из InitialValues.basic_words_list;
