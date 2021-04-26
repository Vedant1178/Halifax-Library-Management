import flask
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from sqlite3 import Error
import pymysql.cursors

app = flask.Flask(__name__)
app.config["DEBUG"] = True

database = r"api/test.db"



# Simple Functions




@app.route('/allTablesResult')
def allTablesResult():

    sql = "show tables;"

    result = execute(sql)
    return render_template('table.html', result=result)


@app.route('/addNewCustomer')
def addNewCustomer():
    return render_template('addNewCustomer.html')

@app.route('/addNewCustomerProcessing', methods=['POST'])
def addNewCustomerProcessing():
    user=request.form
    _fname = user['fname']
    _lname = user['lname']
    _tnum = user['tnum']
    _email = user['email']
    _dc = user['dc']

    sql = f"select * from customer where fname='{_fname}' AND lname='{_lname}';"
    result = execute(sql, True)
    if len(result)>0:
        #print("ALREADY EXISTS IN DB")
        return redirect(f'/addNewCustomerCondition/{_fname}/{_lname}/{_tnum}/{_email}/{_dc}')
    else:
        #print("DOES NOT EXISTS IN DB")
        return  redirect(f'/addNewCustomerResult/{_fname}/{_lname}/{_tnum}/{_email}/{_dc}')


@app.route('/addNewCustomerCondition/<_fname>/<_lname>/<_tnum>/<_email>/<_dc>')
def addNewCustomerCondition(_fname,_lname,_tnum,_email,_dc):
    user = {}
    user['_fname']=_fname
    user['_lname']=_lname
    user['_tnum']=_tnum
    user['_email']=_email
    user['_dc']=_dc
    tempurl = f"'/addNewCustomerResult/{_fname}/{_lname}/{_tnum}/{_email}/{_dc}'"
    
    return render_template('addNewCustomerCondition.html', tempurl=tempurl)


@app.route('/addNewCustomerResult/<_fname>/<_lname>/<_tnum>/<_email>/<_dc>')
def addNewCustomerResult(_fname,_lname,_tnum,_email,_dc):
    sql = f"INSERT INTO customer (fname, lname, telephone_number, mailing_address, discount) VALUES ('{_fname}', '{_lname}', {_tnum}, '{_email}', {_dc});"
    result=execute(sql, False)
    return '<h1>SUCCESSFULLY INSERTED</h1><br><br><button style="height: 50px; width: 100px" onclick="window.location.href=\'/\'">BACK</button>'




@app.route('/viewTableContents')
def viewTableContents():
    return render_template('viewTableContents.html')

@app.route('/viewTableContentsResult', methods=['POST'])
def viewTableContentsResult():
    user = request.form
    _name = user['name']
    sql = f"select * from {_name};"
    result = execute(sql)
    return render_template('table.html', result=result)


@app.route('/addNewArticles')
def addNewArtiles():
    return render_template('addNewArticles.html')

@app.route('/addNewArticlesResult', methods=['POST'])
def addNewArticlesResult():
    user = request.form
    _name = user['name']
    _age = user['age']
        
    sql = f"INSERT INTO user (age, name) VALUES ({_age}, '{_name}');"
    try:
        result=executemsg(sql, False)
    except pymysql.Error as e:
        temp = "<h1>Failure</h1><br>IntegrityError:  " + str(e)
    else: 
        temp = "<h1>Success</h1>"
    
    return temp + '<br><br><button style="height: 50px; width: 100px" onclick="window.location.href=\'/\'">BACK</button>'


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

def create_connection():
    c = None
    try:
        c = sqlite3.connect(database)
        print(sqlite3.version)
        return c
    except Error as e:
        print(e)


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
    finally:
        if c:
            c.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def execute(sql, isSelect=True):
    # LOCAL DATABASE
    # conn = sqlite3.connect(database)
    
    # REMOTE DATABASE
    conn = pymysql.connect(host='dbcourse.cs.smu.ca',
                            port=3306,
                            user='u53',
                            password='sleptHAVANA10',
                            db='u53',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
    result = None
    
    cursor = conn.cursor()
    if isSelect:
        cursor.execute(sql)
        result = cursor.fetchall()
        print(f"result = {result}")
    else:
        result=cursor.execute(sql)
        #result = conn.insert_id()
        conn.commit()
    
    conn.close()
    return result

def executemsg(sql, isSelect=True):
    # LOCAL DATABASE
    # conn = sqlite3.connect(database)
    
    # REMOTE DATABASE
    conn = pymysql.connect(host='dbcourse.cs.smu.ca',
                            port=3306,
                            user='u53',
                            password='sleptHAVANA10',
                            db='u53',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
    result = None
    result = "Success"
    try:
        with conn.cursor() as cursor:
            if isSelect:
                cursor.execute(sql)
                result = cursor.fetchall()
                print(f"result = {result}")
            else:
                result=cursor.execute(sql)
                
                conn.commit()
    except pymysql.err.IntegrityError as e:
        conn.close()
        result = "" + e
        return result
    else:
        conn.close()
        return result


def start_db():

    # create a database connection
    conn = create_connection()

    # create tables
    if conn is not None:
        user_table_sql = """ CREATE TABLE IF NOT EXISTS user (
                            id integer PRIMARY KEY AUTO_INCREMENT,
                            age integer NOT NULL,
                            name text NOT NULL
                        ); """
        create_table(conn, user_table_sql)
    else:
        print("Error! cannot create the database connection.")

# HTTP functions





# Update user
@app.route('/user', methods=['PUT'])
def put_users():
    user = request.get_json()
    _id = user['id']
    _age = user['age']
    _name = user['name']

    sql = f"UPDATE user SET age = {_age}, name = '{_name}' WHERE id = {_id};"
    execute(sql, False)
    return {}

# List all users
@app.route('/users', methods=['GET'])
def get_users():

    _id = request.args['id'] if 'id' in request.args else 0
    _age = request.args['age'] if 'age' in request.args else 0
    _name = request.args['name'] if 'name' in request.args else ''

    sql = f"""SELECT * FROM user WHERE 
            ({_id} = 0 OR id = {_id}) 
            AND ({_age} = 0 OR age = {_age}) 
            AND ('{_name}' = '' OR UPPER(name) = UPPER('{_name}'));"""
        
    sql = f"select * from user;"

    users = execute(sql)
    return jsonify(users)

# Delete user by id
@app.route('/user/<_id>', methods=['DELETE'])
def delete_users(_id):
    sql = f"DELETE FROM user WHERE id = {int(_id)};"
    execute(sql, False)
    return {}

# LOCAL DATABASE
# start_db()

app.run()
