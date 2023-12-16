import random
import re
import db_classes

from db_classes import BasicWords, Users, StudiedWords, WordsInStudy

class Command:
    ADD_WORD = 'ДОБАВЬ СЛОВО'
    DELETE_WORD = 'УДАЛИ СЛОВО'
    USE_EXAMPLE = 'ПОКАЗАТЬ ПРИМЕР'

class InitialValues:
    basic_words_list = [
    {'en_word': 'head', 'ru_word': 'голова'},
    {'en_word': 'fat', 'ru_word': 'толстый'},
    {'en_word': 'number', 'ru_word': 'номер'},
    {'en_word': 'love', 'ru_word': 'любовь'},
    {'en_word': 'mother', 'ru_word': 'мама',},
    {'en_word': 'sister', 'ru_word': 'сестра',},
    {'en_word': 'phone', 'ru_word': 'телефон'},
    {'en_word': 'dog', 'ru_word': 'собака',},
    {'en_word': 'cat', 'ru_word': 'кошка'},
    {'en_word': 'go', 'ru_word': 'идти',}
    ]
    current_user_id = 0
    command_dict = {
    '/enru': 'Перевод с английского на русский',
    '/ruen': 'Перевод с русского на английский',
    '/getwords': 'Создам базовый набор слов, с которого можно начать.',
    '/mywords': 'Показать список слов, которые ты изучаешь',
    '/help': 'Какие команды я знаю.',
    }
    buttons = {
        f'Кнопка {Command.ADD_WORD}': 'Добавить в словарь новое слово.',
        f'Кнопка {Command.DELETE_WORD}': 'Удалить слово, которое уже изучено.',
        f'Кнопка {Command.USE_EXAMPLE}': 'Показать пример использования слова.'
    }

def get_word_to_learn(session_name):
    words_list = []
    words_amount = session_name.query(WordsInStudy).count()
    for id in random.sample(range(1, words_amount), 4):
        en_word = session_name.query(BasicWords.en_word
                                     ).join(WordsInStudy, WordsInStudy.word_id == BasicWords.id
                                            ).filter(WordsInStudy.id == int(id)
                                                     ).all()
        ru_word = session_name.query(BasicWords.ru_word
                                     ).join(WordsInStudy, WordsInStudy.word_id == BasicWords.id
                                            ).filter(WordsInStudy.id == int(id)
                                                     ).all()                             
        words_list.append({en_word[0][0]: ru_word[0][0]})
    return words_list
    
def add_row_to_table(session_name, table_name: str, content_dict: dict):
        if table_name == 'BasicWords':
            row = session_name.query(BasicWords
                                     ).filter(BasicWords.en_word==content_dict['en_word'], 
                                              BasicWords.ru_word==content_dict['ru_word']
                                              ).all()
            if not row:
                session_name.add(BasicWords(en_word=content_dict['en_word'], 
                                            ru_word=content_dict['ru_word']))
        elif table_name == 'Users':
            row = session_name.query(Users).filter(Users.username==content_dict['username']
                                                   ).all()
            if not row:
                session_name.add(Users(username=content_dict['username']))
        elif table_name == 'WordsInStudy':
            print('WordsInStudy filling in')
            row = session_name.query(WordsInStudy
                                     ).filter(WordsInStudy.correct_guesses==content_dict['correct_guesses'], 
                                              WordsInStudy.word_id==content_dict['word_id'], 
                                              WordsInStudy.user_id==content_dict['user_id']
                                              ).all()
            if not row:
                session_name.add(WordsInStudy(correct_guesses=content_dict['correct_guesses'],
                                              word_id=content_dict['word_id'],
                                              user_id=content_dict['user_id']))
        elif table_name == 'StudiedWords':
            row = session_name.query(StudiedWords
                                     ).filter(StudiedWords.word_id==content_dict['word_id'], 
                                              StudiedWords.user_id==content_dict['user_id']
                                              ).all()
            if not row:
                session_name.add(StudiedWords(word_id=content_dict['word_id'], 
                                              user_id=content_dict['user_id']))
        return session_name.commit()

def show_words_in_study(session_name, current_user_id):
    res = session_name.query(WordsInStudy
                             ).filter(WordsInStudy.user_id==current_user_id
                                      ).count()
    return res

def check_and_reg_user(session_name, username: str):
    res = session_name.query(Users.id
                             ).filter(Users.username==username)
    if res.all() == True:
        print('user exists') 
        return None
    else:
        add_row_to_table(session_name, 'Users', {'username': username})
        return res.all()[0][0]

def remove_row_from_table(session_name, word_or_id):
    if type(word_or_id) == int:
        session_name.query(WordsInStudy
                ).filter(WordsInStudy.word_id==word_or_id
                        ).delete()
        return session_name.commit()
    else:
        word_to_remove_id = session_name.query(WordsInStudy.word_id
                                ).join(BasicWords, WordsInStudy.word_id==BasicWords.id
                                        ).filter(BasicWords.en_word==word_or_id
                                                ).all()[0][0]
        session_name.query(WordsInStudy
                        ).filter(WordsInStudy.word_id==word_to_remove_id
                                ).delete()
        return session_name.commit()

def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def has_latin(text):
    return bool(re.search('[a-zA-Z]', text))

def get_new_word_pair(message, session_name, bot_name, user_id):
    word_to_add = message.text.split()
    add_row_to_table(session_name, 'BasicWords', {'en_word':word_to_add[0], 'ru_word': word_to_add[1]})
    added_word_id = session_name.query(BasicWords.id
                                       ).filter(BasicWords.en_word==word_to_add[0])
    add_row_to_table(session_name, 'WordsInStudy', {'correct_guesses': 0, 'word_id': added_word_id, 'user_id': user_id})
    bot_name.send_message(message.chat.id, f'Отлично, теперь ты изучаешь {show_words_in_study(session_name, user_id)} слов')
    return word_to_add

def del_word(message, session_name, bot_name):
    word_to_del = message.text
    remove_row_from_table(session_name, word_to_del)
    bot_name.send_message(message.chat.id, 'Как скажешь, больше не будем иметь дела с этим словом')
    return

def send_word_to_studied(bot_name, session_name, message, user_id):
    word = message.text
    if has_cyrillic(word):
        condition = session_name.query(WordsInStudy.correct_guesses
                                    ).join(BasicWords, WordsInStudy.word_id==BasicWords.id
                                            ).filter(BasicWords.ru_word==word)
    else:
        condition = session_name.query(WordsInStudy.correct_guesses
                                    ).join(BasicWords, WordsInStudy.word_id==BasicWords.id
                                            ).filter(BasicWords.en_word==word)
    if condition.all()[0][0] >= 10:
        if has_cyrillic(word):
            word_id = session_name.query(WordsInStudy.word_id
                                        ).join(BasicWords, WordsInStudy.word_id==BasicWords.id
                                                ).filter(BasicWords.ru_word==word).all()[0][0]
            session_name.commit()
            add_row_to_table(session_name, 'StudiedWords', {'word_id': word_id, 'user_id': user_id})
            remove_row_from_table(session_name, word_id)
        else:
            word_id = session_name.query(WordsInStudy.word_id
                                        ).join(BasicWords, WordsInStudy.word_id==BasicWords.id
                                                ).filter(BasicWords.en_word==word).all()[0][0]
            session_name.commit()
            add_row_to_table(session_name, 'StudiedWords', {'word_id': word_id, 'user_id': user_id})
            remove_row_from_table(session_name, word_id)
        bot_name.send_message(message.chat.id, f'Похоже, ты уже выучил это слово {message.text}')
    return