class Student:
    def __init__(self,name, id):
        self.name = name
        self.id = id

    def set_score(self, Chinese , Math , English):
        self.Chines= Chinese
        self.Math = Math
        self.English = English

    def print_score(self):
        print(f"{self.name} , {self.id}成绩如下：\n语文：{self.Chines} ,数学：{self.Math} ,英语：{self.English}")


student = Student("小明",9527)
student.set_score(110,120,115)
student.print_score()