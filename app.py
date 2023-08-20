import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime, timedelta
import schedulerhelpers
from schedulerhelpers import login_required, nicer_date, nicer_part_time
import json


# Configure application
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'

# Make sure API key is set for password reset emails
#if not os.environ.get("SENDGRID_API_KEY"):
    #raise RuntimeError("SENDGRID_API_KEY not set")
#app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')

app.config['MAIL_DEFAULT_SENDER'] 
mail = Mail(app)

app.jinja_env.filters["date"] = nicer_date
app.jinja_env.filters["enumerate"] = enumerate
app.jinja_env.filters["nicerptdisplay"] = nicer_part_time


# create a blank variable to store temp schedules in, until I find a better solution
temp = []
start = ""
end = ""

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///scheduler.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@app.route("/index")
@login_required
def index():
    """A landing page for users when they log in"""

    # Get username to display as a nice greeting message
    rows = db.execute("SELECT * FROM users WHERE id = (?)", session["user_id"])
    username = rows[0]["username"]

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    suffix = ""
    today = date.today()
    if today.strftime("%d") == "01":
        suffix = "st"
    elif today.strftime("%d") in ["2", "22"]:
        suffix = "nd"
    elif today.strftime("%d") == "03":
        suffix = "rd"
    else:
        suffix = "th"

    day = today.strftime("%d")
    day = day.strip("0")
    today = today.strftime(f"%A, {day}{suffix} %B %Y")

    return render_template("index.html", today=today, username=username, is_admin=is_admin)

@login_required
@app.route("/view")
@app.route("/view/<month_num>")
def view(month_num):
    """A nice overview of the current diary"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    if request.method == "GET" and month_num == "#":

        today = datetime.today()

        # get the month data of the blank month from today, return as list of days
        month = schedulerhelpers.get_month(today)
        month_num = int(today.strftime("%m"))
        year = int(today.strftime("%Y"))
        # for weeks in month, row
        month_header = today.strftime("%B %Y")

        return render_template("view.html", today=today, month=month, month_num = month_num, month_header=month_header, is_admin=is_admin)

    elif request.method == "GET":

        if "prev" in month_num:
            data = month_num.strip("prev")
            monthname, year = data.split(" ")
            mnum = datetime.strptime(monthname, '%B').month
            year = int(year)
            if mnum == 1:
                year -= 1
                mnum = 12
            else:
                mnum -= 1
            today = date(year, (mnum), 1)

        if "next" in month_num:
            data = month_num.strip("next")
            monthname, year = data.split(" ")
            mnum = datetime.strptime(monthname, '%B').month
            year = int(year)
            if mnum == 12:
                year += 1
                mnum = 1
            else:
                mnum += 1
            today = date(year, (mnum), 1)

        dt = datetime.combine(today, datetime.min.time())

        # get the month data of the blank month from the first day of the requested month, return as list of days
        month = schedulerhelpers.get_month(dt)

        # for weeks in month, row
        month_header = today.strftime("%B %Y")

        return render_template("view.html", today=today, month=month, month_header=month_header, is_admin=is_admin)


@login_required
@app.route("/view_week")
@app.route("/view_week/<week_num>")
def view_week(week_num):
    """Week view of the schedule"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    if request.method == "GET" and week_num == "#":
        week_num = datetime.today()
        week_commencing = week_num

        if week_commencing.weekday() != 0:
            while week_commencing.weekday() != 0:
                week_commencing -= timedelta(days=1)

        week = schedulerhelpers.get_week(week_commencing)
        week_date = week_commencing.strftime("%d%m%Y")
        week_commencing = week_commencing.strftime("%d/%m/%Y")

        return render_template("view_week.html", week_header=week_commencing, week_date=week_date, week=week, is_admin=is_admin)

    elif request.method == "GET":
        if "prev" in week_num:
            data = week_num.strip("prev")
            last_week = datetime.strptime(data, '%d%m%Y')
            current_week = last_week
            current_week -= timedelta(days=7)
            week = schedulerhelpers.get_week(current_week)
            week_date = current_week.strftime("%d%m%Y")
            week_commencing = current_week.strftime("%d/%m/%Y")

            return render_template("view_week.html", week_header=week_commencing, week_date=week_date, week=week, is_admin=is_admin)

        if "next" in week_num:
            data = week_num.strip("next")
            last_week = datetime.strptime(data, '%d%m%Y')
            current_week = last_week
            current_week += timedelta(days=7)
            week = schedulerhelpers.get_week(current_week)
            week_date = current_week.strftime("%d%m%Y")
            week_commencing = current_week.strftime("%d/%m/%Y")

            return render_template("view_week.html", week_header=week_commencing, week_date=week_date, week=week, is_admin=is_admin)


