# SCHEDULER
A shift scheduling software- released to 1.0

#### Video Demo:
 https://youtu.be/S5UVkyt33sk

# Description:

## Introduction:

My CS50 final project is **Scheduler**, a program to speed up the task of shift scheduling for teams that need to have multiple staff working on a rota basis.

My inspiration came rather boringly from my own job in IT tech support. Democratically, staff are encouraged to take it in turns to organise shifts for the next few months but in reality this particular task is quite time consuming and needs the staff member to consult everyone's diary for their availability, as such, nobody really wants to complete the task. I thought for my small team, this task could be significantly improved for whoever draws the short straw by letting the computer produce the schedule after a few simple paramaters are set. The more I thought about the problem I wanted to solve with this software, I also thought there was a lot of scope for building the functionality of the program as my own confidence and skills grew.

## Initial problem:

The rules I needed **Scheduler** to satisfy initially were as follows:

- A work week is 5 days, (Not counting planned national holidays), Monday to Friday
- A work day is split into AM and PM sessions
- Each session needs 2 staff to cover, fulfilling a first line support and a second line support role.
- The program needed an algorithm that would evenly distribute shifts between a list of available staff on that day, moving through this list as empty shifts are filled. It was important that the shift pattern produced differed week-by-week to allow staff to have other time for their non-helpdesk shift work such as assisting with development work and running training sessions.

After these four requirements were fulfilled, I decided I could then move on to add further support for other functionality within the program, but I needed to be clear with myself that I could not work on anything more complicated until I had the basic framework working, so as to avoid scope creep and getting lost overthinking my own lofty goals.

Some stretch goals for myself after this milestone was reached were for example:

* The ability to support part-time staff- so the program would know which days of the week these staff were unable to work on
* The ability to set upcoming holiday for staff members so the program doesn't try to schedule them either if they weren't at work
* Automatic knowledge of national holidays
* Ability to have some staff only cover a certain type of shift depending on their skillset

The list very much went on.
I would decide on how I wanted my front-end to look after I had my initial goals working.

## Initial design choices:

Before taking CS50, I had been learning to program for about a year and I had the most experience and familiarity in Python prior to taking the course. I knew off-hand of several library functions that I intended to use to drive my sorting algorithm- mainly ```random```'s ```shuffle``` function, to shuffle an initial list of available staff to produce varied shift patterns for each desired week. I also thought I could look into using ```datetime``` for display of real-world dates when it came to building a user interface of sorts.

Once I'd taken the SQL week and moved onto Flask, I was interested in the ease of storing parameters and facts about my staff in a database to avoid having hard coded work in my Python files. I also thought this could be a good way of storing past shifts that the staff had worked- this would be of no benefit to me in the initial design of the program but it could be used to complete statistics from a managment or HR perspective of how much work of a particular type a worker has been able to complete.

## Project development logs:

### First few days/weeks of the project:

I started to plan how my project should look and behave with a few weeks left of CS50 to go. I was keen to get the idea in my head into the computer before I forgot how I wanted **Scheduler** to behave.

I started by testing my algorithm theory of iterating through a given list of staff and adding their names to a blank, empty list in turn. This worked perfectly when using ```shuffle``` on the list every time the program was run and a new list of names of any length I desired was produced. I changed this to produce a list of 20 names (5 days of the week * 4 shifts per day) and allowing a user to input a desired amount of weeks to schedule as a prompt in the terminal. The program then printed the results to the terminal.

 I could argue that this program now fulfilled my most important rule of the project going in, _that each week was a different shift pattern than the last._ This is important as for my use case, the staff are concerned about having variety in their work but also that each week of work is distributed fairly without too much weighting on one person or another.

 It's now a minimum viable product that produces a not very readable list of names that a user could manually copy over into however the actual shifts are recorded and manually discount holidays or shifts where the staff member was unavailable. This would still not pass the "boringness" test of the task at hand, as the user would still have to put in time and effort to sort out the shifts properly. This would also defeat the object of the output of a names list, if after using the program the staff member sorting the roster has to make sweeping edits and changes the order of the output to solve the original problem.

