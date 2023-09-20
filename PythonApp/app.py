# Import file to link to DB. 
import appDB
# Import to use datetime functionality in this file.
import datetime
# import packages to use with neo4j.
from neo4j import GraphDatabase
from neo4j import exceptions

# driver will be a global variable for connecting to neo4j. 
driver = None


# Function to connect to neo4j database.
def connect():
    global driver
    uri = "neo4j://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4j"), max_connection_lifetime=1000)


# Main function for app.
def main():
    header = menu_header()
    # will continue to display menu and user choice 
    while True:
        display = display_menu()
        choice = input("Choice: ")

        if (choice == "1"):
            choice1 = choice_one()
  
        elif (choice == "2"):
            choice2 = view_sals()
  
        elif (choice == "3"):
            choice3 = emps_born()

        elif (choice == "4"):
            choice4 = add_emp_to_db()

        elif (choice == "5"):
            choice5 = get_did_and_budget()

        elif (choice == "6"):
            choice6 = add_mgr_to_dept()

        elif (choice == "7"):
            choice7 = view_depts()

        elif (choice == "x"):
            break;
        # keep displaying menu until 1-7 or x is entered.
        else:
            display_menu()  


# Choice 1 function to find all employees and dept names in groups of 2.
def choice_one():
    offset = 0
    empDept = appDB.find_emp_dept(offset)
    # Loop through results to give each name and dept.
    for emp in empDept:
        print(emp["name"], "|", emp["dept"])
    key = input("--Quit (q)--")
    # loop to add 2 to offset until q is entered. 
    while key != "q":
        # add 2 to offset to show next 2 names each time.
        offset += 2
        empDept = appDB.find_emp_dept(offset)
        for emp in empDept:
            print(emp["name"], "|", emp["dept"])
        key = input("--Quit (q)--")


# Choice 2 function to view min, avg and max salary of choice employee ID.
def view_sals():
    empID = input("Enter EID: ")
    # calls sql code from DB in appDB.py
    empSals = appDB.find_sals(empID)
    # check empID is valid.
    check_empID = appDB.check_eid_exists(empID)
    # the empID check is not empty - loop to access each sal details from empSals. 
    if (len(check_empID)) != 0:
        for sal in empSals:
            print("")
            print("Salary Details For Employee: ", empID)
            print("-" * 28)
            print("Minimun", (""*25), "|", (""*10), "Average", (""*25),"|", (""*10), "Maximum")
            print(sal["minS"], "|", sal["avgS"], "|", sal["maxS"])
            # exit function breaks out of the current one. 
            exit()
    else:
        print("")
        print("Salary Details For Employee: ", empID)
        print("-" * 28)
        print("Minimun", (""*25), "|", (""*10), "Average", (""*25),"|", (""*10), "Maximum")
        exit()


# Choice 3 function to return emp details from month entered.
def emps_born():
    month = input("Enter Month: ").casefold()
    month = mtNum(month)
    empBorn = appDB.find_emp_born(month)
    for emp in empBorn:
        print(emp["eid"], "|", emp["name"], "|", emp["dob"])
    exit()


# Choice 3 function to validate/change month to number.
def mtNum(month): 
    while True:
        try:
            # Checks if digit and valid month number.
            if month.isdigit():
                month = datetime.datetime.strptime(month, "%m").month
                return month
            # Checks if valid month abbrev and converts to month number.
            else: 
                month = datetime.datetime.strptime(month, "%b").month
                return month   
        except:
            # Keeps asking for user input if try fails.
            month = input("Enter Month: ").casefold()


# Choice 4 function to add employee to database. 
def add_emp_to_db():
    empID = input("EID : ")
    name = input("Name : ")
    dob = input("DOB : ")
    depID = input("Dept ID : ")
    appDB.add_employee(empID, name, dob, depID) 
    exit()


# Choice 5 function to return name and budget of dept managed by eid entered. 
def get_did_and_budget():
    # connect to neo4j database 
    connect()
    user_eid = input("Enter EID: ")
    # call function with user input to get neo4j manages parameter
    with driver.session() as session:
        all_depts = session.read_transaction(get_dep_managed, user_eid)
        print("")
        print("Departments Managed by: ", user_eid)
        print("------------------------")
        print("Department | Budget")
        # Loop through depts
        for dep in all_depts:
            # call sql cmd for each dep 
            bud = appDB.get_dep_budget(dep)
            # loop to get every budget in each dep
            for every in bud: 
                # format to allow for commas in number when printed.
                print (dep, "|",  "{:,}".format(every["budget"]))
        exit()


