import appearance_description_analyzer.normal_form_dictionary as normal_dict
import pymorphy2
morph = pymorphy2.MorphAnalyzer()


# dict_type - тип словаря (0 - обязательный, 1 - необязательный)
def add_to_dict(dict_type, word, word_theme='описание'):
    if dict_type == 0:
        required_thesaurus_file = open('appearance_description_analyzer/required_thesaurus_normal_forms.txt', 'a',
                                       encoding='utf-8')
        required_thesaurus_file.write(word + "," + "," + word_theme + '\n')
        required_thesaurus_file.close()
        # Преобразование словаря в нормальную форму
        normal_dict.make_thesaurus_normal_forms('appearance_description_analyzer/required_thesaurus_normal_forms.txt',
                                                'appearance_description_analyzer/required_thesaurus_normal_forms.txt')
        return "Слово записано в обязательный словарь"
    elif dict_type == 1:
        possible_thesaurus_file = open('appearance_description_analyzer/possible_thesaurus_normal_forms.txt', 'a',
                                       encoding='utf-8')
        possible_thesaurus_file.write(word + "," + "," + word_theme + '\n')
        possible_thesaurus_file.close()
        # Преобразование словаря в нормальную форму
        normal_dict.make_thesaurus_normal_forms('appearance_description_analyzer/possible_thesaurus_normal_forms.txt',
                                                'appearance_description_analyzer/possible_thesaurus_normal_forms.txt')
        return "Слово записано в необязательный словарь"
    else:
        return "Задайте тип словаря: 0 - обязательный, 1 - необязательный"


def remove_from_dict(dict_type, word):
    normal_word = morph.parse(word)[0].normal_form
    if dict_type == 0:
        text = open('appearance_description_analyzer/required_thesaurus_normal_forms.txt', 'r', encoding='utf-8').read()
        if text.find(normal_word) == -1:
            return "Данного слова нет в обязательном словаре"
        else:
            text = text.replace(normal_word, '')
            required_thesaurus_file = open('appearance_description_analyzer/required_thesaurus_normal_forms.txt', 'w',
                                           encoding='utf-8')
            required_thesaurus_file.write(text)
            required_thesaurus_file.close()
            # Преобразование словаря в нормальную форму
            normal_dict.make_thesaurus_normal_forms(
                'appearance_description_analyzer/required_thesaurus_normal_forms.txt',
                'appearance_description_analyzer/required_thesaurus_normal_forms.txt')
            return "Слово удалено из обязательного словаря"
    elif dict_type == 1:
        text = open('appearance_description_analyzer/possible_thesaurus_normal_forms.txt', 'r', encoding='utf-8').read()
        if text.find(normal_word) == -1:
            return "Данного слова нет в необязательном словаре"
        else:
            text = text.replace(normal_word, '')
            possible_thesaurus_file = open('appearance_description_analyzer/possible_thesaurus_normal_forms.txt', 'w',
                                           encoding='utf-8')
            possible_thesaurus_file.write(text)
            possible_thesaurus_file.close()
            # Преобразование словаря в нормальную форму
            normal_dict.make_thesaurus_normal_forms(
                'appearance_description_analyzer/possible_thesaurus_normal_forms.txt',
                'appearance_description_analyzer/possible_thesaurus_normal_forms.txt')
            return "Слово удалено из необязательного словаря"
    else:
        return "Задайте тип словаря: 0 - обязательный, 1 - необязательный"
