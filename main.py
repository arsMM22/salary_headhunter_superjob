import requests
import os
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        middle_salary = int((salary_from + salary_to) / 2)
    elif salary_to:
        middle_salary = int(salary_to * 0.8)
    elif salary_from:
        middle_salary = int(salary_from * 1.2)
    else:
        middle_salary = None
    return middle_salary


def get_hh_statistic():
    languages = ["python", "c", "c#", "c++", "java", "js", "ruby", "go", "1c"]
    vacancies_found_hh = {}
    for language in languages:
        all_salaries = []
        for page in count(0, 1):
            id = 1
            period = 30
            payload = {
                "text": f"программист {language}",
                "area": id,
                "period": period,
                "page": page
            }
            response = requests.get('https://api.hh.ru/vacancies',
                                    params=payload)
            response.raise_for_status()
            vacancies = response.json()
            vacancies_found = vacancies["found"]
            if page >= response.json()["pages"] - 1:
                break
            for vacansy_salary in vacancies["items"]:
                salary = vacansy_salary.get("salary")
                if salary and salary["currency"]:
                    predicted_rub_salary = predict_rub_salary(
                        vacansy_salary["salary"].get("from"),
                        vacansy_salary["salary"].get("to"))
                    if predicted_rub_salary:
                        all_salaries.append(predicted_rub_salary)
        average_salaru = None
        if all_salaries:
            average_salary = int(sum(all_salaries) / len(all_salaries))
        vacancies_found_hh[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
        }
    return vacancies_found_hh


def get_sj_statistic(sj_token):
    languages = ['Python', 'Java']
    vacancies_found_sj = {}
    for language in languages:
        all_salaries = []
        for page in count(0, 1):
            period = 30
            payload = {
                "keyword": language,
                "town": "Moscow",
                "period": period,
                "page": page
            }
            headers = {"X-Api-App-Id": sj_token}
            response = requests.get('https://api.superjob.ru/2.0/vacancies',
                                    params=payload,
                                    headers=headers)
            response.raise_for_status()
            vacancies = response.json()
            vacancies_found = vacancies["total"]
            if not vacancies["objects"]:
                break
            for vacansy_salary in vacancies["objects"]:
                predicted_rub_salary = predict_rub_salary(
                    vacansy_salary["payment_from"],
                    vacansy_salary["payment_to"])
                if predicted_rub_salary:
                    all_salaries.append(predicted_rub_salary)
        average_salary = None
        if all_salaries:
            average_salary = int(sum(all_salaries) / len(all_salaries))
        vacancies_found_sj[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
        }

    return vacancies_found_sj


def get_table(statistic):
    table_data = [[
        "Язык програмирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата"
    ]]
    for language, vacansy in statistic.items():
        table_data.append([
            language, vacansy["vacancies_found"],
            vacansy["vacancies_processed"], vacansy["average_salary"]
        ])
    table = AsciiTable(table_data)
    return table.table


def main():
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    print(get_table(get_sj_statistic(sj_token)))
    print(get_table(get_hh_statistic()))


if __name__ == '__main__':
    main()
