from datetime import date, timedelta, datetime
from random import shuffle
import csv
from cs50 import SQL
from calendar import monthrange
from ics import Calendar, Event

import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///scheduler.db")

"""This file contains the driver code for the schedule sorting algorithm that's used by the app"""

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def check_date_not_in_past(date):
    """Checks the given date vs today's date, return True if not in the past"""

    if date < date.today():
        return False

    return True


def convert_future_date(future_date):
    """specific function to check the future date to make sure it's not the same as today,
        because why do you need the whole program to sort you out shifts for the same date!"""

    while type(future_date) != date:

        try:
            year, month, day = future_date.split("-")
        except ValueError:
            return "invalid input"

        future_date = date(int(year), int(month), int(day))

    if check_date_not_in_past(future_date) == False:
        return "date in past"

    if future_date == date.today():
        return "future is same as today"

    return future_date


def convert_start_date(start_date):
    """Ensures start_date is in datetime.date format"""

    # Check to ensure date has been converted correctly if not today and keep prompting if not
    while type(start_date) != date:

        # If user has selected today, convert today's date
        if start_date.lower() == "today" or start_date.lower() == "now":
            start_date = date.today()
            return start_date

        # If not today, try to convert to correct format
        try:
            year, month, day = start_date.split("-")

        except ValueError:
            return "invalid input"

        # If date passes the above but not within reasonable future dates, ask again.
        # Limit year could be set as a constant elsewhere for longevity but I doubt this will be used in 200 years time
        if int(year) > 2400:
            return "too far in advance"

        # This block to catch tracebacks raised by dateime module
        try:
            start_date = date(int(year), int(month), int(day))

        except ValueError:
            return "invalid input"


    # if date is in the past, ask user to try again
    if check_date_not_in_past(start_date) == False:
        return "date in past"

    else:
        return start_date


def get_day_template(filename):
    """Function to open a csv containing headers for a blank day in the desired shift pattern"""

    blank_day = {}

    # open the desired file and get the fields into a dict
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            for item in row:
                blank_day[item] = ""

    return blank_day


def get_period_to_schedule(start_date, end_date):
    """This function will take the validated start and end dates and return how many weeks/ optionally days
        to be returning a schedule for"""

    total_work_weeks = 0
    days_to_schedule = 0
    counter_date = start_date

    # check to make sure user hasn't inadvertently started scheduling for the weekend
    if start_date.weekday() == 5:
        counter_date += timedelta(days=2)

    elif start_date.weekday() == 6:
        counter_date += timedelta(days=1)

    while counter_date <= end_date:

        # if start date is a weekend, handle this so we start counting period to schedule from the next monday. Add the filled up week to the total work weeks
        if counter_date.weekday() == 5:
            counter_date += timedelta(days=2)
            total_work_weeks += 1
            continue

        # Run day through check to see if it's a public holiday
        if _is_public_holiday(start_date):
            counter_date += timedelta(days=1)
            continue

        # add the working day to the counter
        days_to_schedule += 1
        counter_date += timedelta(days=1)

        if counter_date > end_date:
            total_work_weeks += 1
            break


    return days_to_schedule, total_work_weeks


def get_roster():
    """Function gets the latest roster, served in a file called roster.csv
        depreciated in Flask app version"""

    roster = []
    with open("roster.csv") as roster_master:
        reader = csv.DictReader(roster_master)
        for row in reader:
            roster.append(row)

    # convert part time people's non working days into a list of keys for comparison later
    for staff in roster:
        if staff["contract"].lower() == "p":
            days = staff["non-working days"].split(" ")
            staff["non-working days"] = []
            for day in days:
                if "am" in day:
                    day = day.split("am")
                    day[0] = "am"
                    day[1] = int(day[1])
                if "pm" in day:
                    day = day.split("pm")
                    day[0] = "pm"
                    day[1] = int(day[1])
                else:
                    day = int(day)
                staff["non-working days"].append(day)

    return roster


def put_dates_in_blank_schedule(blank_day, days_needed, start_date):
    """This function takes the amount of days the user would like to schedule and sets up lists of day dictionaries ready for staff"""

    # make a blank list to put lists of days in to represent the schedule, then make a blank week to keep track of weeks
    schedule = []
    week = []

    # while days are left to schedule
    for i in range(days_needed):

        start_day = start_date.weekday()

        # if start date is a weekend, handle this so we start counting period to schedule from the next monday. Add the filled up week to the schedule, then reset.
        if start_day == 5:
            start_date += timedelta(days=2)
            if week:
                schedule.append(week)
                week = []

        elif start_day == 6:
            start_date += timedelta(days=1)
            if week:
                schedule.append(week)
                week = []

        # Run day through check to see if it's a public holiday
        if _is_public_holiday(start_date):
            start_date += timedelta(days=1)
            continue

        else:
            # put the day in the schedule, roll date to be the next day ready to run through loop again
            day = blank_day.copy()
            day["date"] = start_date
            week.append(day)
            start_date += timedelta(days=1)
            days_needed -= 1

    # Append the last week to the schedule, because this won't be caught in my loop if I've run out of the counter
    schedule.append(week)

    return schedule

