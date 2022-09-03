import PyPDF2
import re
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from employees import Employee

PATH_2019 = "data/2019_report.pdf"
PATH_2020 = "data/2020_report.pdf"
PATH_2021 = "data/2021_report.pdf"


# Accept employee data in form of the regex match. Pass in the path to add correct year's data - hires in 2021/21
# will not be added with the 2019 batch.
def add_employee(data, path_name):
    full_name = f"{data[2]} {data[0]}"
    search_name = trim_name(data)
    new_employee = Employee()
    if path_name == PATH_2019:
        new_employee.full_name_2019 = full_name
        new_employee.salary_2019 = data[4]
        new_employee.expenses_2019 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)
    if path_name == PATH_2020:
        new_employee.full_name_2020 = full_name
        new_employee.salary_2020 = data[4]
        new_employee.expenses_2020 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)
    if path_name == PATH_2021:
        new_employee.full_name_2021 = full_name
        new_employee.salary_2021 = data[4]
        new_employee.expenses_2021 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)


# Trim away initials and remove '.' to help search for matches between years. Do as LAST, FIRST to use this name for
# the saving name for the figures.
def trim_name(data):
    full_name = f"{data[0].replace('.', '')}, {data[2].replace('.', '')}"
    split_name = full_name.split(" ")
    stripped_name = []
    for name in split_name:
        if len(name) != 1:
            stripped_name.append(name.title())
    stripped_name = " ".join(stripped_name)
    return stripped_name


# Extract and clean text from all three reports. Each dictionary entry contains a data list for a given report/year.
# Each entry in a list for a given report/year represents the cleaned text from one data page.
report_text = {}
for report_name in [PATH_2019, PATH_2020, PATH_2021]:
    with open(report_name, "rb") as file:
        pdf = PyPDF2.PdfFileReader(file)
        report_text[report_name] = []
        for n in range(pdf.getNumPages()):
            page = pdf.getPage(n)
            text = page.extractText()
            text = text.replace("\n", "")
            text = text.replace("$", "")
            text = text.replace("Name", "")
            # Replace sequences of multiple whitespaces with one whitespace.
            text = re.sub(r"\s+", " ", text)
            # This phrase shows up on pages that contain data and is easy to split around.
            text = text.split("Remuneration Expenses*")
            # Pages with data will have it in these two indices. If not it won't split, and this will throw an error.
            try:
                report_text[report_name].append(f"{text[1].strip()} {text[2].strip()}")
            except IndexError:
                pass

# Dictionary where each entry will be a list of all regex matches for a given report/year.
data_matches = {}
for report_name in report_text:
    data_matches[report_name] = []
    for page in report_text[report_name]:
        # Gets first name (option of multiple first names), last name (option of multiple last names), salary, expenses
        # Six return fields: 0-full last name, 1-ignore, used to find multiple names 2-full first name
        # 3-ignore, used to find multiple names, 4-salary, 5-expenses
        matches = re.findall(r"(([^\s\d,]+ )*[^\s\d,]+), (([^\s\d,]+ )*[^\s\d,]+) (\d+,\d{3}) (-|\d*,*\d+)", page)
        for match in matches:
            data_matches[report_name].append(match)

employee_list = []
for report_name, report_data in data_matches.items():
    if report_name == PATH_2019:
        # Start with 2019 as baseline - every employee gets an entry.
        for entry in report_data:
            add_employee(entry, report_name)
    elif report_name == PATH_2020:
        # Add data to existing employee if search name found. Otherwise, add as a new employee.
        for entry in report_data:
            search_name = trim_name(entry)
            match_found = False
            for employee in employee_list:
                if employee.search_name == search_name:
                    employee.full_name_2020 = f"{entry[2]} {entry[0]}"
                    employee.salary_2020 = entry[4]
                    employee.expenses_2020 = entry[5]
                    match_found = True
                    break
            if not match_found:
                add_employee(entry, report_name)
    elif report_name == PATH_2021:
        # Add data to existing employee if search name found. Otherwise, add as a new employee.
        for entry in report_data:
            search_name = trim_name(entry)
            match_found = False
            for employee in employee_list:
                if employee.search_name == search_name:
                    employee.full_name_2021 = f"{entry[2]} {entry[0]}"
                    employee.salary_2021 = entry[4]
                    employee.expenses_2021 = entry[5]
                    match_found = True
                    break
            if not match_found:
                add_employee(entry, report_name)
    else:
        print("God help you if you made it here.")

def make_int(salary):
    if salary == None:
        return 0
    else:
        return int(salary.replace(",", ""))

# Creation of MySQL table
engine = create_engine("mysql+mysqldb://jaymes:123456@localhost/ubc-salaries", echo=True, future=True)

Base = declarative_base()

class Salaries(Base):
    __tablename__ = "employee_salaries"

    id = Column(Integer, primary_key=True)
    search_name = Column(String(100))
    salary_2019 = Column(Integer)
    salary_2020 = Column(Integer)
    salary_2021 = Column(Integer)

Base.metadata.create_all(engine)

with Session(engine) as session:
    db_entries = []

    for employee in employee_list:
        entry = Salaries(
            search_name = employee.search_name,
            salary_2019 = make_int(employee.salary_2019),
            salary_2020 = make_int(employee.salary_2020),
            salary_2021 = make_int(employee.salary_2021),
        )
        db_entries.append(entry)

    session.add_all(db_entries)
    session.commit()
