# All SQL Commands for app.py here. 

# Connects MySQL database server from Python
import pymysql


# Choice 1: Function to show list of emp names and depts in groups of 2.
def find_emp_dept(offset):
    #Connect to db. 
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    # sql cmd.
    sql = """
            SELECT e.name as name, d.name as dept
            FROM employee e
            INNER JOIN dept d
            ON e.did = d.did
            ORDER BY d.name, e.name ASC
            LIMIT 2 OFFSET %s;
          """     
    # get cursor, execute cmd with offet and return.     
    with db:
        cursor = db.cursor()  
        cursor.execute(sql, (offset))
        return cursor.fetchall()


# Choice 2: Function to find salary details from DB.
def find_sals(empID):   
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    # sql command
    sql = """
            SELECT format(min(s.salary), 2) as minS, format(avg(s.salary), 2) as avgS, format(max(s.salary), 2) as maxS
            FROM salary s
            INNER JOIN employee e
            ON s.eid = e.eid
            WHERE s.eid like %s 
          """ 
    with db:
        cursor = db.cursor()    
        cursor.execute(sql, (empID))
        return cursor.fetchall()       
        
# Choice 2: Function to return the eid if it's like the empID. 
def check_eid_exists(empID):
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT eid FROM employee WHERE eid LIKE %s"  
    with db:
        cursor = db.cursor() 
        cursor.execute(sql, (empID))
        return cursor.fetchall()
    

# Choice 3: Function to find emp info from month born entered.
def find_emp_born(month):
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    # sql cmd.
    sql = """
            SELECT eid, name, dob
            FROM employee
            WHERE month(dob) = %s
          """
    with db:
        cursor = db.cursor() 
        cursor.execute(sql, (month))
        return cursor.fetchall()    
    

# Choice 4: Function to add employee to database with exceptions. 
def add_employee(empID, name, dob, depID): 
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    # sql cmd
    sql = "INSERT INTO employee VALUES (%s, %s, %s, %s)"
    with db:
        try: 
            cursor = db.cursor()
            cursor.execute(sql, (empID, name, dob, depID))
            db.commit()
            if True:
                print("")
                print("Employee sucessfully added")
        # error if primary key already exists.
        except pymysql.err.DataError as e:
            print("*** ERROR ***: ", empID, "already exists")
        # error if invaid date format.
        except pymysql.err.OperationalError as e:
            print("*** ERROR ***: Invalid DOB: ", dob)
        # error if dep doens't exist.
        except pymysql.err.IntegrityError as e:
            print("*** ERROR ***: Department ", depID, "does not exist")


# Choice 5: Function to get budget of dept managed by eid entered. 
def get_dep_budget(all_depts):
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    # sql cmd
    sql = """
            SELECT d.budget as budget
            FROM dept d
            WHERE d.did LIKE %s
          """ 
    with db:
        cursor = db.cursor()  
        cursor.execute(sql, (all_depts))
        return cursor.fetchall()  


# Choice 6: Function to validate eid and did.
# Get eid from db if same as user input and return.
def check_eid_exists(eid):
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT eid FROM employee WHERE eid LIKE %s"  
    with db:
        cursor = db.cursor() 
        cursor.execute(sql, (eid))
        return cursor.fetchall()

# Get eid from db if same as user input and return.
def check_did_exists(did):
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT did FROM dept WHERE did LIKE %s" 
    with db:
        cursor = db.cursor() 
        cursor.execute(sql, (did))
        return cursor.fetchall()


# Choice 7:  Function to read all department details from sql.
def view_all_Depts():
    db = pymysql.connect(host="localhost", user="root", password="root", db="employees", cursorclass=pymysql.cursors.DictCursor) 
    # sql command
    sql = "SELECT * FROM dept" 
    with db:
        cursor = db.cursor()  
        cursor.execute(sql)
        return cursor.fetchall()  