def nicer_date(date):
    """uses datetime if it's an ISO datetime, but if it's a string, my own working out, for ease of putting into Jinja"""

    if type(date) == str:
        year, month, day = date.split("-")
        converted = (f"{day}/{month}/{year}")
        return converted
    else:
        return date.strftime("%d/%m/%Y")


def _is_public_holiday(date):
    """Checks to see if date given is a public holiday or not, returns true if it is"""

    search = db.execute("SELECT * FROM public_holidays WHERE date = (?)", date)
    if search:
        return True

    return False


def count_weighting(schedule):
    """Function takes a completed roster and produces the amount of shifts each staff member has done"""

    totals = []
    blank_person = {}

    rows = db.execute("SELECT name FROM staff")

    for name in rows:
        person = blank_person.copy()
        person["name"] = name["name"]
        person["shifts"] = 0
        for week in schedule:
            for day in week:
                for item in day.items():
                    if item[0] != "date":
                        name = item[1]
                        if name == person["name"]:
                            person["shifts"] += 1

        totals.append(person)

    return totals


def schedule(schedule, roster):
    """puts staff into the schedule, given the current roster of staff, and returns the amended schedule"""

    # check how many staff we have. If not enough people, just shuffling by week isn't enough and it creates a pattern of similar days if there are only 5 people.
    if len(roster) < 5:
        for week in schedule:
            counter = len(roster) - 1
            shuffle(roster)
            # access each day in the week
            for day in week:

                # shuffle the roster each day to create variety for smaller rosters of staff
                shuffle(roster)

                # for each key in the day dict, run checks to see if current staff memeber can work
                for key in day:
                    while day[key] == "":

                        # discount staff who can't do a type of shift
                        while not _staff_can_do_shift(roster[counter], key, day):
                            counter -= 1

                            if counter < 0:
                                counter = len(roster) - 1

                        name = roster[counter]["name"]
                        day[key] = name
                        counter -= 1

                        if counter < 0:
                            counter = len(roster) - 1

    else:
        # first shuffle the staff to output different weeks for each week in the time period
        for week in schedule:
            shuffle(roster)
            roster_copy = roster
            counter = len(roster) - 1

            # access each day in the week
            for day in week:

                # for each key in the day dict, run checks to see if current staff member can work
                # first check to see how many people can work on that day, if there's not many then shuffle to avoid repetition across multiple days
                rows = db.execute("SELECT * FROM unavailable WHERE date = (?)", day["date"].strftime("%Y-%m-%d"))
                if len(rows) <= 4:
                    shuffle(roster)

                for key in day:
                    while day[key] == "":

                        # discount staff who can't do a type of shift
                        while not _staff_can_do_shift(roster_copy[counter], key, day):

                            # put person who can't do that shift next in line to do the next one, for fairness
                            removed = roster_copy.pop(counter)
                            roster_copy.insert((counter + 1), removed)
                            counter -= 1

                            if counter < 0:
                                counter = len(roster_copy) - 1

                        name = roster_copy[counter]["name"]
                        day[key] = name
                        counter -= 1

                        if counter < 0:
                            counter = len(roster_copy) - 1

            roster_copy = []

    return schedule


def _staff_can_do_shift(staff, shift, day):
    """runs validation to see if staff can do the shift"""

    # check if staff is part time to run checks to see if they can work that day
    if staff["contract"].lower() == "p" and _schedule_part_time_check(day, staff, shift):
        return False

    # if staff working that day, but can't do the type of shift, return false
    if _cant_do_type_of_shift(staff, shift):
        return False

    #if staff unavailable for any reason, return false
    if _staff_unavailable(staff, day, shift):
        return False

    return True


def _cant_do_type_of_shift(staff, shift):
    """Checks to make sure the selected staff member can do the type of shift"""

    num = ""
    for letter in shift:
        if letter.isnumeric():
            num = letter

    if num == "1":
        if staff["cando1"] == "n":
            return True
    if num == "2":
        if staff["cando2"] == "n":
            return True

    return False


def _schedule_part_time_check(day, staff, shift):
    """Checks to see if the suggested shift falls on a staffmember's non-working day"""

    #get position of current day in week and check vs weekday selected with the part time non-working days
    days = staff["nonworking_days"].split(" ")

    for item in range(len(days)):
        if "am" in days[item]:
            days[item] = days[item].split("am")
            days[item][0] = "am"

        elif "pm" in days[item]:
            days[item] = days[item].split("pm")
            days[item][0] = "pm"

        else:
            days[item] = int(days[item])

    for item in days:
        if type(item) != int:
            if day["date"].weekday() == int(item[1]):
                if item[0] in shift.lower():
                    return True

    if day["date"].weekday() in days:
        return True

    return False

