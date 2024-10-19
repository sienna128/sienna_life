#imports
import sqlite3
import datetime


#variables

#DATES

today = datetime.date.today()
day_now = today.strftime("%d")
mon_now = today.strftime("%m")

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

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_cal():
    conn = get_db_connection()

    for mon in mon_days:
        for i in range(mon_days[mon]):
            str_dat = str(mon) + "/" + str(i+1)
            conn.execute("INSERT INTO dates (mon, da, str_dat) VALUES (?, ?, ?)", 
                        (str(mon), str(i+1), str_dat)
                        )
            
    conn.commit()
    conn.close()

def create_cal_from_nov():
    conn = get_db_connection()

    for mon in mon_days:
        if mon >= 11:
            for i in range(mon_days[mon]):
                str_dat = str(mon) + "/" + str(i+1)
                conn.execute("INSERT INTO dates (mon, da, str_dat) VALUES (?, ?, ?)", 
                            (str(mon), str(i+1), str_dat)
                            )
            
    conn.commit()
    conn.close()

def create_cal_from_today():
    conn = get_db_connection()

    for mon in mon_days:
        if mon >= int(mon_now):
            for i in range(mon_days[mon]):
                if i+2 > int(day_now):
                    str_dat = str(mon) + "/" + str(i+1)
                    conn.execute("INSERT INTO dates (mon, da, str_dat) VALUES (?, ?, ?)", 
                                (str(mon), str(i+1), str_dat)
                                )
            
    conn.commit()
    conn.close()

def create_cal_from_today_days(days):
    #only works if the days are in one or two months, but not for three or more months
    conn = get_db_connection()

    today = datetime.date.today()
    day_now = today.strftime("%d")
    mon_now = today.strftime("%m")
    day_now = int(day_now)
    mon_now = int(mon_now)
    mon_now_days = mon_days[mon_now]
    
    days_left = mon_now_days - day_now
    if days < days_left:
        for i in range(days):
            str_dat = str(mon_now) + "/" + str(day_now + i)
            conn.execute("INSERT INTO dates (mon, da, str_dat) VALUES (?, ?, ?)", 
                         (str(mon_now), str(day_now + i), str_dat))
    else:
        for i in range(days_left):
            str_dat = str(mon_now) + "/" + str(day_now + i)
            conn.execute("INSERT INTO dates (mon, da, str_dat) VALUES (?, ?, ?)", 
                         (str(mon_now), str(day_now + i), str_dat))
        for i in range(days - days_left):
            str_dat = str(mon_now + 1) + "/" + str(i + 1)
            conn.execute("INSERT INTO dates (mon, da, str_dat) VALUES (?, ?, ?)",
                         str(mon_now + 1), str(i + 1), str_dat)
    conn.commit()
    conn.close()




            
def main():
    create_cal_from_today_days(7)

main()