from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    PER,
    NamesExtractor,
    Doc
)
from pymystem3 import Mystem
import pymorphy2
import nltk
from nltk import tokenize as tok
import spacy_udpipe
import graphviz
from collections import OrderedDict

import os
# os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

nltk.download('punkt')

spacy_udpipe.download("ru")
udpipe_model = spacy_udpipe.UDPipeModel("ru")

morph = pymorphy2.MorphAnalyzer()

# Создание упорядоченного словаря (предложение : [id слова : форматирование текста])
colored_text_dict = OrderedDict()

# Словари
a = os.path.basename(__file__)
b = os.path.abspath(__file__).replace(a, '')

required_thesaurus = open(os.path.join(b, 'required_thesaurus_normal_forms.txt'), 'r', encoding='utf-8').read()
required_thesaurus_plus = open(os.path.join(b, 'required_thesaurus_normal_forms_plus.txt'), 'r', encoding='utf-8').read()
possible_thesaurus = open(os.path.join(b, 'possible_thesaurus_normal_forms.txt'), 'r', encoding='utf-8').read()

required_dictionary = []
required_dictionary_plus = []
possible_dictionary = []

# Составление словарей
for line in required_thesaurus.split('\n'):
    for r_word in line.split(',')[0].split(';'):
        required_dictionary.append(r_word)

for line in required_thesaurus_plus.split('\n'):
    for r_word in line.split(',')[0].split(';'):
        # required_dictionary.append(r_word)  # убрать ?
        required_dictionary_plus.append(r_word)

for line in possible_thesaurus.split('\n'):
    for r_word in line.split(',')[0].split(';'):
        possible_dictionary.append(r_word)

# Значениями для форматирования текста
color_format = []
color_name_format = []
# Сбросить форматирование вывода в консоль к начальным значениям
standard_format = "\033[0m{}"
# Заполнение списков значениями для форматирования текста
for v in range(31, 37):
    color_format.append("\033[" + str(v) + "m{}\033[0m")
    color_name_format.append("\033[" + str(v + 10) + "m{}\033[0m")


# Функция возвращает начальную форму слова
def normal_form(word):
    res_word = morph.parse(word)[0].normal_form
    return res_word


# Вывод текста с цветовой разметкой (актуальная функция)
def colored_format_text_print(full_colored_text_dict):
    result_text = ""
    for key, value in full_colored_text_dict.items():
        result_sentence = ""
        docUP = udpipe_model(key)
        last_word = ""
        for sent in docUP:
            for word in sent.words:
                if word.id == 0:
                    continue
                if word.id in value:
                    # print(value[word.id].format(word.form), end=' ')
                    if (word.id == 1
                            or (word.form == ',') or (word.form == '.')
                            or (word.form == ':') or (word.form == ';')
                            or (word.form == '?') or (word.form == '!')
                            or (word.form == '»')):
                        result_sentence += value[word.id].format(word.form)
                    elif last_word == '«':
                        result_sentence += value[word.id].format(word.form)
                    else:
                        result_sentence += ' ' + value[word.id].format(word.form)
                last_word = word.form
        # print(result_sentence)

        # Добавить в форматирование
        # result_sentence = result_sentence.replace(r' "\S*', '"')
        # result_sentence = result_sentence.replace(r'\S*" ', '"')

        result_text += result_sentence + '\n'
    print(result_text)


# Функция, вызывающая нахождение описаний внешности в предложениях
def find_descriptions_of_appearance(text, show_colored_format_text_print=True, text_format=color_format[5]):
    # Разделение текста на предложения
    sentences = tok.sent_tokenize(text)

    result = dict()

    count = 0
    for s in sentences:
        # Вызов функции выделения описаний внешности из предложений (без имён)
        result_connected_dict, colored_current_sentence_dict = find_descriptions(s, text_format)
        colored_text_dict[s] = colored_current_sentence_dict

        count += len(result_connected_dict)

        # Для проверки соединенного выделения при записи в файл
        result_phrases = []
        for key in result_connected_dict.keys():
            result_phrases.append(key)

        # print(result_phrases)
        result[s] = result_phrases

    # Вывод текста с цветовой разметкой
    if show_colored_format_text_print:
        colored_format_text_print(colored_text_dict)

    return result


