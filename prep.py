#imports
import sqlite3
import datetime


#variables

#DATES

today = datetime.date.today()
day_now = today.strftime("%d")

#never have a day start with 0 ex: 11/05 -> 11/5
if day_now[0] == "0":
    day_now = day_now[1]
mon_now = today.strftime("%m")
today_str = mon_now + "/" + day_now

month_days = {
    "January": 31,
    "February": 28,  
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31
}

mon_days = {}

for i, mon in enumerate(month_days):
    mon_days[i+1] = month_days[mon]

year_dates_list = []
dates_to_day = {}

count = 2
for mon in mon_days:
    for day in range(mon_days[mon]):
        date = str(mon) + "/" + str(day+1)
        year_dates_list.append(date)
        dates_to_day[date] = count % 7
        count += 1

def list_from_date(date):
    ind = year_dates_list.index(date)
    new_list = year_dates_list[ind:]
    return new_list




            
def main():
    pass
    #create_cal_week_from_date(today_str)

#main()