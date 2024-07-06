import requests
import sqlite3
import sys

DATABASE = '/db/vacancies.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vacancies
                 (id TEXT PRIMARY KEY,
                  company_id TEXT,
                  company_name TEXT,
                  title TEXT,
                  experience TEXT,
                  skills TEXT,
                  salary TEXT,
                  url TEXT)''')
    conn.commit()
    conn.close()

def get_vacancies(keyword, area=113, per_page=10):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": area,  
        "per_page": per_page,
    }
    headers = {
        "User-Agent": "Your User Agent",
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        result = []
        for vacancy in vacancies:
            vacancy_id = vacancy.get("id")
            company_id = vacancy.get("employer", {}).get("id")
            company_name = vacancy.get("employer", {}).get("name")
            vacancy_title = vacancy.get("name")
            import requests
import sqlite3
import sys

DATABASE = '/db/vacancies.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vacancies
                 (id TEXT PRIMARY KEY,
                  company_id TEXT,
                  company_name TEXT,
                  title TEXT,
                  experience TEXT,
                  skills TEXT,
                  salary TEXT,
                  url TEXT)''')
    conn.commit()
    conn.close()

def get_vacancies(keyword, area=113, per_page=10):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": area,  
        "per_page": per_page,
    }
    headers = {
        "User-Agent": "Your User Agent",
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        result = []
        for vacancy in vacancies:
            vacancy_id = vacancy.get("id")
            company_id = vacancy.get("employer", {}).get("id")
            company_name = vacancy.get("employer", {}).get("name")
            vacancy_title = vacancy.get("name")
            experience = vacancy.get("experience", {}).get("name")
            skills = ", ".join([skill.get("name") for skill in vacancy.get("key_skills", [])])
            salary = vacancy.get("salary")
            salary_from = salary.get("from") if salary else "Не указано"
            salary_to = salary.get("to") if salary else "Не указано"
            salary_currency = salary.get("currency") if salary else ""
            salary_formatted = f"{salary_from} - {salary_to} {salary_currency}" if salary else "Не указано"
            result.append({
                "vacancy_id": vacancy_id,
                "company_id": company_id,
                "company_name": company_name,
                "vacancy_title": vacancy_title,
                "experience": experience,
                "skills": skills,
                "salary": salary_formatted,
                "url": vacancy.get("alternate_url"),
            })
        return result
    else:
        print(f"Request failed with status code: {response.status_code}")
        return []

def save_vacancies(vacancies):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    for vacancy in vacancies:
        c.execute('''INSERT OR IGNORE INTO vacancies
                     (id, company_id, company_name, title, experience, skills, salary, url)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (vacancy["vacancy_id"], vacancy["company_id"], vacancy["company_name"],
                   vacancy["vacancy_title"], vacancy["experience"], vacancy["skills"],
                   vacancy["salary"], vacancy["url"]))
    conn.commit()
    conn.close()

def main():
    init_db()

    if len(sys.argv) < 2:
        print("Usage: python parser.py <keyword>")
        return
    
    keyword = sys.argv[1]
    area = 113  
    per_page = 10

    try:
        vacancies = get_vacancies(keyword, area, per_page)
        save_vacancies(vacancies)
        print(f"Saved {len(vacancies)} vacancies to the database.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
