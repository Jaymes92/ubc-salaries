class Employee:
    def __init__(self):
        self.full_name_2019 = None
        self.full_name_2020 = None
        self.full_name_2021 = None
        self.full_name_2022 = None
        self.search_name = None
        self.salary_2019 = None
        self.salary_2020 = None
        self.salary_2021 = None
        self.salary_2022 = None
        self.expenses_2019 = None
        self.expenses_2020 = None
        self.expenses_2021 = None
        self.expenses_2022 = None

    def __repr__(self) -> str:
        result = ""
        for key, value in self.__dict__.items():
            if value is not None:
                result += f"{key}: {value}\n"
        return result