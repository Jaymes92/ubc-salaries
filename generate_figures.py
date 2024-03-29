import fitz
import re
import os
from employees import Employee
import matplotlib.pyplot as plt


os.makedirs("figures", exist_ok=True)

PATH_2019 = "data/2019_report.pdf"
PATH_2020 = "data/2020_report.pdf"
PATH_2021 = "data/2021_report.pdf"
PATH_2022 = "data/2022_report.pdf"


# Accept employee data in form of the regex match. Pass in the path to add correct year's data - hires in a later year
# will not be in a prior year's batch of data.
def add_employee(data, name):
    full_name = f"{data[2]} {data[0]}"
    search_name = trim_name(data)
    new_employee = Employee()
    if name == PATH_2019:
        new_employee.full_name_2019 = full_name
        new_employee.salary_2019 = data[4]
        new_employee.expenses_2019 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)
    if name == PATH_2020:
        new_employee.full_name_2020 = full_name
        new_employee.salary_2020 = data[4]
        new_employee.expenses_2020 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)
    if name == PATH_2021:
        new_employee.full_name_2021 = full_name
        new_employee.salary_2021 = data[4]
        new_employee.expenses_2021 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)
    if name == PATH_2022:
        new_employee.full_name_2022 = full_name
        new_employee.salary_2022 = data[4]
        new_employee.expenses_2022 = data[5]
        new_employee.search_name = search_name
        employee_list.append(new_employee)


# Only look at first name in both first and last names (as it isn't consistent year to year). Return LAST, FIRST for easy search name comparisons.
def trim_name(data):
    first_name = data[2].split(" ")[0]
    first_name = first_name.replace(".", "").replace("(", "").replace(")", "")
    last_name = data[0].split(" ")[0]
    last_name = last_name.replace(".", "").replace("(", "").replace(")", "")
    stripped_name = f"{last_name}, {first_name}"
    return stripped_name


# Extract and clean text from all three reports. Each dictionary entry contains a data list for a given report/year.
# Each entry in a list for a given report/year represents the cleaned text from one data page.
report_text = {}
for report_name in [PATH_2019, PATH_2020, PATH_2021, PATH_2022]:
    with fitz.open(report_name) as file:
        report_text[report_name] = []
        for page in file:
            text = page.get_text()
            text = text.replace("\n", "")
            text = text.replace("$", "")
            text = text.replace("Name", "")
            # Replace sequences of multiple whitespaces with one whitespace.
            text = re.sub(r"\s+", " ", text)
            # This phrase shows up on pages that contain data and is easy to split around.
            text = text.split("Remuneration Expenses*")
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
    elif report_name == PATH_2022:
        # Add data to existing employee if search name found. Otherwise, add as a new employee.
        for entry in report_data:
            search_name = trim_name(entry)
            match_found = False
            for employee in employee_list:
                if employee.search_name == search_name:
                    employee.full_name_2022 = f"{entry[2]} {entry[0]}"
                    employee.salary_2022 = entry[4]
                    employee.expenses_2022 = entry[5]
                    match_found = True
                    break
            if not match_found:
                add_employee(entry, report_name)           
    else:
        print("God help you if you made it here.")


# Create one plot. Clear and re-plot and save with different title. Generating and closing many figures will crash PC.
fig, ax = plt.subplots()
for employee in employee_list:
    salary = []
    for sal in [employee.salary_2019, employee.salary_2020, employee.salary_2021, employee.salary_2022]:
        if sal:
            sal = sal.replace(",", "")
            salary.append(int(sal))
        else:
            salary.append(0)
    ax.bar(["2019", "2020", "2021", "2022"], salary)
    ax.set_title(employee.search_name)
    plt.xlabel("Year")
    plt.ylabel("Salary ($)")
    plt.savefig(f"./figures/{employee.search_name}")
    ax.clear()