I moved onto thinking about how I could attach meaning to the list of names produced to make it more readable for the end user. I surmised a Python dictionary would work well here, with the original list of names being now a list of dictionaries. Each day would be a dictionary with a "date" field, and 4 slots for each shift. My dictionary by the nature of the data type wouldn't be inherently sortable, so the "date" field would be important to keep track of which day the dictionary was referring to. To test this theory to begin with, I made a hard coded simple list of the days of the working week to iterate through my dictionary of days and made a prototype function: ```make_blank_schedule(amount_of_days, test_dates)```. The idea of this function was that ```amount_of_days``` was an integer passed in, of the total amount of days to schedule and for now ```test_dates``` was my hardcoded list of the days of the week to plug into each blank day to fill up the "date" key. I defined the prototype for each day as a dictionary at the top of my file with the keys pre-filled, and all of the values blank.

I learned an important lesson about copying my blank ```test_day``` into each dictionary that I hadn't encountered before the project. It turns out that appending the same ```test_day``` to the end of the days list was actually copying the same reference in memory to the very same ```test_day```, however many times I appended it. As I started to iterate through my list of days and adding the days of the week, I was mystified about why my printed result had set every day to be Friday. Having diagnosed my problem, (And being transported back to several weeks of headaches and fighting with memory in C) I fixed this by defining days as: ```[test_day.copy() for day in range(amount_of_days)]```

My next hurdle would then be to marry my sorting algorithm with my more readable days list and fill in the blank values of "AM1", "AM2", "PM1", "PM2" with names. I could worry about making the staff data structures more than a string representing their name after I had sorted the above, as I knew it wouldn't necessarily be as simple as iterating through a list.

I started by defining a hard-coded list of 6 staff.
I then started to define a function that would shuffle the input list of staff and put them into the blank values of each day. I needed to get the blank values somehow and be able to update them in turn.
I achieved this by iterating through each day in the days list, checking if each key in the day was empty, and if it was, putting the next name in the list in place. This also worked fine after some trial and error. My minimum viable project was now a bit more readable, with meaning attached to who was going to be able to work in each slot.

With all of the above sorted, I now feel confident that my program works to my minimum goals. I could easily replace my test names with the people I work with and get to scheduling the next few weeks of shifts. I could go back to prompting for how many weeks I wanted to schedule for to make it a bit more user friendly. At this stage I showed a second person my output and the comment made was that some days repeat throughout the week- this is expected given I am not changing how I shuffle and sort through my list of names. As I start to expand functionality to allow for times where staff are unavailable, this should change the pattern of names as time goes on.

### Building on my MVP:

With my program doing the bare minimum of what I would like it to do, it's time to move on to making it more dynamic and more like the real world data I work with. The question was what to tackle next.

I settled on being able to build staff being unavailable into the program as I felt this was the next sensible goal. I needed to be able to reflect some staff being part time and factor this into the ```schedule()``` function.

To test this theory, I changed my list of test names to be another list of dictionaries to give my pretend staff a meaningful key, value pair that would denote if they were full time or part time, and if part time, what days of the week they could work on. I can already see a potential problem emerge that could change the sorting element of ```schedule()``` ultimately, _should there be a minimum amount of shifts a part time worker should do?_ This could get missed if there were so many staff that their name was missed on their working days, but this could be part of the programmable elements later on in the lifecycle of the project.

With a couple more conditions added to my ```schedule()``` function, I now have a system that allows for different working patterns. I implemented ```tabluate``` at this point for nicer command line testing.

Well where next? I want to be able to set periods of time where workers might be on holiday, or unavailable for a session if they have a meeting. To do this, I need to work on dealing with dates. I need to work on getting the ```datetime``` implemented and adding proper dates into the "date" field of each day dictionary.

### datetime:

Now I'm bringing in datetime, it makes sense to work in the ability for the user to specify when they are scheduling for.

I made a test program to see if I could calculate a total amount of work weeks and work days using ```timedelta```, as I would need to factor in the fact that I don't want to schedule for Saturdays and Sundays. Once this was working, my next challenge was to be able to attach specific dates as a value to my currently working list of day dicts.

From here, I made significant progress on my main program, to the point where I was so focused on making each next step work that I forgot to keep this log updated. I reached the point where I had a multi-function, navigable console program that prompts the user to either schedule, or view the current roster of staff (with the eventual idea here that a user could make changes to this in future). I settled on keeping the roster of staff and the structure of a blank day as csv files to continue to make this functionality work, as I hoped to make the jump to a navigable web app shortly after making my core functionality stable.

## The first version:

The first iteration of my working program is now entirely written in Python and achieves all of the first goals I hoped to acheieve. I have a program that can navigate full time and part time staff, and if they can work a particular type of shift. I tested this by plugging in a few weeks for the future, setting up a roster of staff based on my actual colleagues, and I was able to instantly generate a few weeks of the schedule, which is ultimately what I hoped to acheieve- instant schedules, with minimal editing needed. At this point, I felt it was time to move over to a web application that could build on a SQL database to store further data and attributes for the staff, mainly their unavailable days (through holiday or other meetings) and I surmised that in my current method of storing attributes in csv files would get out of hand quickly when dealing with lists of unavailable days and times.

A brief overview of the Python version before starting the refactor:

The program's main loop first calls a function, ```startup()``` and stores it's return value in a variable called option, to represent the option the user has selected from those available. ```startup()``` simply calls in order, a neat title of the program, and then displays the available options for the user to choose. It involves some input validation to ensure the user selects an available option using try and except blocks. A second function is then called, ```get_roster()```, and stores this return value in a variable called roster. This means that the actual working roster list could change in future, if this program was used to schedule for different amounts of staff, and the only file that would need to change is the csv that stores the actual roster. The program then checks ```option``` to see what was chosen, and runs one of 3 options as appropriate using an if loop- schedule, view or exit the program. View and exit are the least complex- view calls ```view_roster()```, passing in the current roster and printing it to the console in a user friendly way, using the ```tabluate``` module. Exit utilises ```sys``` to exit the program without a traceback.

Schedule requires several checks to happen to work. First, the user is asked for the start date. I contained this within a function, ```get_start_date()``` because I wanted to make sure the user wasn't choosing dates in the past, or entering dates that weren't actually valid. Similarly, the user is then prompted for a future date, with similar validity checks contained in helper functions.
When the two dates are stored in variables, I then needed to work out the total working days to schedule, and perhaps redundantly, the amount of work weeks this turned into. I kept this second check for error checking as I built this program. Once I had worked this out, I made a seperate function, verbosely called ```put_dates_in_blank_schedule()``` which is where I stored my refactored dates test from before, and I was most proud of getting this working. This function takes in a blank day template to structure how many slots need to be filled on the day, the total amount of days needed, and a start date, chosen by the user before.
The body of this function creates a blank list to put the schedule in, then using ```datetime```'s ```date.weekday()``` function, works out what day of the week the start date is- to weed out weekends and to count the amount of working days that the first week scheduled should contain. The function sets up a for loop to run through this first working week, and changes the blank "date" field in each day dict to be the actual date of the time period requested. As the loop progresses, the function changes the ```start_date``` variable worked out earlier using ```timedelta``` to roll the working date forwards.
I store each working week in a seperate list, so the ultimate end product ```schedule``` is a list, full of lists of working weeks, and each week list contains however many day dictionaries that there should be for that week.
Full working weeks need to be worked out next, so using a tracking variable called ```days_needed```, while this is divisible by 5, a full working week is calculated. The loop breaks if after this loop no days remain to be worked out, but if it finishes and days remain, the final week is then calculated and appended to the end of the ```schedule``` list.