@login_required
@app.route("/roster", methods=["GET", "POST"])
def roster():
    """Page to allow someone to view the current roster and their stats, and add/delete staff"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    if request.method == "POST":
        #print(request.form)

        # Ensuring staff name and contract type is filled in before adding new staff to DB
        if request.form.get("staff_name") == "" and not request.form.get("contract"):
            flash("Please enter staff name and contract type", category="danger")
            return render_template("roster.html", staff=staff, is_admin=is_admin)
        elif request.form.get("staff_name") == "":
            flash("Please enter staff name", category="warning")
            return render_template("roster.html", staff=staff, is_admin=is_admin)
        elif not request.form.get("contract"):
            flash("Please enter staff contract type", category="warning")
            return render_template("roster.html", staff=staff, is_admin=is_admin)

        # If minimum field requirements met, add staff member to DB
        nonworking = ""
        contract = request.form.get("contract")
        if contract == "P_1":
            contract = "P"
            nonworking = "pm2 3 4"
        elif contract == "P_2":
            contract = "P"
            nonworking = "0 1 am2"

        cando1 = request.form.get("cando1")
        if not cando1:
            cando1 = "n"
        elif cando1 == "1":
            cando1 = "y"

        cando2 = request.form.get("cando2")
        if not cando2:
            cando2 = "n"
        elif cando2 == "2":
            cando2 = "y"

        if nonworking == "":
            rows = db.execute("INSERT INTO staff (name, contract, cando1, cando2) VALUES (?, ?, ?, ?)",
                   request.form.get("staff_name"), contract, cando1, cando2)
        else:
            rows = db.execute("INSERT INTO staff (name, contract, nonworking_days, cando1, cando2) VALUES (?, ?, ?, ?, ?)",
                    request.form.get("staff_name"), contract, nonworking, cando1, cando2)
        if not rows:
            flash("Something went wrong adding staff member to the roster, please try again", category="danger")

        flash("Added successfully!", category="success")

        # Refresh query for list of staff before displaying new list
        staff = db.execute("SELECT * FROM staff")
        return render_template("roster.html", staff=staff, is_admin=is_admin)

    if request.method == "GET":
        staff = db.execute("SELECT * FROM staff")
        return render_template("roster.html", staff=staff, is_admin=is_admin)


@login_required
@app.route("/availability", methods=["GET", "POST"])
def availability():
    """A page that allows the user to change their own availability to work/ full admin access"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    # first stage- logged in user can select from list of staff, select person and then proceed to input dates
    if request.method == "POST":

        rows = db.execute("SELECT * FROM staff")
        person = request.form.get("staff")
        person_id = db.execute("SELECT id FROM staff WHERE name = (?);", person)

        # redirects if a staff member hasn't been chosen
        if person_id == []:
            return redirect("/availability")

        current_unavailable = db.execute("SELECT * FROM unavailable WHERE staff_id = (?);",
                                        person_id[0]["id"])

        # If a person has been selected and the user wants to delete the date, query the db for the id of the entry to delete
        for item in request.form:
            if "delete" in item:

                to_delete = item.strip("delete ")
                found = db.execute("SELECT * FROM unavailable WHERE id = (?);", to_delete)

                if found:
                    db.execute("DELETE FROM unavailable WHERE id = (?);", found[0]['id'])
                    flash("Deleted successfully!", category="success")

        if request.form.get("add_date"):

            # Check that date isn't in past/ convert to date
            add_date = schedulerhelpers.convert_start_date(request.form.get("add_date"))

            # if is in past, add error
            if add_date == "date in past":
                flash("You've chosen a date in the past, please select a date from today onwards", category="warning")
                return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

            # add to db- first check if user has selected a full or part day
            time_chosen = False
            for item in request.form:
                if "flexRadioDefault" in item:
                    time_chosen = True

            # if user hasn't selected a timeperiod, tell the user they need to choose one
            if time_chosen == False:
                flash("Please select if the staff member cannot work a full or part day", category="danger")
                return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

            time = ""
            for item in request.form:
                if "flexRadioDefault" in item:
                    time_chosen = item
                    time = time_chosen.strip("flexRadioDefault")

            # check database to make sure user hasn't duplicated a time period, if they have, also error
            dates = []

            #ie, new staff member has never turned up in the unavailable db, need to make their first entry so they turn up later

            if current_unavailable == []:
                db.execute("INSERT INTO unavailable (date, staff_id, partdayAM, partdayPM) VALUES (?, ?, ?, ?)", add_date, person_id[0]["id"], "y", "y")
                flash("Added!", category="success")

                # refresh staff member's current unavailable list for display
                current_unavailable = db.execute("SELECT * FROM unavailable WHERE staff_id = (?) ORDER BY date",
                                        person_id[0]["id"])
                
                return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

            for entry in range(len(current_unavailable)):
                day = {}
                day["id"] = current_unavailable[entry]["id"]
                day["date"] = current_unavailable[entry]["date"]
                day["am"] = current_unavailable[entry]["partdayAM"]
                day["pm"] = current_unavailable[entry]["partdayPM"]
                dates.append(day)

            for day in dates:
                if request.form.get("add_date") == day["date"]:

                    if "full" in time and day["am"] == "y" and day["pm"] == "y":
                        flash("Staff member already unavailable on that date, select a different one", category="danger")
                        return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)
                    elif "part_dayA" in time and day["am"] == "y":
                        flash("Staff member already unavailable on that date, select a different one", category="danger")
                        return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)
                    elif "part_dayP" in time and day["pm"] == "y":
                        flash("Staff member already unavailable on that date, select a different one", category="danger")
                        return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

                    # if all checks passed, proceed to add into db
                    if "part_dayA" in time:
                        db.execute("UPDATE unavailable SET partdayAM = 'y' WHERE id = (?)", day["id"])
                        flash("Updated!", category="success")
                        # refresh staff member's current unavailable list for display
                        current_unavailable = db.execute("SELECT * FROM unavailable WHERE staff_id = (?) ORDER BY date",
                                                        person_id[0]["id"])
                        return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

                    elif "part_dayP" in time:
                        db.execute("UPDATE unavailable SET partdayPM = 'y' WHERE id = (?)", day["id"])
                        flash("Updated!", category="success")
                        # refresh staff member's current unavailable list for display
                        current_unavailable = db.execute("SELECT * FROM unavailable WHERE staff_id = (?) ORDER BY date",
                                                        person_id[0]["id"])
                        return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

                    elif "full" in time and (day["am"] == "y" or day["pm"] == "y"):
                        if day["am"] == "y":
                            db.execute("UPDATE unavailable SET partdayPM = 'y' WHERE id = (?)", day["id"])
                        elif day["pm"] == "y":
                            db.execute("UPDATE unavailable SET partdayAM = 'y' WHERE id = (?)", day["id"])

            if "part_dayA" in time:
                db.execute("INSERT INTO unavailable (date, staff_id, partdayAM, partdayPM) VALUES (?, ?, ?, ?)", add_date, person_id[0]["id"], "y", "n")
                flash("Added!", category="success")
            elif "part_dayP" in time:
                db.execute("INSERT INTO unavailable (date, staff_id, partdayAM, partdayPM) VALUES (?, ?, ?, ?)", add_date, person_id[0]["id"], "n", "y")
                flash("Added!", category="success")
            else:
                db.execute("INSERT INTO unavailable (date, staff_id, partdayAM, partdayPM) VALUES (?, ?, ?, ?)", add_date, person_id[0]["id"], "y", "y")
                flash("Added!", category="success")

        # refresh staff member's current unavailable list for display
        current_unavailable = db.execute("SELECT * FROM unavailable WHERE staff_id = (?) ORDER BY date",
                                        person_id[0]["id"])

        return render_template("availability.html", list=rows, person=person, current_unavailable=current_unavailable, is_admin=is_admin)

    # When landing on the page, get list of current staff to make changes to
    if request.method == "GET":
        rows = db.execute("SELECT * FROM staff")
        return render_template("availability.html", list=rows, is_admin=is_admin)


