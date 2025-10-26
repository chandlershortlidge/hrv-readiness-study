import glob
# glob is a Python module that finds files matching a pattern.
import pandas as pd
from pathlib import Path

def get_all_workout_files():
    """Returns list of all workout file paths"""
    return glob.glob('../data/raw/workouts/*.txt')
# This says: "Find all files in the workouts folder that end with .txt"

def open_workout_file(file_path):
    """Opens a workout file and returns its lines as a list"""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def calculate_weighted_set_volume(line):
    """Takes a line like 'Set 1 : 40 kg x 9' and returns volume for that set"""
    parts = line.split(" x ")
    # splits string into list: ['Set 3 : 30 kg ', '14\n']
    sets = parts[0].split(":")
    # extracts first item in list, splits into new list by colon: ['Set 3 ', ' 30 kg ']
    weight = sets[1].split(" ")
    # extracts second item in list, splits new into new list by space: ['', '30', 'kg', '']
    kilos = weight[1]
    # assigns second item in list (the number) to variable kilos
    kilos = float(kilos)
        # converts kilos from object to float for calculations
    reps = parts[1].strip()
    # extracts reps from second item in original list, removes newline character
    reps = int(reps)
    # converts reps into an interger for calculations
    set_volume = kilos * reps
    # calculates volume for the set
    return set_volume


# create a function to deal with bodyweight exercises
def extract_bodyweight_volume(line, bodyweight):
      """Extracts total volume for bodyweight exercises from workout file lines"""

      if "reps" in line:  
         # extracts any string starting with "Set" and containing "reps"
         parts = line.split(" : ")
         # splits string into "Set #" and "# kg" (a list)
         reps_str = parts[1]
            # assigns the second item in the list to reps_str
         reps = reps_str.split(" ")[0]
            # splits the string by " " to isolate the number of reps
         reps = int(reps)
            # converts reps into an interger for calculations
         rep_volume = bodyweight * reps
            # calculates volume for each rep based on bodyweight
      return rep_volume


# build wrapper function to extract total volume from workout files
def extract_volume(file_path, bodyweight=80):
    """Extracts total volume from a workout file"""
    lines = open_workout_file(file_path)
    total_volume = 0
    for line in lines:
        if line.startswith("Set") and "kg" in line:
            set_volume = calculate_weighted_set_volume(line)
            total_volume += set_volume
        elif line.startswith("Set") and "reps" in line:
            set_volume = extract_bodyweight_volume(line, bodyweight)
            total_volume += set_volume
    return total_volume



def get_workout_name(file_path):
    """Extracts workout name from first line of file"""
    # open file
    lines = open_workout_file(file_path)
    # read first line and remove whitespace
    workout_name = lines[0].strip()  
    return workout_name

def get_workout_date(file_path):
    """Extracts workout date from file name"""
    # get filename without path or extension: '26_09_25'
    file_name = Path(file_path).stem
    
    # split to get parts: ['26', '09', '25']
    parts = file_name.split('_')
    day, month, year = parts[0], parts[1], parts[2]
    
    # convert 2-digit year to 4-digit: '25' -> '2025'
    year = '20' + year
    
    # create date string in YYYY-MM-DD format
    date_str = f'{year}-{month}-{day}'
    
    return date_str


def extract_set_data(line):
    """
    Extracts weight, reps, and volume from a set line.
    Returns a dictionary with the data.
    """
    parts = line.split(" x ")
    sets = parts[0].split(":")
    weight = sets[1].split(" ")
    kilos = float(weight[1])
    reps = int(parts[1].strip())
    volume = kilos * reps
    
    return {
        "weight": kilos,
        "reps": reps,
        "volume": volume
    }


def extract_exercise_sets(file_path, exercise_names, bodyweight=80):
    """
    Extracts individual sets for specific exercises from a workout file.
    
    Parameters:
    - file_path: path to the workout file
    - exercise_names: list of exercise names to track (e.g., ["Bench Press (Barbell)", "Squat (Barbell)"])
    - bodyweight: your bodyweight for bodyweight exercises
    
    Returns:
    - list of dictionaries, each containing date, exercise, set_number, weight, reps, volume
    """
    lines = open_workout_file(file_path)
    workout_date = get_workout_date(file_path)
    
    all_sets = []
    current_exercise = None
    set_number = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if this line is one of our tracked exercises
        if line_stripped in exercise_names:
            current_exercise = line_stripped
            set_number = 0
            continue
        
        # If we're tracking this exercise and hit a set line
        if current_exercise:
            if line.startswith("Set") and "kg" in line:
                set_number += 1
                set_data = extract_set_data(line)
                all_sets.append({
                    "date": workout_date,
                    "exercise": current_exercise,
                    "set_number": set_number,
                    "weight": set_data["weight"],
                    "reps": set_data["reps"],
                    "volume": set_data["volume"]
                })
            elif line.startswith("Set") and "reps" in line:
                set_number += 1
                parts = line.split(" : ")
                reps = int(parts[1].split(" ")[0])
                volume = bodyweight * reps
                all_sets.append({
                    "date": workout_date,
                    "exercise": current_exercise,
                    "set_number": set_number,
                    "weight": bodyweight,
                    "reps": reps,
                    "volume": volume
                })
            elif line_stripped == "":
                # Blank line means exercise is over
                current_exercise = None
    
    return all_sets


def build_exercise_dataframe(exercise_names, bodyweight=80):
    """
    Builds a complete dataframe of all sets for tracked exercises across all workout files.
    
    Parameters:
    - exercise_names: list of exercise names to track
    - bodyweight: your bodyweight for bodyweight exercises
    
    Returns:
    - pandas DataFrame with columns: date, exercise, set_number, weight, reps, volume
    """
    workout_files = get_all_workout_files()
    all_data = []
    
    for file in workout_files:
        sets = extract_exercise_sets(file, exercise_names, bodyweight)
        all_data.extend(sets)
    
    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    return df