With this done, it was easy to put names into this schedule, implementing my test functions from previously. For each week in the schedule, the roster is shuffled to pick a starting staff member. The function then loops through the days in the list, putting staff in order into each shift slot. I built checks to check the staff member's ability to do this shift contained in a helper function ```_staff_can_do_shift()``` which runs three checks against the staff member. If any of the checks fail, this person can't do the shift and the main schedule function should move onto the next staff member in the list. I check if the staff member is part time in this function, and if they are, a seperate function validates the days the part time staff member can't work, what day is being scheduled for. I then check if the staff member can work the type of shift, and then finally I built the skeleton for checking if the staff member was unavailable.

Once all of this was done, the program then displays, again using ```tabulate``` each now scheduled week to allow the user to copy the information into however the team reads these shifts- in my real world example I would then need to put these shifts into a shared Outlook calendar.

With all of this complete, I felt now was the time to make the program more dynamic and user friendly, and move it onto a web application to allow for a nicer UI and for features such as logging in and a better way of saving the output of the problem. My program works in it's current state and is the longest program I have written to date- and I already feel like I've acomplished a huge amount. It's now time to push this further.

### **Scheduler 2.0**

Now my basic program worked, I needed to decide how I wanted users to interact with the program. I considered trying to use ```tkinter``` to build a Python only nicer graphical UI- but to demonstrate and pull from other areas of CS50- I thought I could achieve more with a web application built on a Flask framework, so I could carry my working scheduling functions into the end product with ease, should they need to come forward if I was then working with a database instead of csv files. What else could then be achieved using this method?

- user logins. Each staff member could have their own login, to either complete a schedule, or to update thier own availability, or even eventually, request to swap shifts.
- admin or management login. Should a different workplace have different rules to my own, scheduluing access could be restricted to certain users.
- ease of schedule lookup. If the schedule is moved into a database table, a search function could be implemented to bring up particular days stored in a completed schedule table.
- ease of staff variable editing and storage. If my roster of staff is now just a different table, administation pages could be built to allow edits to change if someone can or can't do types of shift as an example.
- more variety with the UI. I have less experience with front end development but once the program works (again), I then have more scope to make a interactive webpage.

### First changes to functionality

Building on the knowledge gained by completing CS50's Finance project, before reworking the main scheduling "engine" I needed to make a landing page to ask for users to log in or register to make changes within the application. I'd need to decide on an initial database structure to do this. To begin with, I supposed that I would need 2 tables at least within the database- one to store the user's information (And by that same token, their staff attributes), a second to organise unavailability for certain days, and thinking about it, probably a third to store the worked out schedule to allow for functionality like shift swaps later.

My first challenge was to get to the same point as I'd got to with my console version.

I found it relatively easy to set up a basic Flask application, building on the Finance project to implement a main landing page, login and registration pages that I hoped to improve later (with minimum password requirements and the likes). Once this was done, I fleshed out some other eventual functionality I hoped to implement before getting started on the main page. I added an empty user settings page, a view page (I could turn this into the main landing page- an interactive calendar to allow someone to click on dates to view), a page to create the schedule from, and a page to add staff to a roster. I hoped to expand this to be an "admin role only" page in the future so that only users with the right type of profile could set up the staff page, make changes and also make changes to the structure of the shifts- eventually.

