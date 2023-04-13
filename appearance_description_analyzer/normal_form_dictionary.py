import pymorphy2

morph = pymorphy2.MorphAnalyzer()


# Функция возвращает начальную форму слова
def normal_form(word):
    res_word = morph.parse(word)[0].normal_form
    return res_word


def make_thesaurus_normal_forms(thesaurus_filename, result_filename):
    thesaurus = open(thesaurus_filename, 'r', encoding='utf-8').read()
    result_file = open(result_filename, 'w', encoding='utf-8')

    for line in thesaurus.split('\n'):
        if line == '':
            continue
        dictionary = dict()
        full_line = line.split(',')
        for r_word in full_line[0].split(';'):
            if r_word == '':
                continue
            cur_word = morph.parse(r_word)[0].normal_form
            part_of_speech = morph.parse(cur_word)[0].tag.POS
            if part_of_speech in dictionary:
                if cur_word not in dictionary[part_of_speech]:
                    dictionary[part_of_speech].append(cur_word)
            else:
                dictionary[part_of_speech] = [cur_word]
        for key, value in dictionary.items():
            first_part = ';'.join(value)
            second_part = key
            if second_part == None:
                second_part = "None"
            third_part = full_line[2]
            result_file.write(first_part + "," + second_part + "," + third_part + '\n')

    result_file.close()