@login_required
@app.route("/settings", methods=["GET", "POST"])
def settings():
    """user's own settings page"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]



    # Get logged in user. Link user to staff database.
    rows = db.execute("SELECT * FROM users WHERE id = (?)", session["user_id"])
    staff = db.execute("SELECT * FROM staff WHERE id = (?)", rows[0]["staff_id"])

    # if user is staff- list upcoming shifts
    if staff:
        upcoming_shifts = db.execute("WITH temp AS (SELECT date, AM_1, AM_2, PM_1, PM_2 FROM schedule WHERE date > date('now') ORDER BY date ASC) SELECT * FROM TEMP WHERE (AM_1 = (?) OR AM_2 = (?) OR PM_1 = (?) OR PM_2 = (?)) LIMIT 10"
                                     , staff[0]["name"], staff[0]["name"], staff[0]["name"], staff[0]["name"])

        for shift in upcoming_shifts:
            shift_copy = shift.copy()
            for item in shift_copy:
                if item != "date" and shift_copy[item] != staff[0]["name"]:
                    shift.pop(item)

    if request.method == "POST":

        rows = db.execute("SELECT hash FROM users WHERE id = (?)", session["user_id"])

        #Get currently logged in user's password and check to see if they've entered the same thing
        if not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
            flash("Current password was incorrect", category="danger")
            return render_template("settings.html", is_admin=is_admin, upcoming_shifts=upcoming_shifts)

        if not request.form.get("new_password"):
            flash("Please enter a new password", category="warning")
            return render_template("settings.html", is_admin=is_admin, upcoming_shifts=upcoming_shifts)

        if request.form.get("new_password") != request.form.get("confirm_password"):
            flash("New password did not match confirmation", category="danger")
            return render_template("settings.html", is_admin=is_admin, upcoming_shifts=upcoming_shifts)

        else:
            password_hash = generate_password_hash(request.form.get("new_password"))
            db.execute("UPDATE users SET hash = (?) WHERE id = (?);", session["user_id"], password_hash)
            flash("Password changed successfully!", category="success")

    return render_template("settings.html", is_admin=is_admin, upcoming_shifts=upcoming_shifts)


@login_required
@app.route("/app_settings", methods=["GET", "POST"])
def app_settings():

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    current_holidays = db.execute("SELECT * FROM public_holidays;")

    if request.method == ["POST"]:

        holiday_to_add = request.form.get("holiday_date")

    return render_template("app_settings.html", is_admin=is_admin, current_holidays=current_holidays)


@login_required
@app.route("/create", methods=["GET", "POST"])
def schedule():
    """The scheduling worker outerer"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    # make sure function can access global variable temp to ensure it can actually commit the preview to the DB should user want
    global temp
    global start
    global end

    if request.method == "POST" and "Confirm" in request.form:

        # if user has hit confirm on the preview, access the stored schedule from the temp variable
        for week in temp:
            for day in week:
                if db.execute("SELECT * FROM schedule WHERE date == (?)", day["date"]):
                    db.execute(f"UPDATE schedule SET (AM_1, AM_2, PM_1, PM_2) = (?, ?, ?, ?) WHERE date == (?)",
                                day["AM_1"], day["AM_2"], day["PM_1"], day["PM_2"], day["date"])
                else:
                    db.execute("INSERT INTO schedule (date, AM_1, AM_2, PM_1, PM_2) VALUES (?, ?, ?, ?, ?)",
                                day["date"], day["AM_1"], day["AM_2"], day["PM_1"], day["PM_2"])

        flash("Submitted successfully!", category="success")

        # clear temp for later, clear start and end for later
        temp = []
        start = ""
        end = ""
        return redirect("/")

    elif request.method == "POST" and "dates" in request.form:
        # redirect user back to create if they want to choose different dates
        return redirect("/create")

    elif request.method == "POST" and "redo" in request.form:

        # If user wants to redo the schedule with the same dates as before
        # Access stored dates
        days_to_schedule, total_work_weeks = schedulerhelpers.get_period_to_schedule(start, end)

        # Query schedule to see how current schedule is set up and make a blank day based on this
        headings = db.execute("SELECT name FROM pragma_table_info('schedule') WHERE name != 'id' ORDER BY cid")
        blank_day = {}
        for item in headings:
            column_name = item['name']
            blank_day[column_name] = ""

        schedule = schedulerhelpers.put_dates_in_blank_schedule(blank_day, days_to_schedule, start)

        # Get current roster
        roster = db.execute("SELECT * FROM staff")

        # Work it all out
        done_schedule = schedulerhelpers.schedule(schedule, roster)

        # overwrite previous temp
        temp = done_schedule
        totals = schedulerhelpers.count_weighting(schedule)

        return render_template("preview.html", days_to_schedule=days_to_schedule, total_work_weeks=total_work_weeks, schedule=done_schedule, totals=totals, is_admin=is_admin)

    # If user's selected the dates they want to schedule on this page and hit submit:
    elif request.method == "POST":

        # Get the dates plugged in as strings turn them into dates
        start_date = schedulerhelpers.convert_start_date(request.form.get("start_date"))
        end_date = schedulerhelpers.convert_future_date(request.form.get("end_date"))

        # Check to make sure user has put in dates that meet requirements, and isn't scheduling for the past
        if type(start_date) != date or type(end_date) != date:

            if start_date == "date in past":
                flash('Start date cannot be in the past', category='danger')

            # This to protect against someone playing around with the HTML and then trying to submit
            elif start_date == "invalid input" or end_date == "invalid input":
                flash('Invalid input', category='danger')

            elif start_date == "too far in advance":
                flash('Please enter a start date closer to the present day', category='danger')

            elif end_date == "date in past":
                flash('End date cannot be in the past', category='danger')

            elif end_date == "too far in advance":
                flash('End date too far in advance', category='danger')

            elif end_date == "future is same as today":
                flash("Please schedule for more than one day", category='danger')

            return render_template("create.html", is_admin=is_admin)

        elif start_date == end_date:
            flash("Please schedule for more than one day", category='danger')
            return render_template("create.html", is_admin=is_admin)

        else:

            # Query schedule database to see if a schedule already exists for this timeperiod and ask user if they want to proceed via flash message
            if db.execute("SELECT * FROM schedule WHERE date >= (?) AND date <= (?)", start_date, end_date):
                flash("A schedule already exists for the dates chosen. Do you wish to continue and reschedule these dates, overwriting the previous schedule?", category="warning")

            # If user wants to go ahead and schedule, generate preview
            days_to_schedule, total_work_weeks = schedulerhelpers.get_period_to_schedule(start_date, end_date)

            # First prepare the selected dates using existing working function to prevent the need to rework
            # Query schedule to see how current schedule is set up and make a blank day based on this
            headings = db.execute("SELECT name FROM pragma_table_info('schedule') WHERE name != 'id' ORDER BY cid")
            blank_day = {}
            for item in headings:
                column_name = item['name']
                blank_day[column_name] = ""

            schedule = schedulerhelpers.put_dates_in_blank_schedule(blank_day, days_to_schedule, start_date)

            # Get current roster
            roster = db.execute("SELECT * FROM staff")

            # Work it all out
            done_schedule = schedulerhelpers.schedule(schedule, roster)

            #ensure this variable is stored somewhere, store start and end dates in temp variables also in case
            temp = done_schedule
            start = start_date
            end = end_date
            totals = schedulerhelpers.count_weighting(schedule)
            return render_template("preview.html", days_to_schedule=days_to_schedule, total_work_weeks=total_work_weeks, schedule=done_schedule, totals=totals, is_admin=is_admin)

    # If user reaches page through GET:
    else:
        return render_template("create.html", is_admin=is_admin)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return schedulerhelpers.apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return schedulerhelpers.apology("must provide password", 400)

        # Ensure password was confirmed
        elif not request.form.get("confirmation") and not request.form.get("password"):
            return schedulerhelpers.apology("must confirm password", 400)

        # Query database for username to check username doesn't already exist
        rows = db.execute("SELECT * FROM users WHERE username = (?)", request.form.get("username"))
        if len(rows) == 1:
            return schedulerhelpers.apology("username already taken", 400)

        # Check values of password and confirmation match, let user know if they don't
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password == confirmation:
            return schedulerhelpers.apology("password and confirmation do not match", 400)

        # INSERT the new user into users, storing a hash of the user’s password, not the password itself.
        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?);", request.form.get("username"), password_hash)

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return schedulerhelpers.apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return schedulerhelpers.apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return schedulerhelpers.apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/delete_staff", methods=["POST"])
def delete_staff():
    """Deletes a staff member from the database"""

    entry = json.loads(request.data)
    entry_id = entry['id']
    found = db.execute("SELECT * FROM staff WHERE id = (?)", entry_id)

    if found:
        db.execute("DELETE FROM staff WHERE id = (?)", found[0]['id'])
        flash("Deleted successfully!", category="success")

    return jsonify({})