I then got to work on the "create" page- so the page that pulled my main engine from my first version. It's first iteration is a simple webform prompting the user for the start and end date to schedule, and a button to submit this.
I wanted to be able to flag to the user that they had provided bad input through message flashing, so at the time of writing this is my next TODO. Finally, I created a simple success page that displays a form of the worked out schedule along with the dates. As I wrote and tested this, I noticed I was getting errors that I hadn't encountered in my first attempt at weekend and work week validation- my function that copies the blank day schedule was getting stuck somewhere in an infinate loop sometimes and I was mystified about how I hadn't seen this before.
On reviewing my function, I realised that this was definately overworked and complicated. I was running checks to convert the day of the week into my own "working week" convention and the infinate loop was being generated when I moved onto trying to work through full weeks. I was trying to divide by 5, but I wasn't checking if when I reached the end of a block of 5 steps- that the 5th day was actually a Friday. I'd initially been really proud of this function so I was annoyed it needed to be reworked, but having the hindsight of a few weeks away from looking at it meant it was easy to diagnose the issue and to really simplify in order to fix. All I really needed to do was check to see if I'd reached the end of the week, not bother converting into anything else, and just skip to the next Monday and I would achieve what I was originally trying to do.
I wanted to maintain this idea of a "working week" and moving into the next week to allow my randomness and sorting side of the algorithm to kick in for each new week created as this is an integral part of making the schedule dynamic for the workers.
To add to this, I ended up actually making a further table for my database to store public holidays and added a new check into my reworked date working out function- the check runs a query against the table to see if the date being added to the list to be scheduled is a public holiday, and the date is skipped if it is. As part of the settings page, I could then allow functionality to configure future public holidays later. To test, I manually added the upcoming public holidays for 2023 in the back end so I had something to work with.
As part of this rework, it had bothered me in the Python version of the program that I didn't yet have a way to make a staff member simply unavailable. I ended up adding a futrther table to store these dates and reference them against the id number for the relevant staff member as a foreign key relating to the staff table. I again added some test dates, but adding a check to the current scheduling algorithm was fairly simple. So with all of the above done, my program basically is in the same place as it was before my move to a web-based UI- and actually covers a further check my previous version hadn't. I wanted to be able to make the "unavailable" check more specific and talk about times within a day- sometimes a staff member might only be unavailable for half a day.

My next goals to work on were to make the main schedule page nicer in terms of it's validation and error checking. Once this is complete, I want to make a schedule preview page that will warn a user if the timeperiod they want to schedule for has already been worked out- allow the user to proceed if they want to override this, and ultimately hit a confirm button that commits their schedule to the database.

## The final version

After a couple of weeks of solid work, I feel like I now have the application I envisioned. I am particularly proud of my very own calendar page, which ensures that today's date is highlighted, can view past and future months and indicates if the schedule has been worked out for the days it's displaying.

A walkthrough of the project- from login, the application runs a check to see if the logged in user is an admin or not. In my current role, anyone can work out the schedule, but it would be up to management to add or remove staff or alter what sort of work they can take on, so I have simulated this by hiding this functionality behind this persmission level. An admin can also access a page called "Application settings" where the user can toggle if the scheduler should take into account weekends, the upcoming public holiday dates can be changed and the likes.

Next to this, there is a page called "user settings" which is visible to any user. This page allows the user to change their password if they would like, and if the user is also a staff member, displays a few of their upcoming shifts.

There are 3 main pages that any user can access to be able to use the application for it's intended function. View schedule as mentioned above, is a calendar view on landing. If shifts are present in the database for the day, each day has a clickable person icon that the user can select, which triggers an offcanvas information pane so the user can see who is working for that day. Should the user want more detail, from this page they can select "week" to see a week view of the calendar with names now visible with who should be working each slot. Finally, there is an "export" tab, where the user can export the data as a csv or as an .ics calendar invite to further automate this process. My current workplace stores the rota in a shared outlook calendar, so it would make sense that whoever is using my program can click a button and get the work sent to where it needs to go.

