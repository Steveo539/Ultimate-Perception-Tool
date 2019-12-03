import json
# TODO: allow the functions to pass the parsed information to the database


# helper function that takes in a list of dicts representing each individual employee, and returns a list of the employees name and their emails
def parse_data(data: []):
    # dictionary that maps each employee ID: int to a tuple (employee full name: str, email: str)
    employee_data = {}
    for employee in data:
        employee_data[employee["employeeId"]] = (employee["firstName"] + " " + employee["lastName"], employee["email"])

    return employee_data


# helper function that takes in a file path to a json file and uses python's JSON module to parse the file which is returned
def import_json(file_path: str):
    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)

    return json_data


if __name__ == "__main__":
    print(parse_data(import_json("../../CustomerData/Flipchart-employees.json")))