@app.route("/update_staff", methods=["POST"])
def update_staff():
    """Updates a staff member from the roster page"""

    # Get the updated data from the js function
    entry = json.loads(request.data)

    # query database for a staffmember with the matching ID, and if matching, update valid values
    found = db.execute("SELECT * FROM staff WHERE id == (?)", entry["id"])

    if found:
        if entry['name'] != '':
            db.execute("UPDATE staff SET name = (?) WHERE id == (?)", entry['name'], entry["id"])

        if "choose" not in entry['contract'].lower():

            contract = entry['contract']
            nonworking = ""

            if contract == "P_1":
                contract = "P"
                nonworking = "pm2 3 4"

            elif contract == "P_2":
                contract = "P"
                nonworking = "0 1 am2"

            if contract == "P":
                db.execute("UPDATE staff SET (contract, nonworking_days) = (?, ?) WHERE id == (?)", contract, nonworking, entry["id"])

            else:
                db.execute("UPDATE staff SET contract = (?) WHERE id == (?)", contract, entry["id"])

        if entry['cando1'] == True:
            entry['cando1'] = "y"
            db.execute("UPDATE staff SET cando1 = (?) WHERE id == (?)", entry['cando1'], entry["id"])
        if entry['cando1'] == False:
            entry['cando1'] = "n"
            db.execute("UPDATE staff SET cando1 = (?) WHERE id == (?)", entry['cando1'], entry["id"])
        if entry['cando2'] == True:
            entry['cando2'] = "y"
            db.execute("UPDATE staff SET cando2 = (?) WHERE id == (?)", entry['cando2'], entry["id"])
        if entry['cando2'] == False:
            entry['cando2'] = "n"
            db.execute("UPDATE staff SET cando2 = (?) WHERE id == (?)", entry['cando2'], entry["id"])

    return jsonify({})

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    """Allows user to reset their password if they've forgotten it"""
    return render_template("reset_password.html")

"""def send_email():

#send_email(subject, sender, recipients, text_body, html_body)

    msg = Message('Testing scheduler email', recipients=['zoeposnette@googlemail.com'])
    text_body = 'This is a test email!'
    html_body = '<p>This is a test email!</p>'
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)"""

@app.route("/export", methods=["GET", "POST"])
def export():
    """Final part of the veiw page, allowing export of shifts"""

    # Get is_admin detail for access to app config page
    rows = db.execute("SELECT is_admin FROM users WHERE id = (?);", session["user_id"])
    is_admin = rows[0]["is_admin"]

    if request.method == "POST":

        export_ready = "y"
        return render_template("export.html", is_admin=is_admin, export_ready=export_ready)

    return render_template("export.html", is_admin=is_admin)