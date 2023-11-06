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
    info_about_vacancies_hh = []
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
        info_about_vacancies_hh.append(page_payload)

    return info_about_vacancies_hh, pages_number


def get_response_sj(language, api_key):
    info_about_vacancies_sj = []
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
        info_about_vacancies_sj.append(page_response)
        if not page_response['more']:
            return info_about_vacancies_sj, total
        else:
            page += 1


def predict_rub_salary_hh(vacancy):
    vac_salary = vacancy['salary']
    if vac_salary:
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
    analyzed_salaries = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, analysis in average_salaries_for_vacancies.items():
        job_analysis = [language]
        for count in analysis.values():
            job_analysis.append(count)
        analyzed_salaries.append(job_analysis)

    title = f'{website} Moscow'
    table_instance = AsciiTable(analyzed_salaries, title)

    return table_instance


def create_salaries_hh(languages):
    website = 'HeadHunter'
    average_salaries_for_vacancies = {}
    for language in languages:
        info_about_vacancies, pages_number = get_response_hh(language)
        salaries = []
        for vacancies in info_about_vacancies:
            for vacancy in vacancies['items']:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    salaries.append(salary)
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

    table = output_console(average_salaries_for_vacancies, website)

    return table


def create_salaries_sj(languages, api_key):
    website = 'Super Job'
    average_salaries_for_vacancies = {}
    for language in languages:
        info_about_vacancies_sj, total = get_response_sj(language, api_key)
        salaries = []
        for vacancies in info_about_vacancies_sj:
            for vacancy in vacancies['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    salaries.append(salary)
        if salaries:
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

    table = output_console(average_salaries_for_vacancies, website)

    return table


def main():
    load_dotenv()
    api_key = os.getenv('API_KEY_SJ')
    programming_language = ['Python', 'Java', 'Javascript', 'Go', 'PHP', 'C++']
    table_hh = create_salaries_hh(programming_language)
    table_sj = create_salaries_sj(programming_language, api_key)
    print(f"{table_hh.table}\n\n{table_sj.table}")


if __name__ == '__main__':
    main()
