"""
UI for scheduling and playout of clock chimes stored as .mp3 files

Manage a church or other electronic carillon to playout .mp3 files of
user-provided songs, peals, tolls, and hourly strikes at scheduled system
time(s). Requires Python3 but no desktop environment.  Creates a text
based user interface between stdin and stdout for adding, deleting, or
changing scheduled playouts. Requires the playsound module for audio
playout which in turn uses windll.winm on Windows, AppKit.NSSound
on Apple OS, or GStreamer on Linux. The Playsound module for Python2 is
incompatible with that for Python3, so if Python2 is present on the
target system, playsound must be installed with 'pip3 install playsound'"""

# D.L. Poole July 2021


import threading
import time
from playsound import playsound

# The file path is prepended to user given file names.  It will be
# platform and installation-dependent
file_path = "/home/dave/Carillon/"

# The schedule is an unordered list of playout events
# Default schedule for a tower clock
schedule=[]
schedule.append(["",0,6,0,23,59,"Hour"])
schedule.append(["",0,6,0,23,0,"Strike"])
schedule.append(["",0,6,0,23,15,"Quarter"])
schedule.append(["",0,6,0,23,30,"Half"])
schedule.append(["",0,6,0,23,45,"ThreeQuarter"])

# Weekday List and Dictionary for validation/encoding of user input
day_list = ['su','mo','tu','we','th','fr','sa']
day_dict = {'su':0,'mo':1,'tu':2,'we':3,'th':4,'fr':5,'sa':6}