def _staff_unavailable(staff, day, shift):
    """Checks the staff's unavailability by querying the unavailable DB and checks the day being looked at,
    returns true if staff unavailable on the date passed in"""

    rows = db.execute("SELECT * FROM unavailable WHERE staff_id = (SELECT id FROM staff WHERE name == (?))", staff["name"])
    for row in rows:
        if day["date"].strftime("%Y-%m-%d") == row["date"]:
            if shift == "AM_1" or shift == "AM'_2" and row["partdayAM"] == "y":
                return True
            elif shift == "PM_1" or shift == "PM'_2" and row["partdayPM"] == "y":
                return True
            elif row["partdayAM"] and row["partdayPM"] == "y":
                return True
    return False

def nicer_part_time(string):

    if string == "pm2 3 4":
        return "Wed PM, Thu, Fri"
    elif string == "0 1 am2":
        return "Mon, Tues, Wed AM"


def get_month(date):
    """Function takes in a date in datetime, ready to fill a blank list for the days of the week
        of the month for the view view"""

    month_list = []
    week = []
    blank_day = {}
    today_date = date
    today = datetime.today()
    today = today.date()

    day_num = int(today_date.strftime("%d"))
    year_num = int(today_date.strftime("%y"))
    month_num = int(today_date.strftime("%m"))

    today_date -= timedelta(days=(day_num -1))
    start_date = today_date

    while start_date.weekday() != 6:
        start_date -= timedelta(days=1)

    count = 0

    # Handle december differently or we get stuck in a neverending loop
    if month_num == 12:
        while int(start_date.strftime("%m")) != 1:
            day = blank_day.copy()
            day["date"] = start_date.date()
            day["day"] = int(start_date.strftime("%d"))
            day["weekday"] = start_date.weekday()

            shifts = db.execute("SELECT AM_1, AM_2, PM_1, PM_2 from schedule WHERE date = (?)", start_date.strftime("%Y-%m-%d"))
            if shifts:
                day["shifts"] = "y"
                day["shift_data"] = shifts
            if start_date.strftime("%m") == today_date.strftime("%m"):
                day["month_id"] = "month_main"
            else:
                day["month_id"] = "month_sec"

            week.append(day)
            count += 1

            if count == 7:
                month_list.append(week)
                week = []
                count = 0

            start_date += timedelta(days=1)
    else:
        while int(start_date.strftime("%m")) < (month_num + 1):

            day = blank_day.copy()
            day["date"] = start_date.date()
            day["day"] = int(start_date.strftime("%d"))
            day["weekday"] = start_date.weekday()
            shifts = db.execute("SELECT AM_1, AM_2, PM_1, PM_2 from schedule WHERE date = (?)", start_date.strftime("%Y-%m-%d"))
            if shifts:
                day["shifts"] = "y"
                day["shift_data"] = shifts
            if start_date.strftime("%m") == today_date.strftime("%m"):
                day["month_id"] = "month_main"
            else:
                day["month_id"] = "month_sec"

            week.append(day)
            count += 1

            if count == 7:
                month_list.append(week)
                week = []
                count = 0

            start_date += timedelta(days=1)

    if start_date.weekday() != 6:
        week = []
        # work out how many days to put in the last week of the calendar for view
        while start_date.weekday() != 6:
            start_date -= timedelta(days=1)

        for i in range(7):
            day = blank_day.copy()
            day["date"] = start_date.date()
            day["day"] = int(start_date.strftime("%d"))
            day["weekday"] = start_date.weekday()
            shifts = db.execute("SELECT AM_1, AM_2, PM_1, PM_2 from schedule WHERE date = (?)", start_date.strftime("%Y-%m-%d"))
            if shifts:
                day["shifts"] = "y"
                day["shift_data"] = shifts

            if start_date.strftime("%m") == today_date.strftime("%m"):
                day["month_id"] = "month_main"
            else:
                day["month_id"] = "month_sec"
            week.append(day)

            start_date += timedelta(days=1)
        month_list.append(week)

    for week in month_list:
        for day in week:
            if today == day["date"]:
                day["today"] = True

    return month_list


def get_week(date):
    """Function to get a week view from a given date for the week view page"""

    week_list = []
    blank_day = {}

    today = datetime.today()
    today = today.date()

    for i in range(5):
        day = blank_day.copy()
        day["date"] = date.date()
        day["day"] = int(date.strftime("%d"))
        day["weekday"] = date.weekday()
        shifts = db.execute("SELECT AM_1, AM_2, PM_1, PM_2 from schedule WHERE date = (?)", date.strftime("%Y-%m-%d"))
        if shifts:
            day["shifts"] = "y"
            day["shift_data"] = shifts

        week_list.append(day)
        date += timedelta(days=1)

    for day in week_list:
        if today == day["date"]:
            day["today"] = True

    return week_list


def export_meeting(date):
    """Function to convert given db entries into exportable meetings"""

    c = Calendar()
    e = Event()
    e.name = "My cool event"
    e.begin = '2014-01-01 08:30:00'
    e.end = '2014-01-01 12:30:00'
    c.events.add(e)
    c.events
    with open('my.ics', 'w') as my_file:
        my_file.writelines(c.serialize_iter())