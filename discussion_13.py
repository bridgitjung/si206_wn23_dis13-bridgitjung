import unittest
import sqlite3
import json
import os
# import numpy as np
import matplotlib.pyplot as plt
# starter code

# Create Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


# TASK 1
# CREATE TABLE FOR EMPLOYEE INFORMATION IN DATABASE AND ADD INFORMATION
def create_employee_table(cur, conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS Employees (
                    employee_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    hire_date DATE NOT NULL,
                    job_id INTEGER NOT NULL,
                    salary INTEGER NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES Jobs(job_id)
                    )''')
    conn.commit()
    # pass

# ADD EMPLOYEE'S INFORMTION TO THE TABLE

def add_employee(filename, cur, conn):
    #load .json file and read job data
    # WE GAVE YOU THIS TO READ IN DATA
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename)))
    file_data = f.read()
    f.close()
    # THE REST IS UP TO YOU
    # print(file_data)

    cur.execute("""
            DELETE FROM Employees
        """)

    data = json.loads(file_data)
    for employee in data:
        cur.execute("""
            INSERT INTO Employees (first_name, last_name, hire_date, job_id, salary)
            VALUES (?, ?, ?, ?, ?)
        """, (employee['first_name'], employee['last_name'], employee['hire_date'], employee['job_id'], employee['salary']))
    conn.commit()

    # conn.commit()
    # pass

# TASK 2: GET JOB AND HIRE_DATE INFORMATION
def job_and_hire_date(cur, conn):
    cur.execute('''
        SELECT job_title
        FROM employees
        JOIN jobs ON employees.job_id = jobs.job_id
        WHERE hire_date = (
            SELECT MIN(hire_date) 
            FROM employees
        )
    ''')
    job_title = cur.fetchone()[0]
    return job_title

# TASK 3: IDENTIFY PROBLEMATIC SALARY DATA
# Apply JOIN clause to match individual employees
def problematic_salary(cur, conn):
    cur.execute('''
        SELECT first_name, last_name
        FROM employees
        JOIN jobs ON employees.job_id = jobs.job_id
        WHERE employees.salary < jobs.min_salary OR employees.salary > jobs.max_salary
    ''')
    problematic_employees = cur.fetchall()
    return problematic_employees
    # pass

# TASK 4: VISUALIZATION
def visualization_salary_data(cur, conn):
    cur.execute('''
        SELECT job_title, salary, min_salary, max_salary
        FROM employees
        JOIN jobs ON employees.job_id = jobs.job_id
    ''')
    data = cur.fetchall()

    salary_by_job = {}
    min_salary_by_job = {}
    max_salary_by_job = {}
    for job, salary, min_salary, max_salary in data:
        if job not in salary_by_job:
            salary_by_job[job] = []
            min_salary_by_job[job] = min_salary
            max_salary_by_job[job] = max_salary
        salary_by_job[job].append(salary)

    x = []
    y = []
    for job in salary_by_job:
        for salary in salary_by_job[job]:
            x.append(job)
            y.append(salary)

    fig, ax = plt.subplots()
    ax.scatter(x, y)
    for job in min_salary_by_job:
        ax.scatter(job, min_salary_by_job[job], color='red', marker='x')
        ax.scatter(job, max_salary_by_job[job], color='red', marker='x')

    ax.set_xlabel('Job Title')
    ax.set_ylabel('Salary')
    ax.set_title('Salary Data by Job Title')

    plt.xticks(rotation=90)

    plt.show()
    # pass

class TestDiscussion12(unittest.TestCase):
    def setUp(self) -> None:
        self.cur, self.conn = setUpDatabase('HR.db')

    def test_create_employee_table(self):
        self.cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='employees'")
        table_check = self.cur.fetchall()[0][0]
        self.assertEqual(table_check, 1, "Error: 'employees' table was not found")
        self.cur.execute("SELECT * FROM employees")
        count = len(self.cur.fetchall())
        self.assertEqual(count, 13)

    def test_job_and_hire_date(self):
        self.assertEqual('President', job_and_hire_date(self.cur, self.conn))

    def test_problematic_salary(self):
        sal_list = problematic_salary(self.cur, self.conn)
        self.assertIsInstance(sal_list, list)
        self.assertEqual(sal_list[0], ('Valli', 'Pataballa'))
        self.assertEqual(len(sal_list), 4)


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('HR.db')
    create_employee_table(cur, conn)

    add_employee("employee.json",cur, conn)

    job_and_hire_date(cur, conn)

    wrong_salary = (problematic_salary(cur, conn))
    print(wrong_salary)

    visualization_salary_data(cur, conn)

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)

