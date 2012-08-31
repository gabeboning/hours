import sys
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import datetime
import decimal
from bs4 import BeautifulSoup
import argparse

class Basecamp:
  def __init__(self):
    # get the config from git
    self.bcUser = subprocess.check_output("git config basecamp.user-id", shell=True).strip()
    self.bcKey = subprocess.check_output("git config basecamp.key", shell=True).strip()
    self.bcUrl = subprocess.check_output("git config basecamp.url", shell=True).strip()
    self.auth = HTTPBasicAuth(self.bcKey, '')
    self.projects = {}


  # returns beautifulsoup object of the time report
  def getReport(self, fromDate, toDate):
    r = requests.get(self.bcUrl + "/time_entries/report.xml?subject_id=" + self.bcUser + "&from=" + fromDate + "&to=" + toDate, auth=self.auth)
    return BeautifulSoup(r.text)



  def getProjectInfo(self, project_id):
    if project_id in self.projects:
      return self.projects[project_id]
    
    r = requests.get(self.bcUrl + "/projects/" + project_id + ".xml", auth=self.auth)
    xml = BeautifulSoup(r.text)
    p = {"name":xml.find("name").string, "client":xml.find("company").find("name").string}

    self.projects[project_id] = p
    return p
  
  def hoursRange(self, start, end):
    start = start.strftime("%Y%m%d")
    end = end.strftime("%Y%m%d")

    entries = self.getReport(start, end)
    projects = {}
    total = 0

    for entry in entries.findAll('time-entry'):
      time = float(entry.find('hours').string)
      total += time

      pid = entry.find('project-id').string

      if pid in projects:
        projects[pid] += time
      else:
        projects[pid] = time

    return projects

  def hoursByDay(self, date):
    return self.hoursRange(date, date)  

  def hoursToday(self):
    now = datetime.datetime.now()
   
    return self.hoursByDay(now)


  def hoursWeek(self):
    now = datetime.datetime.now()
    monday = now - datetime.timedelta(now.weekday())

    return self.hoursRange(monday, now)