Create schedule is the main reason for the program existing and builds on all of my previous prototypes. Once the user chooses the dates they would like to work out (provided they're not trying to schedule for the past), the program produces a preview page. This will warn the user if they are about to overwrite work- but this also allows the user to try and reschedule if they would like. Essentially, there's an element of RNG in terms of how the shifts are sorted out, so I noticed when testing that if you don't have many staff in your roster, a lot of days start to follow the same pattern which would be boring for my current workplace. The user might also want to sure that a newer member of staff has someone more experienced works with them at the same time. The user can also select different dates before committing, in case they made a mistake.
I tweaked the scheduling function before settling on if I was happy with it to try and reduce some of the repetition. The function now checks to see how many staff are now available to work a day and if it's less than 5 (For now as the sweet spot where I noticed the repetition reducing from), rather than shuffling the working out staff list per week, it does this before each day.
I also changed how someone is handled if they can't do the offered shift. Previously, the function would just move onto the next person in the list if the currently checked staff member couldn't work. This meant that it would be several shifts later when the same person would be offered again- which in practice probably isn't right if their number came up at a certain point. I changed this to mean that if someone can't do the current shift, they get put back in the list, just one slot down in the order so they are checked against the next and not lost at the end of the pile. I am adding them to the top of the stack, to use terms we learned in the course.

Finally, any user can access "Change availability" as manually, this is what we would do anyway. I deliberately have not used specific times throughout the program- the meaning of when the shifts are could differ between workplaces. When editing details within this page, the user can choose if someone isn't around for a full day or a part day in the morning or afternoon. If they have an hour long meeting, or a training session that isn't as long as the full shift, then they still won't be around to work the entire shift so I didn't see that this would bring any benefit to the program in it's current iteration while reducing my own workload.

## Project file descriptions:

### flask_session
This folder contains the flask session data, so that the app remembers which user is logged in. This is important so the app can differentiate between an admin or not, along with being able to call up their data if they are a staff member.

### static
*  styles.css
* title.png
* index.js
* Scheduler.png
* 483795-PGTJHS-240.jpg

This folder contains the static files needed to run the site. I have my stylesheet, a couple of versions of my application's logo/title, a javascript file that drives a couple of onclick functions so actions take place without the page having to refresh and an image from Freepik (https://www.freepik.com/free-vector/colorful-hand-drawn-productivity-concept_3271325.htm#query=productivity%20icon&position=0&from_view=keyword&track=ais) that I've used to make my landing page look nice.

### templates
This folder is where all the templates for the webpages of the app are kept.

  Template    | Description
------------- | -------------
apology.html  | Displays a nicer error message for 400 errors, etc
app_settings.html  | Settings for the application- admin only
availability.html | Allows any user to alter staff availability
create.html | Allows any user to create a schedule for user-chosen dates
export.html | Allows any user to export the schedule as a csv or meeting invites
index.html  | Main landing page when user first logs in
layout.html | Main tempate that contains the boilerplate code, navbar and footer for all pages
login.html  | The login page
preview.html | This page displays to allow the user to check the schedule before committing it to the database
register.html | Allows a new user to register to use the app
reset_password.html | Allows the user to reset their password if they've forgotten it
roster.html | Allows an admin to make changes to the staff members
settings.html | User specific settings- so reset their own password for example
view_week.html | Working week view of the schedule
view.html   | Month view of the schedule

### app.py
This is the main driver code for the application. The application is initialised, each view function is kept here.
There are a couple of functions towards the end of the program that are triggered from the javascript onclick functions. Take deleting a staff member from the roster for example. There is a button on the roster page- when clicked, the javascript takes the data about which button was clicked, passes it to a delete staff function within app.py, which queries the database and removes the entry if it exists. This flashes a success or failure.

### README.md
This document!

### scheduler.db
The Scheduler SQL database that the app queries and edits.

### schedulerhelpers.py
This file contains all the funtions that work out how the schedule should be structured and were taken from my intial test console program. As my program grew, this file turned into a hugely long file at over 600 lines of code.

## Project dependencies:
Within app.py:

### SQL from the cs50 module
* flask
* flask_session
* flask_mail
* tempfile
* werkzeug.security
* datetime
* json
-my own schedulerhelpers
-os

### within schedulerhelpers:

* datetime
* random
* csv
* SQL from the cs50 module
* calendar
* ics
* os
* requests
* urllib.parse
* flask
* functools

### Framework
* Structure of the web application is built on Bootstrap as a base.