# Функция выделения из текста предложений с именами -> вызывающая нахождение описаний внешности в этих предложениях
def appearance_descriptions_for_names(text, show_colored_format_text_print=True):
    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    doc = Doc(text)

    doc.segment(segmenter)

    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)

    doc.tag_ner(ner_tagger)

    for span in doc.spans:
        span.normalize(morph_vocab)

    for span in doc.spans:
        if span.type == PER:
            span.extract_fact(names_extractor)

    output = []

    for s in {_.normal: _.fact.as_dict for _ in doc.spans if _.fact}:
        output.append(s)

    nameSet = set()

    for n in output:
        string = ' '.join(n.split())
        m = Mystem()
        lemmas = m.lemmatize(string)

        phrase = []

        for l in lemmas:
            if not l[0].isalpha():
                continue
            phrase.append(l.title())

        f_name = ' '.join(phrase)
        nameSet.add(f_name)

    # Вывод списка имён (без повторений)
    # print('Имена персонажей:')
    # for x in nameSet:
        # print(x)

    names = []
    for x in nameSet:
        names.append(x)

    # Разделение текста на предложения
    sentences = tok.sent_tokenize(text)

    # Создание словаря предложений, в которых встречаются имена
    dictionary = dict()

    previous = ''
    previous_form = ''

    color_names_dict = dict()
    color_index = 0

    result = dict()

    for s in sentences:
        # Предложение без выделенных описаний
        colored_sent_dict = dict()
        words_dict = dict()
        docUP = udpipe_model(s)
        for sent in docUP:
            for word in sent.words:
                colored_sent_dict[word.id] = standard_format
                words_dict[word.form] = word.id

        current = "".join(
            c for c in s if c not in ('!', '.', ':', ',', '?', '—', '–', '«', '»', ";", "/", "\\", ")", "(", "\""))
        words = current.strip().split()
        for word in words:
            p = normal_form(word).title()
            if p in names:
                name = p
                list = [s]
                if name in dictionary:
                    dictionary[name].extend(list)
                else:
                    dictionary[name] = list

                if name not in color_names_dict:
                    color_names_dict[name] = color_index
                    color_index += 1
                    if color_index >= len(color_format):
                        color_index = 0
                result_connected_dict, colored_sent_dict = find_descriptions(s, color_format[color_names_dict[name]])
                colored_sent_dict[words_dict[word]] = color_name_format[color_names_dict[name]]

                result_phrases = []
                for key in result_connected_dict.keys():
                    result_phrases.append(key)

                # print(result_phrases)
                if p in result:
                    result[p] += result_phrases
                else:
                    result[p] = result_phrases

            if (previous + ' ' + p) in names:
                name = previous + ' ' + p
                list = [s]
                if name in dictionary:
                    dictionary[name].extend(list)
                else:
                    dictionary[name] = list

                if name not in color_names_dict:
                    color_names_dict[name] = color_index
                    color_index += 1
                    if color_index >= len(color_format):
                        color_index = 0
                result_connected_dict, colored_sent_dict = find_descriptions(s, color_format[color_names_dict[name]])
                colored_sent_dict[words_dict[previous_form]] = color_name_format[color_names_dict[name]]
                colored_sent_dict[words_dict[word]] = color_name_format[color_names_dict[name]]

                result_phrases = []
                for key in result_connected_dict.keys():
                    result_phrases.append(key)

                # print(result_phrases)
                if previous + ' ' + p in result:
                    result[previous + ' ' + p] += result_phrases
                else:
                    result[previous + ' ' + p] = result_phrases

            previous = p
            previous_form = word

        for name in color_names_dict.keys():
            for word in words:
                if normal_form(word) == normal_form(name):
                    colored_sent_dict[words_dict[word]] = color_name_format[color_names_dict[name]]

        colored_text_dict[s] = colored_sent_dict

    # print('\nПредложения, относящиеся к именам персонажей:')
    # for key, value in dictionary.items():
        # print(key, value, end=';')
        # print('\n')

    # Вывод текста с цветовой разметкой
    if show_colored_format_text_print:
        colored_format_text_print(colored_text_dict)

    return result


