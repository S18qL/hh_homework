import requests
import pprint
import json
from abc import ABC, abstractmethod




class VacancyAPI(ABC):
    @abstractmethod
    def search(self, *args, **kwargs):
        pass


class VacancyToFile(ABC):
    @abstractmethod
    def search(self, *args, **kwargs):
        pass

    @abstractmethod
    def save_to_file(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_from_file(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete_info(self, *args, **kwargs):
        pass

class SaverJSON(VacancyToFile):
    @staticmethod
    def save_to_file(d, filename):
        """save json to file"""
        try:
            with open(filename, 'a') as outfile:
                json.dump(d, outfile, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            return e

    def get_from_file(self, filename):
        """:return json from file"""
        try:
            a = json.load(filename)
            return a
        except Exception as e:
            return e



class HeadHunterAPI(VacancyAPI):
    def __init__(self):
        self.url = "https://api.hh.ru/vacancies"
        self.vacancies_list = "Вызовите метод search для получения списка вакансий"
        self.p = 'Python'


    def __getitem__(self, key):
        if type(self.vacancies_list) != str:
            return json.dumps(self.vacancies_list[key], indent=4, ensure_ascii=False)
        else:
            return self.vacancies_list

    def __str__(self):
        if type(self.vacancies_list) != str:
            return json.dumps(self.vacancies_list, indent=4, ensure_ascii=False)
        else:
            return self.vacancies_list

    def total_vacancy(self):
        """:return amount of found vacancions"""
        params = {'text': f'{self.p}', 'page': 1, 'area': 1}
        result_total_vacancies = requests.get(self.url, params=params).json()
        total_vacancies = dict(keyword=self.p, count=result_total_vacancies['found'])
        return total_vacancies

    def search(self, skills_s, n_vacancies=None, experience=None):
        """main function for searching vacancy on hh.ru"""
        skills_lst = [i.strip().replace(",","") for i in skills_s.split()]
        params = {}
        if experience:
            if experience < 1:
                experience = "noExperience"
            elif 1<experience<3:
                experience="between1And3"
            elif 3<experience<6:
                experience="between3And6"
            elif experience>6:
                experience="moreThan6"
            params["experience"] = experience

        params = {'text': f"NAME:({self.p}) AND DESCRIPTION:({' '.join(skills_lst)})"}

        result_vacancies = requests.get(self.url, params=params).json()["items"]
        if n_vacancies:
            result_vacancies = result_vacancies[:int(n_vacancies)]
        self.vacancies_list = result_vacancies
        return result_vacancies

    def parse_info(self, hh_vac_info_dict):
        """get main vacation info """
        name = hh_vac_info_dict["name"]
        link = hh_vac_info_dict["alternate_url"]
        requirement = hh_vac_info_dict["snippet"]["requirement"]
        description = hh_vac_info_dict["snippet"]["responsibility"]
        salary = hh_vac_info_dict.get("salary")
        if salary:
            salary = salary.get("from")
        return name,link,requirement,description,salary

    def get_parsed_vacancies(self, skills_s, n_vacancies=None, experience=None):
        return [self.parse_info(i) for i in self.search(skills_s, n_vacancies=n_vacancies, experience=experience)]


class Vacancy:
    def __init__(self, name, link, requirement, description, salary):
        self.name = name
        self.link = link
        self.requirement = requirement
        self.salary = salary
        self.description = description

    def to_dict(self):
        """:return vacancy as dict"""
        return {"Title": self.name, "Link": self.link,"Salary": self.salary, "Description": self.description, "Requirements": self.requirement}

    def __str__(self):
        return f"Title: {self.name}\nLink: {self.link}\nSalary: {self.salary}\nDescription: {self.description}" \
               f"\nRequirements: {self.requirement}\n"

    def __eq__(self, other):
        return self.salary == other.salary

    def __lt__(self, other):
        return self.salary < other.salary

    def __gt__(self, other):
        return self.salary > other.salary




def user_interaction():
    platforms = ["HeadHunter", "SuperJob"]
    search_query = input("Введите поисковый запрос: ")
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))

    filter_words = input("Введите ключевые слова для фильтрации вакансий: ")
    exp =  int(input("Введите ваш опыт работы для фильтрации вакансий: "))

    # a = SuperJobAPI()
    b = HeadHunterAPI()
    for i in b.get_parsed_vacancies(search_query + filter_words, n_vacancies=top_n, experience=exp):
        new_v = Vacancy(*i)
        print(new_v)
        SaverJSON.save_to_file(new_v.to_dict(), "new_file.json")
    # for i in a.get_parsed_vacancies(search_query + filter_words, n_vacancies=top_n, experience=exp):
    #     new_v = Vacancy(*i)
    #     print(new_v)
    #     SaverJSON.save_to_file(new_v.to_dict(), "new_file.json")


if __name__ == "__main__":
    user_interaction()


