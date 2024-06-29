import requests
from itertools import count
from terminaltables import AsciiTable
super_job_token = "v3.r.138401654.adc7fa533f117f616aebef2822a4be9690583eb8.3198eaa9852a16c8ceaa85335ea73be63a66e029"
def predict_rub_salary(salary_from=None,salary_to=None):
    if salary_from and salary_to:
        middle_salary = int((salary_from+salary_to)/2)
    elif salary_to:
        middle_salary = int(salary_to*0.8)
    elif salary_from:
        middle_salary = int(salary_from*1.2)
    else:
        middle_salary=None 
    return middle_salary
def hh_statistic():
    languages = ["python", "c", "c#", "c++", "java", "js", "ruby", "go", "1c"]
    vacansis_found = {}
    for language in languages:
        all_money = []
        for page in count(0,1):
            payload = {"text": f"программист {language}","area": 1,"period": 30,"page":page}
            response = requests.get('https://api.hh.ru/vacancies', params = payload)
            response.raise_for_status()
            vacansy_found = response.json()["found"] 
            vacansis_salary = response.json()["items"]
            if page >= response.json()["pages"]-1:
                break
            for vacansy_salary in vacansis_salary:
                money = vacansy_salary.get("salary")
                if money and money["currency"]:    
                    predicted_rub_salary = predict_rub_salary(vacansy_salary["salary"].get("from"),vacansy_salary["salary"].get("to"))
                    if predicted_rub_salary:
                        all_money.append(predicted_rub_salary)
        if all_money:
            average_salary = int(sum(all_money)/len(all_money))
        vacansis_found[language]={
            "vacancies_found":vacansy_found,
            "vacancies_processed":len(all_money),
            "average_salary":average_salary
        }
    return vacansis_found
def sj_statistic():
    languages = ['Python','Java']
    vacansis_found = {}
    for language in languages:
        all_money = []
        for page in count(0,1):
            payload = {"keyword": language,"town": "Moscow","period": 30,"page":page}
            headers ={"X-Api-App-Id": super_job_token}
            response = requests.get('https://api.superjob.ru/2.0/vacancies', params=payload,headers=headers)
            response.raise_for_status()
            vacansy_found = response.json()["total"] 
            vacansis_salary = response.json()["objects"]
            if not vacansis_salary:
                break
            for vacansy_salary in vacansis_salary:    
                predicted_rub_salary = predict_rub_salary(vacansy_salary["payment_from"],vacansy_salary["payment_to"])
                if predicted_rub_salary:
                    all_money.append(predicted_rub_salary)
        if all_money:
            average_salary = int(sum(all_money)/len(all_money))
        vacansis_found[language]={
            "vacancies_found":vacansy_found,
            "vacancies_processed":len(all_money),
            "average_salary":average_salary
        }
    return vacansis_found

def get_table(statistic):
    table_data = [
           ["Язык програмирования","Вакансий найдено","Вакансий обработано","Средняя зарплата"]
        ]
    for language,vacansy in statistic.items():
        table_data.append([
            language,
            vacansy["vacancies_found"],
            vacansy["vacancies_processed"],
            vacansy["average_salary"]
        ])
    table = AsciiTable(table_data)
    return table.table
print(get_table(sj_statistic()))
print(get_table(hh_statistic()))