import glob
# glob is a Python module that finds files matching a pattern.
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