def main():
    """Text UI for Scheduling playout of electronic chime sounds in .mp3 files.

    Start a playout thread then enter an infinite while loop for user input. Wait
    on user input to build or maintain an unordered list of scheduled events. The
    user may request instructions, display any existing schedule, enter a line number
    followed by space-delimited parameters to add or replace an event, or enter a
    line number alone to delete a scheduled event."""

    # Start the playout thread as a non-daemon process
    threading.Thread(target = playout,).start()
    # Display user instructions
    show_instructions()
    # Wait on and accept user-input continuously
    #"You can check out any time you like, but you can never leave"
    while True:
        # Show schedule in case lines were renumbered
        print("")
        show_schedule()
        while True:
            try:
                # Prompt for user input then await it
                print(">",end = "")
                command = input()
                # ? shows instructions
                if command.split(" ")[0] == "?":
                    show_instructions()
                    break
                # null line shows schedule
                if command.split(" ")[0] == "":
                    show_schedule()
                    break
                # Otherwise, first user-input field must be a line number
                if (command.split(" ")[0]).isnumeric():
                    line_number = int(command.split(" ")[0])
                else:
                    print("Error: Input must begin with a line number")
                    break
                # Line number only is a request to delete
                if len(command.split(" ")) == 1:
                    # If there is anything to delete
                    if len(schedule) >0:
                        # Delete it
                        try:
                            schedule.pop(line_number-1)
                        except:
                            print("No line ",line_number," to delete")
                    break
                # Check for a complete entry, five single-spaced parameters  
                if len(command.split(" "))<5:
                    print ("Error: Enter five items, separated by single space")
                    print (" Line# Day Hour(s) Minute and Tune")
                    break
                # The second user input field is date, weekday, or weekday range
                # User entered a hard date as mm/dd/yy
                if "/" in command.split(" ")[1]:
                    if len(command.split(" ")[1]) != 8:
                        print("Error: Date must be mm/dd/yy")                       
                        break
                    # Convert to integer for validation
                    month = int(command.split(" ")[1].split("/")[0])
                    day = int(command.split(" ")[1].split("/")[1])
                    year = int(command.split(" ")[1].split("/")[2])
                    if month <0 or month >12:
                        print("Error: ", month, " is not a valid month")
                        break
                    if day <0 or day>31:
                        print("Error: ",day," is not a valid Day")
                        break
                    if year <21:
                        print("Error: ",year," is not a valid Year")
                        break
                    # Date is valid, but retrieve the string to save in event
                    date = command.split(" ")[1]
                    # Make weekdays out of range to disable daily playout
                    start_day = end_day = 8
                # User entered a weekday or weekday range e.g. su, su-sa, etc.
                else:
                    # Weekday ranges are defined by a "-" delimiter
                    days = command.split(" ")[1].split("-")
                    # Convert first weekday in string to an integer start day index
                    start_day = day_dict.get(days[0])
                    # Default to a single weekday if not a weekday range
                    end_day = start_day
                    # Weekday range contains a second string
                    if len(days) == 2:
                        # Convert second weekday in string to an integer end day index
                        end_day = day_dict.get(days[1])
                    elif len(days)>2:
                        print ("Error: Weekday list. Use multiple events instead")
                        break
                    # If the weekday is not in the dictionary
                    if start_day == None or end_day == None:
                        print ("Error: Day(s) must be su, mo, tu, we, th, fr or sa")
                        break
                    # User specified weekday(s) so null the hard date field in event
                    date = ""
                # The third user input field is an hour or hour range
                hours = command.split(" ")[2]
                start_hour = hours.split("-")[0]
                # Default to single hour
                end_hour = start_hour
                # An hour range is delimited by "-"
                if len(hours.split("-")) == 2:
                    end_hour = hours.split("-")[1]
                # Hour lists not supported
                elif len(hours.split("-"))>2:
                    print ("Error: Hour range must be start-end")
                    break
                # Convert start hour to integer for validation
                if start_hour.isnumeric():
                    start_hour = int(start_hour)
                else:
                    print("Start Hour(s) ", start_hour," must be numeric")
                    break
                if start_hour < 0 or start_hour > 23:
                    print ("Start Hour ",start_hour," must between 0 and 23")
                    break
                # Convert end hour to integer for validation
                if end_hour.isnumeric():
                    end_hour = int(end_hour)
                else:
                    print("End Hour ",end_hour," must be numeric")
                    break
                if end_hour < 0 or end_hour > 23:
                    print ("End Hour ", end_hour," must be between 0 and 23")
                # The fourth user input field is a minute value, never a range
                minute = command.split(" ")[3]
                # Convert minute to integer for validation
                if minute.isnumeric:
                    minute = int(minute)
                else:
                    print ("Minute ",minute," must be numeric")
                    break
                if minute <0 or minute > 59:
                    print ("Minute ",minute," must be between 0 and 59")
                    break
                # The fifth user input field is a file name (.mp3 file) which must
                # allow for embedded spaces or the "Strike" keyword
                file = command.split(" ",4)[4]
                # The strike keyword is case insensitive and
                # will be parsed into Strikexx.mp3 by the playout thread when used
                if file.lower() == "strike":
                    file_name = "Strike"
                # Striking requires twelve Strikehh files
                    for i in range(12):
                        file_name = file_path + "Strike" + str(i+1)+".mp3"
                        try:
                            f = open(file_name, "r")
                            if not f.readable():
                                f.close()
                                raise
                                break
                        except:
                            print("Error: File ", file_name," is missing")
                            break                    
                # Validate the user-supplied file name
                else:
                    if file.lower().endswith(".mp3"):
                        file_name = file_path+file
                    else:
                        file_name = file_path+file+".mp3"
                    try:
                        f = open(file_name, "r")
                        if not f.readable():
                            print("Error: ", file_name," is not readable")
                            break
                        f.close()
                    except:
                        print("Error:", file_name," not found - check sPeLLing")
                        break

                # The user's input line is fully parsed and validated
                # No break out of inner while loop due to a user error
                # Build an event list and insert or append it to schedule list
                # An event is an ordered list of parameters of mixed types defining
                # date, weekday or day range, hour or hour range, minute, and
                # a filename or the keyword "Strike"
                event = []
                event.append(date) # nul for day range or hard date as mm/dd/yy string
                event.append(start_day) # int starting weekday number
                event.append(end_day) # int ending weekday number
                event.append(start_hour) # int starting hour
                event.append(end_hour) # int ending hour
                event.append(minute) # int minute
                event.append(file) # prepend path, append .mp3 at playout
                
                # Append the event to or insert into in the schedule 
                if int(command.split(" ")[0])-1 >= len(schedule):
                    schedule.append(event)
                else:
                    schedule[int(command.split(" ")[0])-1] = event
            #wend of main()
            # Mop up any unanticipated error in parsing user input
            except:
                print("Unanticipated Error: User input line discarded")
    # wend of user input loop
         
def show_schedule():
    """Display the list of scheduled events. 

    Events are displayed in line order in roughly the same space-delimited
    format they were (or should have been) entered in.  Consecutive line
    numbers are prepended, new if an event has been deleted, to aid the user
    in editing"""
    
    print('Day(s) Hr(s) Min Tune')
    for i in range(0, len(schedule)):
        print(i+1,end = '')
        print(": ",end = '')
        # The first item in the event may be a hard date string
        if schedule[i][0] !=  "":
            print(schedule[i][0],end = " ")
        # or it may be a weekday number or weekday number range
        else:
            # Print the weekday or first weekday of a range
            print(day_list[schedule[i][1]],end = '')
            # and complete it if it's a range
            if day_list[schedule[i][2]]!= day_list[schedule[i][1]]:
                print ("-",end = '')
                print(day_list[schedule[i][2]],end = ' ')
            else:
                print(" ",end = '')
        # Display the event's hour or hour range        
        print(schedule[i][3],end = '')
        if schedule[i][3]!= schedule[i][4]:
            print ("-",end = '')
            print(schedule[i][4],end = ' ')
        else:
            print(" ",end = "")
        # Display the event's minute
        print (schedule[i][5],end = " ")
        # Finally display the strike keyword or file name
        print (schedule[i][6])
        
