import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os


def get_response_hh(language):
    data = []
    page = 0
    pages_number = 1
    url = 'https://api.hh.ru/vacancies'
    while page < pages_number:
        params = {
            'text': f'NAME:Программист {language}',
            'area': '1',
            'period': '31',
            'page': page,
        }
        page_response = requests.get(url, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        page += 1
        data.append(page_payload)

    return data, pages_number


def get_response_sj(language, api_key):
    data = []
    page = 0
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': api_key,
    }
    while True:
        params = {
            'town': 4,
            'catalogues': 48,
            'count': 100,
            'keyword': language,
            'page': page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_response = response.json()
        total = page_response['total']
        data.append(page_response)
        if page_response['more'] == False:
            return data, total
        else:
            page += 1


def predict_rub_salary_hh(vacancy):
    vac_salary = vacancy['salary']
    if vac_salary is not None:
        if vac_salary['from'] is None:
            salary = int(vac_salary['to'] * 0.8)
            return salary
        elif vac_salary['to'] is None:
            salary = int(vac_salary['from'] * 1.2)
            return salary
        else:
            salary = int((vac_salary['from'] + vac_salary['to']) / 2)
            return salary
    else:
        return None


def predict_rub_salary_sj(vacancy):
    if vacancy['payment_to'] or vacancy['payment_from'] == 0:
        if vacancy['payment_from'] == 0 and vacancy['payment_to'] != 0:
            salary = int(vacancy['payment_to'] * 0.8)
            return salary
        elif vacancy['payment_to'] == 0 and vacancy['payment_from'] != 0:
            salary = int(vacancy['payment_from'] * 1.2)
            return salary
    else:
        salary = int((vacancy['payment_from'] + vacancy['payment_to']) / 2)
        return salary


def output_console(average_salaries_for_vacancies, website):
    analyzed_salaries = []
    analyzed_salaries.append(['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'])
    for language, analysis in average_salaries_for_vacancies.items():
        job_analysis = []
        job_analysis.append(language)
        for count in analysis.values():
            job_analysis.append(count)
        analyzed_salaries.append(job_analysis)
    title = f'{website} Moscow'
    table_instance = AsciiTable(analyzed_salaries, title)
    print(table_instance.table)


def create_salaries_hh(languages):
    website = 'HeadHunter'
    average_salaries_for_vacancies = {}
    for language in languages:
        average_salaries_for_vacancies[language] = {}
        data, pages_number = get_response_hh(language)
        salaries = []
        average_salaries_for_vacancies[language]['vacancies_found'] = pages_number
        count = 0
        for vacancies in data:
            for vacancy in vacancies['items']:
                salary = predict_rub_salary_hh(vacancy)
                if salary is not None:
                    count += 1
                    salaries.append(salary)
        average_salaries_for_vacancies[language]['vacancies_processed'] = count
        average = int(sum(salaries) / len(salaries))
        average_salaries_for_vacancies[language]['average_salary'] = average

    output_console(average_salaries_for_vacancies, website)


def create_salaries_sj(languages):
    website = 'Super Job'
    average_salaries_for_vacancies = {}
    load_dotenv()
    api_key = os.getenv('API_KEY_SJ')
    for language in languages:
        average_salaries_for_vacancies[language] = {}
        data, total = get_response_sj(language, api_key)
        average_salaries_for_vacancies[language]['vacancies_found'] = total
        salaries = []
        count = 0
        for d in data:
            for vacancy in d['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary is not None:
                    count += 1
                    salaries.append(salary)
        if salaries:
            average_salaries_for_vacancies[language]['vacancies_processed'] = count
            average = int(sum(salaries) / len(salaries))
            average_salaries_for_vacancies[language]['average_salary'] = average

    output_console(average_salaries_for_vacancies, website)


def main():
    programming_language = ['Python', 'Java', 'Javascript', 'Go', 'PHP', 'C++',]
    create_salaries_hh(programming_language)
    create_salaries_sj(programming_language)


if __name__ == '__main__':
    main()
