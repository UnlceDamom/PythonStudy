class employee:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def print_info(self):
        print(f'姓名：{self.name} , 工号{self.id}')


class FullTimeEmployee(employee):
    def __init__(self, name, id, monthly_salary):
        super().__init__(name, id)
        self.monthly_salary = monthly_salary

    def calculate_monthly_salary(self):
        return self.monthly_salary


class PartTimeEmployee(employee):
    def __init__(self, name, id, daily_salary, work_days):
        super().__init__(name, id)
        self.daily_salary = daily_salary
        self.work_days = work_days

    def calculate_monthly_salary(self):
        return self.daily_salary * self.work_days


ming = FullTimeEmployee('小明', '9527', 100000)
ming.print_info()
print(ming.calculate_monthly_salary())

hong = PartTimeEmployee('小红', '10086', 300, 26)
hong.print_info()
print(hong.calculate_monthly_salary())
