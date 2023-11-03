from flask import request
from typing import Tuple
from uk_covid19 import Cov19API
import sched
import time
from time_conver import hhmm_to_seconds, current_time_hhmm

global update

covid_data = sched.scheduler(time.time, time.sleep)


def parse_csv_data(csv_filename):
   print(csv_filename) 
   file = open(csv_filename, "r").readlines()
   lines = []
   for line in file:
      lines.append(line.strip())
   return lines

    
def test_parse_csv_data ():
   data = parse_csv_data ('nation_2021-10-28.csv')
   assert len (data) == 639


def process_covid_csv_data(covid_csv_data):
   last7days_cases = 0
   total_deaths = 0
   current_hospital_cases = int(covid_csv_data[1].split(",")[5])
   total_deaths = int(covid_csv_data[14].split(",")[4])
   for i in range(3,10):
      covid_csv_data[i].split(",")[6] 
      last7days_cases += int(covid_csv_data[i].split(",")[6])
   return last7days_cases, current_hospital_cases, total_deaths


def test_process_covid_csv_data ():
  last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data (parse_csv_data ('nation_2021-10-28.csv'))
  assert last7days_cases == 240299
  assert current_hospital_cases == 7019
  assert total_deaths == 141544

def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> str:
    filters = [
        'areaType=' + location_type,
        'areaName=' + location
    ]

    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate",
        "hospitalCases": "hospitalCases",
    }

    api = Cov19API(filters=filters, structure=cases_and_deaths)

    data = api.get_json()["data"]
    return data


def add_covid_data():
    exeter_data = covid_API_request()
    local_area = exeter_data[0]["areaName"]
    local_new_case = 0
    for x in range(7):
        local_new_case += exeter_data[x]["newCasesByPublishDate"]
    uk_data = covid_API_request("England", "nation")
    nation_area = uk_data[0]["areaName"]
    nation_new_case = 0
    nation_hospital_cases = uk_data[0]["hospitalCases"]
    for x in range(7):
        nation_new_case += uk_data[x]["newCasesByPublishDate"]
    total_death = uk_data[1]["cumDeaths28DaysByDeathDate"]
    return local_area, local_new_case, nation_area, nation_new_case, nation_hospital_cases, total_death


def schedule_covid_updates(update_interval, update_name):
    repeat_field = request.args.get("repeat")
    covid_data.enter(update_interval, 1, add_covid_data)
    if repeat_field == "repeat":
        covid_data.enter(update_interval, 2, lambda: schedule_covid_updates(24 * 60 * 60, update_name))
    covid_data.run(blocking=False)


def add_update(update_name, update_interval):
    global update
    update = []
    update.append({
        "title": update_name,
        "content": update_interval
    })


def remove_update(update_name):
    global update
    for n in update:
        if n["title"] == update_name:
            update.remove(n)