# Функция выделения описаний внешности из предложения current_sentence
def find_descriptions(current_sentence, color_text_format):
    colored_sent_dict = OrderedDict()
    words_dict = dict()
    gl_id = 0
    # Вызов функции создания графа синтаксического разбора текущего предложения (раскомментировать, если нужно составить граф разбора предложения)
    # make_graph(current_sentence)
    phrases_for_name = []
    docUP = udpipe_model(current_sentence)
    for sent in docUP:
        for word in sent.words:
            words_dict[word.id] = word.form
        for word in sent.words:
            # print(word.id, word.form, word.deprel, word.head, normal_form(word.form))
            if word.id not in colored_sent_dict:
                colored_sent_dict[word.id] = standard_format
            if (word.deprel == 'amod'
                or word.deprel == 'nmod'
                or word.deprel == 'conj'
                or word.deprel == 'obl'
                or word.deprel == 'acl'
                or word.deprel == 'acl:relcl'
                or word.deprel == 'appos'
                or word.deprel == 'obj'
                or word.deprel == 'nsubj'
                or word.deprel == 'nsubj:pass'
                or word.deprel == 'root'
                or word.deprel == 'ccomp'    # новое
                or word.deprel == 'advcl'    # новое
                or word.deprel == 'parataxis'    # новое
                or word.deprel == 'iobj'    # новое
            ):
                current_id = word.id
                string = ''
                idc = 0
                id_s = []
                for word_j in sent.words:
                    if (word_j.head == current_id
                        and word_j.deprel != 'punct'
                        and word_j.deprel != 'cc'
                        and morph.parse(word_j.form)[0].tag.POS != 'VERB'  # слово в описании не должно являться глаголом
                        and (idc == 0 or word_j.id == idc + 1)
                        # слово относится(head) к отобранному в предыдущем условии и стоит в предложении перед отобранным
                        or (word_j.head == current_id
                            and word_j.id + 1 == current_id
                            and word_j.deprel != 'punct'
                            and morph.parse(word_j.form)[0].tag.POS != 'VERB') # слово в описании не должно являться глаголом
                    ):
                        string += words_dict[word_j.id] + ' '
                        idc = word_j.id
                        id_s.append(idc)
                        # print("idc", idc)

                        # print("1 +: ", word_j.id, word_j.form)
                        colored_sent_dict[word_j.id] = color_text_format    # для словаря цветовой разметки

                    if (word_j.id == current_id
                            # не выделяет (предложение 64 - усы)
                            and not (word_j.deprel == 'nsubj' and len(string.split(' ')) <= 1)  # выводит меньше ошибочных одиночных слов
                            and not (word_j.deprel == 'root' and len(string.split(' ')) <= 1) # выводит меньше ошибочных одиночных слов
                    ):
                        # print(word.form)

                        # нужно ли?
                        if not (idc == 0 or word_j.id == idc + 1):
                            string = ''
                            # print("id_s clear", id_s)
                            id_s.clear()

                        # print("2 +: ", string, id_s)
                        string += words_dict[current_id] + ' '
                        idc = current_id
                        # print("idc", idc)
                        id_s.append(idc)

                        # Отмечаем отобранное слово цветом
                        # для словаря цветовой разметки
                        colored_sent_dict[current_id] = color_text_format
                        # print(current_id)

                if len(phrases_for_name) > 0 and len(id_s) > 0 and id_s[0] == gl_id + 1:
                    phrases_for_name[len(phrases_for_name) - 1] += string
                # соединяет фразы, слова в которых идут друг за другом в предложении (составляя одну фразу)
                elif len(phrases_for_name) > 0 and len(id_s) > 0 and id_s[0] == gl_id:
                    string = " ".join(string.split(' ')[1:])
                    phrases_for_name[len(phrases_for_name) - 1] += string
                else:
                    phrases_for_name.append(string)
                if len(id_s) > 0:
                    gl_id = id_s[len(id_s) - 1]

    # Убрать phrases_for_name ?
    # print("Список фраз до последующей обработки:")
    # print(phrases_for_name)

    current_phrase_dict, colored_sent_dict = rules_for_set(colored_sent_dict, current_sentence)
    return current_phrase_dict, colored_sent_dict
    # return phrases_for_name, colored_sent_dict


