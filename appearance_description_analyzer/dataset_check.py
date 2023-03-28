# Программа для сравнения результата работы программы (нахождения описаний) с образцовыми описаниями из dataset
import numpy as np
import csv
import appearance_description_analyzer.appearance_description_analyzer as analyzer


def dataset_check(dataset_filename):
    text_correct = []
    text_sentences = []
    with open(dataset_filename, 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            text_correct.append(row[4])
            text_sentences.append(row[3])

    del text_correct[0]
    del text_sentences[0]

    # Лист правильных описаний из dataset
    list_of_correct_descriptions = []
    for line in text_correct:
        list_of_current_line_correct = line.lower().split('|')
        if line == '[not]':
            list_of_current_line_correct = []
        list_of_correct_descriptions.append(list_of_current_line_correct)

    # Текст для обработки
    text = '\n'.join(text_sentences)

    # Вызов функции обработки предложений из dataset
    text_to_check = analyzer.sentences_from_dateset_for_description(text, False)

    # Лист описаний из программы
    list_of_descriptions_to_check = []

    for line in text_to_check.values():
        list_of_current_line = []
        line = str(line)
        for phrase in line[1:-1].lower().split(', '):
            list_of_current_line.append(phrase[1:-1])
        if line == '[]':
            list_of_current_line = []
        list_of_descriptions_to_check.append(list_of_current_line)

    # Лист количество описаний в предложении (образцовых)
    list_amount = []
    for sent in list_of_correct_descriptions:
        list_amount.append(len(sent))

    # print(list_amount)

    # Лист значений нахождения полноты описаний
    list_completeness = []

    # Лист значений нахождения полноты точности
    list_accuracy = []

    # Лист значений количества правильно найденных описаний
    list_correct_descriptions = []

    # Лист значений количества всех найденных описаний
    list_all_descriptions = []
    for sent in list_of_descriptions_to_check:
        list_all_descriptions.append(len(sent))

    for i in range(len(list_of_descriptions_to_check)):
        current_amount = 0
        correct_str = ', '.join(list_of_correct_descriptions[i])
        for from_program in list_of_descriptions_to_check[i]:
            if correct_str.find(from_program) != -1:
                current_amount += 1
                list_of_descriptions_to_check[i].remove(from_program)
                # print(from_program)
        program_str = ', '.join(list_of_descriptions_to_check[i])
        for correct in list_of_correct_descriptions[i]:
            if program_str.find(correct) != -1:
                current_amount += 1
                # print(correct)
        # Подсчет полноты
        if list_amount[i] != 0:
            list_completeness.append(current_amount / list_amount[i])
        elif len(list_of_descriptions_to_check[i]) > 0:
            list_completeness.append(0)
        else:
            list_completeness.append(1)
        # Подсчет точности
        if list_all_descriptions[i] != 0:
            list_accuracy.append(current_amount / list_all_descriptions[i])
        elif len(list_of_descriptions_to_check[i]) > 0:
            list_accuracy.append(0)
        else:
            list_accuracy.append(1)
        # print("Количество правильно найденных описаний: " + str(current_amount))
        # print("Полнота в предложении: " + str(list_completeness[i]))
        list_correct_descriptions.append(current_amount)

    # print(list_completeness)
    # print(list_accuracy)

    # Полнота: кол-во правильно найденных описаний / кол-во описаний (образцовых)
    print("Среднее значение полноты (по предложению): " + str(round(np.mean(list_completeness), 2)))
    # print("Полнота (по тексту): " + str(np.sum(list_correct_descriptions) / np.sum(list_amount)))

    # Точность: кол-во правильно найденных описаний / кол-во всех найденных описаний
    print("Среднее значение точности (по предложению): " + str(round(np.mean(list_accuracy), 3)))
    # print("Точность (по тексту): " + str(np.sum(list_correct_descriptions) / np.sum(list_all_descriptions)))
