import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os


AREA = '1'
PERIOD = '31'
TOWN = 4
CATALOGUES = 48
COUNT = 100


def get_response_hh(language):
    vacancies_hh = []
    page = 0
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
        page += 1
        vacancies_hh.append(page_payload)

    return vacancies_hh, pages_number


def get_response_sj(language, api_key):
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


def predict_rub_salary_hh(vacancy):
    vacancy_salary = vacancy['salary']
    if not vacancy_salary:
        return None
    elif not vacancy_salary['from']:
        salary = int(vacancy_salary['to'] * 0.8)
        return salary
    elif not vacancy_salary['to']:
        salary = int(vacancy_salary['from'] * 1.2)
        return salary
    else:
        salary = int((vacancy_salary['from'] + vacancy_salary['to']) / 2)
        return salary


def predict_rub_salary_sj(vacancy):
    if vacancy['payment_to'] and vacancy['payment_from'] != 0:
        salary = int((vacancy['payment_from'] + vacancy['payment_to']) / 2)
        return salary
    elif not vacancy['payment_from']:
        salary = int(vacancy['payment_to'] * 0.8)
        return salary
    elif not vacancy['payment_to']:
        salary = int(vacancy['payment_from'] * 1.2)
        return salary


def creating_vacancy_table(average_salaries_for_vacancies, website):
    analyzed_salaries = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, analysis in average_salaries_for_vacancies.items():
        job_analysis = [language]
        for count in analysis.values():
            job_analysis.append(count)
        analyzed_salaries.append(job_analysis)

    title = f'{website} Moscow'
    table_instance = AsciiTable(analyzed_salaries, title)

    return table_instance


def creating_table_of_average_salaries_hh(languages):
    website = 'HeadHunter'
    average_salaries_for_vacancies = {}
    for language in languages:
        vacancies_hh, pages_number = get_response_hh(language)
        salaries = []
        for vacancies in vacancies_hh:
            for vacancy in vacancies['items']:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    salaries.append(salary)
        average = 0
        try:
            average = int(sum(salaries) / len(salaries))
        except ZeroDivisionError:
            print("Cannot divide by zero!")
        count = len(salaries)
        average_salaries_for_vacancies[language] = {
                'vacancies_found': pages_number,
                'vacancies_processed': count,
                'average_salary': average,
        }

    return average_salaries_for_vacancies, website


def creating_table_of_average_salaries_sj(languages, api_key):
    website = 'Super Job'
    average_salaries_for_vacancies = {}
    for language in languages:
        vacancies_sj, total = get_response_sj(language, api_key)
        salaries = []
        for vacancies in vacancies_sj:
            for vacancy in vacancies['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    salaries.append(salary)
        if salaries:
            average = 0
            try:
                average = int(sum(salaries) / len(salaries))
            except ZeroDivisionError:
                print("Cannot divide by zero!")
            count = len(salaries)
            average_salaries_for_vacancies[language] = {
                    'vacancies_found': total,
                    'vacancies_processed': count,
                    'average_salary': average,
            }

    return average_salaries_for_vacancies, website


def main():
    load_dotenv()
    api_key = os.getenv('API_KEY_SJ')
    programming_language = ['Python', 'Java', 'Javascript', 'Go', 'PHP', 'C++']

    average_salaries_for_vacancies, website = creating_table_of_average_salaries_sj(programming_language, api_key)
    table_sj = creating_vacancy_table(average_salaries_for_vacancies, website)

    average_salaries_for_vacancies, website = creating_table_of_average_salaries_hh(programming_language)
    table_hh = creating_vacancy_table(average_salaries_for_vacancies, website)

    print(f"{table_hh.table}\n\n{table_sj.table}")


if __name__ == '__main__':
    main()
