# Function collection for golf statistics

###########################################
## Function to enter golf course details ##
###########################################

# Description: Function will prompt user to enter details by hole from scorecard for either 9 or 18 holes

def get_hole_info():
    
    tmp = pd.DataFrame(columns=['Course Name','Course Tees','Hole','Yardage','Par'])
    course_name = input("Enter the Course Name: ")
    course_tees = input("Enter the Tee Name: ")
    num_holes = input("Enter the number of holes (18 or 9): ")
    
    if num_holes == "18":
        for hole in range(1, 19):
            ydg = input(f"Enter yardage for hole {hole}: ")
            par = input(f"Enter par for hole {hole}: ")
            new_row = pd.DataFrame({'Course Name':[course_name],'Course Tees':[course_tees],'Hole':[hole],'Yardage':[ydg],'Par':[par]})
            tmp = pd.concat([tmp, new_row], ignore_index=True)
    elif num_holes == "9":
        for hole in range(1, 10):
            ydg = input(f"Enter yardage for hole {hole}: ")
            par = input(f"Enter par for hole {hole}: ")
            new_row = pd.DataFrame({'Course Name':[course_name],'Course Tees':[course_tees],'Hole':[hole],'Yardage':[ydg],'Par':[par]})
            tmp = pd.concat([tmp, new_row], ignore_index=True)
    else:
        print("Invalid input. Please choose either '18' or '9' holes.")
    return tmp

## Example on how to call and use the function:
# course_info = get_hole_info()
# print(course_info) - view the course details - we need to write it then to the base dataset 

#############################################
## Function to enter summary round details ##
#############################################

# Description: Function will prompt the user to enter the basic summary details from their round to include course, holes played, tees played, and score

def create_summary_round():

    tmp = pd.DataFrame(columns=['Date','Course','Event','Tee','Holes Played','Course Handicap','Score'])
    date_entry = input('Enter a date in YYYY-MM-DD format: ')
    year, month, day = map(int, date_entry.split('-'))
    date1 = datetime.date(year, month, day)

    course_name = input("Enter the Course Name: ")
    course_tees = input("Enter the Tee Name: ")
    occasion = input("What is the Event/Occasion for Round: ")
    num_holes = input("Enter the number of holes (18, Front 9,  or Back 9): ")
    course_handicap = input("Enter the your Course Handicap: ")
    score = input("Enter the your final score (not adjusted for course handicap): ")
    new_row = pd.DataFrame({'Date':[date1],'Course':[course_name],'Event':[occasion],'Tee':[course_tees],'Holes Played':[num_holes],'Course Handicap':[course_handicap],'Score':[score]})
    tmp = pd.concat([tmp,new_row], ignore_index=True)
    return tmp

## Example on how to call an use the function:
# round_summary = create_summary_round()
# print(round_summary) - view round details - need to write it then to the base dataset

######################################
## Function to enter detailed round ##
######################################

# Description: Function will prompt the user to enter a detailed round summary to include GIR, FIR, and putting trends

def detailed_round_trends():
    
    tmp = pd.DataFrame(columns=['Date','Course','Event','Hole','Tee','Fairway','Green','Putts',	'Score'])
    date_entry = input('Enter a date in YYYY-MM-DD format: ')
    year, month, day = map(int, date_entry.split('-'))
    date1 = datetime.date(year, month, day)
    
    course_name = input("Enter the Course Name: ")
    course_tees = input("Enter the Tee Name: ")
    num_holes = input("Enter the number of holes (18, Front 9,  or Back 9 ")
    occasion = input("What is the Event/Occasion for Round: ")
    
    if num_holes == "18":
        for hole in range(1, 19):
            fir = input(f"Enter Fairway in Regulation for hole {hole}: Right, Hit, Left, Short, Long, N/A  ")
            gir = input(f"Enter Green in Regulation for hole {hole}: Right, Hit, Left, Short, Long, N/A  ")
            putts = input(f"Enter number of putts for hole {hole}:  ")
            score = input(f"Enter score for hole {hole}:  ")
            new_row = pd.DataFrame({'Date':[date1],'Course Name':[course_name],'Event':[occasion],'Hole':[hole],'Course Tees':[course_tees],'Fairway':[fir],'Green':[gir],'Putts':[putts],'Score':[score]})
            tmp = pd.concat([tmp, new_row], ignore_index=True)
    elif num_holes == "Front 9":
        for hole in range(1, 10):
            fir = input(f"Enter Fairway in Regulation for hole {hole}: Right, Hit, Left, Short, Long, N/A  ")
            gir = input(f"Enter Green in Regulation for hole {hole}: Right, Hit, Left, Short, Long, N/A  ")
            putts = input(f"Enter number of putts for hole {hole}:  ")
            score = input(f"Enter score for hole {hole}:  ")
            new_row = pd.DataFrame({'Date':[date1],'Course Name':[course_name],'Event':[occasion],'Hole':[hole],'Course Tees':[course_tees],'Fairway':[fir],'Green':[gir],'Putts':[putts],'Score':[score]})
            tmp = pd.concat([tmp, new_row], ignore_index=True)
    elif num_holes == "Back 9":
        for hole in range(10, 19):
            fir = input(f"Enter Fairway in Regulation for hole {hole}: Right, Hit, Left, Short, Long, N/A  ")
            gir = input(f"Enter Green in Regulation for hole {hole}: Right, Hit, Left, Short, Long, N/A  ")
            putts = input(f"Enter number of putts for hole {hole}:  ")
            score = input(f"Enter score for hole {hole}:  ")
            new_row = pd.DataFrame({'Date':[date1],'Course Name':[course_name],'Event':[occasion],'Hole':[hole],'Course Tees':[course_tees],'Fairway':[fir],'Green':[gir],'Putts':[putts],'Score':[score]})
            tmp = pd.concat([tmp, new_row], ignore_index=True)
    else:
        print("Invalid input. Please choose either '18' or '9' holes.")
    return tmp

## Example on how to call an use the function:
# detailed_round = detailed_round_trends()
# print(detailed_round) - view round details - need to write it then to the base dataset