def playout():
    """Playout .mp3 files from a schedule list at :00 per their respective time-stamps.

    Upon launch or reawaken, the playout thread waits on the system minute, scans the
    schedule list, and plays any entries. Upon completion of the last entry, it calculates
    the time to the next system minute then requests sleep from the platform. Upon wake,
    it waits for the system minute then scans again. Note that a playout of length exceeding
    one minute may play instead of another event scheduled for that or the next minute.
    In case an unanticipated user error makes its way into the schedule list or the
    list is otherwise corrupted, an error is displayed, the event is removed from the
    schedule, and both UI and playout continue."""

    import datetime
    # Always keep running, even in the aftermath of user error
    while True:     
        # Synchronize to the next even minute by waiting on it
        while datetime.datetime.now().strftime("%S")!= "00":
            pass
        # Synchronized     
        try:
            # Scan all events in the schedule list
            for i in range(0,len(schedule)):
                # Parse for reasons why the ith event in the schedule isn't to be played or
                # struck right now().  Continue immediately to the next schedule item in
                # the for-loop if it isn't
                # Event is on hard date, continue if not today
                if schedule[i][0]!= "" and \
                   datetime.datetime.now().strftime("%x")!= schedule[i][0]:
                    continue
                # Event is on a weekday range, continue if now() is before it
                if schedule[i][1] <8 and \
                   int((datetime.datetime.now().strftime("%w")).lower())<schedule[i][1]:
                    continue
                # ... or after it
                if schedule[i][2] <8 and \
                   int((datetime.datetime.now().strftime("%w")).lower())>schedule[i][2]:
                    continue
                # Continue if event is set for a later hour today
                if int((datetime.datetime.now().strftime("%H")))<schedule[i][3]:
                    continue
                # ... or an earlier hour, so it must have already happened
                if int((datetime.datetime.now().strftime("%H")))>schedule[i][4]:
                    continue
                # continue if not right this minute (and second)
                if int((datetime.datetime.now().strftime("%M")))!= schedule[i][5]:
                    continue
                # All reasons a scheduled entry is not to be played now() have been cleared
                # So if its a strike, build the strike file name and play the strikes
                if schedule[i][6] == "Strike":
                    # Strike 12 hour time, with 12 strikes at Noon and Midnight
                    hour =  int(datetime.datetime.now().strftime("%H"))%12
                    if hour == 0:
                        hour = 12
                    playsound(file_path+"Strike"+str(hour)+".mp3")   
                # Its a previously validated file, so prepend the path, append the type,
                # and play it
                else:
                    ##print("Playing ",file_path+schedule[i][6]+".mp3")
                    playsound(file_path+schedule[i][6]+".mp3")
                # Playsound returns control only when play is done
                # wend of test for all parameters of the ith event or play it 
            # end of for-next loop to examine all events in the schedule
        # Mop up any oversignt in prior input validations or corruption of the schedule
        # list. Display an error and the failed event then delete that event. Keep
        # playout() running. Assume main() is still running, so display a replacement
        # user input prompt after the error messages 
        except:
            print("Internal Error: A scheduled event could not be played")
            print("Event ",i+1, schedule[i])
            print("Event ",i+1," deleted. Resuming schedule")
            show_schedule()
            print(">",end = "")
            schedule.pop(i)
        # All scheduled events checked and those for this minute played
        # Nothing to do until the next :00 so put this playout thread to sleep
        time.sleep(59-int(datetime.datetime.now().strftime("%S")))
    # wend to keep playout thread from exiting unless main() is closed
    
def show_instructions():
    """Display instructions for the UI on stdout

- Enter Line# Day(s) Hour(s) Minute and File Name or Strike..
- Separate line# and event parameters with a single space.
- Day is mm/dd/yy, su, mo, tu, we, th, fr, or sa.
- Hour is 24-hour time between 0 and 23.
- Minute is between 0 to 59.  Events play at hh:mm:00.
- Ranges are allowed and inclusive: 0-23 = hourly, su-sa = daily.
- Tunes are filenames and are cAsE SeNsiTiVe.
- Line#<enter> to delete a line.
- ?<enter> to repeat these instructions"""
    
    print("""- Enter Line# Day(s) Hour(s) Minute and File Name or Strike..
- Separate line# and event parameters with a single space.
- Day is mm/dd/yy, su, mo, tu, we, th, fr, or sa.
- Hour is 24-hour time between 0 and 23.
- Minute is between 0 to 59.  Events play at hh:mm:00.
- Ranges are allowed and inclusive: 0-23 = hourly, su-sa = daily.
- Tunes are filenames and are cAsE SeNsiTiVe.
- Line#<enter> to delete a line.
- ?<enter> to repeat these instructions""")
                        
# Run main() as a standalone program
if __name__ == "__main__":
    main()