# Choice 5 function to find departments managed by eid from neo4j database. 
def get_dep_managed(tx, user_eid):
    # neo4j query to find all depts managed by user_eid
    query = "MATCH (e:Employee{eid:$eid})-[r:MANAGES]->(d:Department) RETURN d.did"
    depts = []
    results = tx.run(query, eid=user_eid)
    for result in results:
        depts.append(result["d.did"]) # append to array and if empty doesn't print anything out below **** 
    # will return names to value var below
    return depts


# Choice 6 function to add a manager to a department.
# Check constraints in neo db.
def check_constraints(tx):
    # Checks if constraint exists for uniqie eids and dids and create if they don't exist.
    query1 = "CREATE CONSTRAINT one_did IF NOT EXISTS ON (d:Department) ASSERT d.did IS UNIQUE"
    query2 = "CREATE CONSTRAINT one_eid IF NOT EXISTS ON (e:Employee) ASSERT e.eid IS UNIQUE"
    # Run the check
    tx.run(query1)
    tx.run(query2)


# Neo cmd to add mgr.
def add_managerToDep(tx, eid, did):
    query = """
                MERGE (e:Employee{eid:$eid})
                MERGE(d:Department{did:$did})
                CREATE (e)-[r:MANAGES]->(d)
            """
    tx.run(query, eid=eid, did=did)


# Add to neo database.
def add_to(eid, did):
    with driver.session() as session: 
        add_to_db = session.write_transaction(add_managerToDep, eid, did)
        print("Employee", eid, "now manages Department", did)
  
  
# Check eid/did is valid from sql.
def check_eid_did(eid, did):
    valid_eid = appDB.check_eid_exists(eid)
    valid_did = appDB.check_did_exists(did)
    if (len(valid_eid)) and (len(valid_did)) != 0:
        return True      
    else:
        print("Employee", eid, "does not exist")
        print("Department", did, "does not exist") 
        print("")   
        #call origional function again.
        add_mgr_to_dept()     


 # Check if managed in neo.
def get_did_already_managed(tx):
    # neo4j query to find deps already managed.
    query = "MATCH(d)<-[r:MANAGES]-(e) RETURN d.did"
    depts = []
    results = tx.run(query)
    for result in results:
        depts.append(result["d.did"])
    return depts


# Get eid for did already managed from neo.
def get_eid_of_did_already_managed(tx, did):
    query = "MATCH(d:Department{did:$did})<-[r:MANAGES]-(e:Employee) RETURN e.eid"
    emp_who = []
    values = tx.run(query, did=did)
    for value in values:
        emp_who.append(value["e.eid"])
    return emp_who


# Check with neo db if managed.
def check_if_managed(eid, did):
    with driver.session() as session:   
        constraints = session.write_transaction(check_constraints)
        already_managed = session.read_transaction(get_did_already_managed)
        emps_of_dep_managed = session.read_transaction(get_eid_of_did_already_managed, did)
        #print(already_managed)
        for e in emps_of_dep_managed:
            if (len(emps_of_dep_managed) != 0):
                print("Department", did, "is already managed by Employee", e)
                exit()


# Choice 6 - main function.
def add_mgr_to_dept():
    connect()
    eid = input("Enter EID: ")
    did = input("Enter DID: ")  
    # Check if eid/dids are valid 
    valid = check_eid_did(eid, did)
    # If valid check if dept already managed. 
    if valid is True:
        final_check = check_if_managed(eid, did)
        # Will run unless final_check fails.
        time_to_add = add_to(eid, did)
        exit()


# Choice 7 function to view details of all departments
def view_depts():
    depts_list = []
    if (len(depts_list) == 0):
        allDepts = appDB.view_all_Depts()
        print("Did", "|", "Name", "|", "Location", "|", "Budget")
        for dep in allDepts:
            print(dep["did"], "|", dep["name"], "|", dep["lid"], "|", dep["budget"])
            depts_list.append(allDepts)
    else:
        print("Did", "|", "Name", "|", "Location", "|", "Budget")
        for dep in depts_list:
            print(dep["did"], "|", dep["name"], "|", dep["lid"], "|", dep["budget"])  


# Function for main menu - displays choices for user.
def display_menu():

    print("MENU")
    print("=" * 4)
    print("1 - View Emlpoyees & Departments") 
    print("2 - View Salary Details")
    print("3 - View by Month of Birth")
    print("4 - Add New Employee")
    print("5 - View Departments managed by Employee")
    print("6 - Add Manager to Departments") 
    print("7 - View Departments")
    print("x - Exit Application")


def menu_header():
    print("")  
    print("Employees")
    print("---------")
    print("")


# Executes when main function is read.
if __name__ == "__main__":
	main()