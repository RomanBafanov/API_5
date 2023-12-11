import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os


AREA = '1'
PERIOD = '31'
TOWN = 4
CATALOGUES = 48
COUNT = 100


def get_vacancies_hh(language):
    vacancies_hh = []
    page = 0
    total = 0
    pages_number = 1
    url = 'https://api.hh.ru/vacancies'
    while page < pages_number:
        params = {
            'text': f'NAME:Программист {language}',
            'area': AREA,
            'period': PERIOD,
            'page': page,
        }
        page_response = requests.get(url, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        total = page_payload['found']
        page += 1
        vacancies_hh.append(page_payload)

    return vacancies_hh, total


def get_vacancies_sj(language, api_key):
    vacancies_sj = []
    page = 0
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': api_key,
    }
    while True:
        params = {
            'town': TOWN,
            'catalogues': CATALOGUES,
            'count': COUNT,
            'keyword': language,
            'page': page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_response = response.json()
        total = page_response['total']
        vacancies_sj.append(page_response)
        if not page_response['more']:
            return vacancies_sj, total
        else:
            page += 1


def predict_rub_salary(payment_to, payment_from):
    if not payment_to and not payment_from:
        return None
    elif not payment_to:
        salary = int(payment_from * 1.2)
        return salary
    elif not payment_from:
        salary = int(payment_to * 0.8)
        return salary
    else:
        salary = int((payment_from + payment_to) / 2)
        return salary


def create_a_table_of_average_salaries(average_salaries_for_vacancies, website):
    analyzed_salaries = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, analysis in average_salaries_for_vacancies.items():
        job_analysis = [language]
        for count in analysis.values():
            job_analysis.append(count)
        analyzed_salaries.append(job_analysis)

    title = f'{website} Moscow'
    table_instance = AsciiTable(analyzed_salaries, title)

    return table_instance


def find_average_salaries_hh(languages):
    average_salaries_for_vacancies = {}
    for language in languages:
        vacancies_hh, total = get_vacancies_hh(language)
        salaries = []
        for vacancies in vacancies_hh:
            for vacancy in vacancies['items']:
                vacancy_salary = vacancy['salary']
                if vacancy_salary:
                    payment_to = vacancy_salary['to']
                    payment_from = vacancy_salary['from']
                    salary = predict_rub_salary(payment_to, payment_from)
                else:
                    salary = None
                if salary:
                    salaries.append(salary)
        try:
            average = int(sum(salaries) / len(salaries))
        except ZeroDivisionError:
            print("Cannot divide by zero!")
            average = 0

        count = len(salaries)
        average_salaries_for_vacancies[language] = {
            'vacancies_found': total,
            'vacancies_processed': count,
            'average_salary': average,
        }

    return average_salaries_for_vacancies


def find_average_salaries_sj(languages, api_key):
    average_salaries_for_vacancies = {}
    for language in languages:
        vacancies_sj, total = get_vacancies_sj(language, api_key)
        salaries = []
        for vacancies in vacancies_sj:
            for vacancy in vacancies['objects']:
                payment_to = vacancy['payment_to']
                payment_from = vacancy['payment_from']
                salary = predict_rub_salary(payment_to, payment_from)
                if salary:
                    salaries.append(salary)
        try:
            average = int(sum(salaries) / len(salaries))
        except ZeroDivisionError:
            print("Cannot divide by zero!")
            average = 0

        count = len(salaries)
        average_salaries_for_vacancies[language] = {
            'vacancies_found': total,
            'vacancies_processed': count,
            'average_salary': average,
        }

    return average_salaries_for_vacancies


def main():
    load_dotenv()
    api_key = os.getenv('API_KEY_SJ')
    programming_language = ['Python', 'Java', 'Javascript', 'Go', 'PHP', 'C++']

    average_salaries_for_vacancies = find_average_salaries_sj(programming_language, api_key)
    table_sj = create_a_table_of_average_salaries(average_salaries_for_vacancies, 'Super Job')

    average_salaries_for_vacancies = find_average_salaries_hh(programming_language)
    table_hh = create_a_table_of_average_salaries(average_salaries_for_vacancies, 'HeadHunter')

    print(f"{table_hh.table}\n\n{table_sj.table}")


if __name__ == '__main__':
    main()