# Функция последующей обработки отобранного набора фраз-описаний
def rules_for_set(colored_sent_dictionary, current_sentence):
    # print(current_sentence)

    # Фильтрация по правилам
    filtered_phrase_dict = dict()
    docUP = udpipe_model(current_sentence)
    for sent in docUP:
        current_phrase = ""
        id_list = []
        for word in sent.words:
            # print(word.id, word.form, word.deprel, word.head)
            if colored_sent_dictionary[word.id] != standard_format:
                if current_phrase != "":
                    current_phrase += " "
                current_phrase += word.form
                id_list.append(word.id)
            else:
                if current_phrase == "":
                    continue
                if current_phrase not in filtered_phrase_dict:
                    filtered_phrase_dict[current_phrase] = id_list
                else:
                    for cur_id in id_list:
                        filtered_phrase_dict[current_phrase].append(cur_id)

                # Фраза выделена (закончилась)
                c = current_phrase
                # print(c)

                # Фраза состоит из одного слова
                # print(morph.parse(c)[0].tag.POS)
                if (c.find(' ') == -1 and (morph.parse(c)[0].tag.POS != 'ADJF' and morph.parse(c)[0].tag.POS != 'ADJS'
                    and morph.parse(c)[0].tag.POS != 'PRTF' and morph.parse(c)[0].tag.POS != 'PRTS'
                    # новое NOUN
                    and morph.parse(c)[0].tag.POS != 'NOUN')):
                    # print("1 -")
                    for cur_id in filtered_phrase_dict[current_phrase]:
                        colored_sent_dictionary[cur_id] = standard_format

                # Фраза состоит больше, чем из одного слова
                if len(c.split()) > 1:
                    flag = 0
                    for f_p in c.split():
                        if (morph.parse(f_p)[0].tag.POS == 'ADJF' or morph.parse(f_p)[0].tag.POS == 'NOUN'
                                or morph.parse(f_p)[0].tag.POS == 'ADJS'
                                or morph.parse(f_p)[0].tag.POS == 'PRTF' or morph.parse(f_p)[0].tag.POS == 'PRTS'
                        ):
                            flag = 1

                    if flag == 0:
                        # print("7 -")
                        for cur_id in filtered_phrase_dict[current_phrase]:
                            colored_sent_dictionary[cur_id] = standard_format

                    if morph.parse(c.split()[-1])[0].tag.POS == 'NPRO':  # убирает местоимение с конца фразы
                        # print("4 [-1]")
                        colored_sent_dictionary[filtered_phrase_dict[current_phrase][-1]] = standard_format

                        # Новое (теперь последним словом стало предпоследнее)
                        if morph.parse(c.split()[-2])[0].tag.POS == 'PREP':  # убирает союз с конца фразы
                            # print("8 [-2]")
                            colored_sent_dictionary[filtered_phrase_dict[current_phrase][-2]] = standard_format

                    if morph.parse(c.split()[0])[0].tag.POS == 'NPRO':  # убирает местоимение из начала фразы
                        # print("5 [0]")
                        colored_sent_dictionary[filtered_phrase_dict[current_phrase][0]] = standard_format
                    if morph.parse(c.split()[0])[0].tag.POS == 'CONJ':  # убирает союз из начала фразы
                        # print("6 [0]")
                        colored_sent_dictionary[filtered_phrase_dict[current_phrase][0]] = standard_format
                    # Новое
                    if morph.parse(c.split()[-1])[0].tag.POS == 'PREP':  # убирает союз с конца фразы
                        # print("8 [-1]")
                        colored_sent_dictionary[filtered_phrase_dict[current_phrase][-1]] = standard_format

                # Проверка по словарю
                # Фраза состоит из одного слова
                if len(c.split(' ')) == 1:
                    if normal_form(c) not in possible_dictionary and normal_form(c) not in required_dictionary and c not in required_dictionary_plus:
                        # print("9 -")
                        for cur_id in filtered_phrase_dict[current_phrase]:
                            colored_sent_dictionary[cur_id] = standard_format

                # Фраза состоит больше, чем из одного слова
                else:
                    flag_in_required_dictionary = 0
                    flag_in_possible_dictionary = 0
                    for c_word in c.split(' '):
                        res_word = normal_form(c_word)
                        # print(morph.parse(c_word)[0].normal_form)
                        if res_word in required_dictionary or c_word in required_dictionary_plus:
                            # print(res_word + " in required_dictionary (or plus)")
                            flag_in_required_dictionary += 1
                        if res_word in possible_dictionary:
                            # print(res_word + " in possible_dictionary")
                            flag_in_possible_dictionary += 1
                    if flag_in_required_dictionary == 0 and flag_in_possible_dictionary < 2:
                        # print("10 -")
                        for cur_id in filtered_phrase_dict[current_phrase]:
                            colored_sent_dictionary[cur_id] = standard_format

                current_phrase = ""
                id_list = []

    # Соединение фраз после фильтрации
    phrase_dict = dict()
    docUP = udpipe_model(current_sentence)
    for sent in docUP:
        current_phrase = ""
        id_list = []
        for word in sent.words:
            # print(word.id, word.form, word.deprel, word.head)
            if colored_sent_dictionary[word.id] != standard_format:
                if current_phrase != "":
                    current_phrase += " "
                current_phrase += word.form
                id_list.append(word.id)
            else:
                if current_phrase == "":
                    continue
                if current_phrase not in phrase_dict:
                    phrase_dict[current_phrase] = id_list
                else:
                    for cur_id in id_list:
                        phrase_dict[current_phrase].append(cur_id)

                current_phrase = ""
                id_list = []

    # print("Соединенные фразы после фильтрации:")
    # print(phrase_dict)

    # Для вывода списка фраз
    print_set = []
    for key in phrase_dict:
        print_set.append(key)
    # print(print_set, '\n')

    return phrase_dict, colored_sent_dictionary


# Функция создания графа синтаксического разбора предложения
def make_graph(current_sentence):
    dot = graphviz.Digraph(comment='Parse Tree', format='png')

    docUP = udpipe_model(current_sentence)
    for sent in docUP:
        for word in sent.words:
            # Вывод характеристик для каждого слова в предложении (раскомментировать, если нужно)
            # print(word.id, word.form, word.deprel, word.head)

            # Создаем вершину (точку)
            dot.node(str(word.id), word.form)

    for sent in docUP:
        for word in sent.words:
            if word.id != 0:
                # Создаем ребро между двумя точками
                dot.edge(str(word.head), str(word.id), word.deprel)

    # Вывод графа в pdf файл
    dot.render('test-output/parse_tree' + '.gv', view=False)
