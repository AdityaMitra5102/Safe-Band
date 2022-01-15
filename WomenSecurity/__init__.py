import logging
import azure.functions as func
from flask import * 
import pyodbc
import uuid
import datetime
import requests
#from sendgrid import SendGridAPIClient
#from sendgrid.helpers.mail import Mail


app= Flask(__name__)
server = 'tcp:safeband.database.windows.net'
database = 'SECURITY'
username = 'women_safety'
password = '{Anisha@2010}'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                      server+';DATABASE='+database+';UID='+username+';PWD=' + password)
cursor = cnxn.cursor()


def createTable():
    try:
        cursor.execute(
            "CREATE TABLE [SECURITY](UID VARCHAR(30) , NAME VARCHAR(40) ,EMAIL VARCHAR(30)) ")
        cursor.commit()
    except:
        pass

def createCasesTable():
    try:
        cursor.execute(
            "CREATE TABLE [cases](UID VARCHAR(30) , Location VARCHAR(50), ts VARCHAR(30)) ")
        cursor.commit()
    except:
        pass


def getEMAIL_BY_UID(UID):
        try:
            command = 'SELECT EMAIL FROM [SECURITY] WHERE UID=?'
            cursor.execute(command, UID)
            retValue = cursor.fetchone()[0]
            cursor.commit()
            return retValue
        except:
            return "Error"
			
			
def getNAME_BY_UID(UID):
        try:
            command = 'SELECT NAME FROM [SECURITY] WHERE UID=?'
            cursor.execute(command, UID)
            retValue = cursor.fetchone()[0]
            cursor.commit()
            return retValue
        except:
            return "Error"

def addCases(UID, LOC):
    currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ct=str(currenttime)
    try:
        command = 'INSERT INTO [cases] VALUES(?,?,?)'
        cursor.execute(command,UID,LOC,ct)
        cursor.commit()
    except:
        createCasesTable()
        command = 'INSERT INTO [cases] VALUES(?,?,?)'
        cursor.execute(command,UID,LOC,ct)
        cursor.commit()

def addUser(UID, NAME, EMAIL):
    try:
        command = 'INSERT INTO [SECURITY] VALUES (?,?,?)'
        cursor.execute(command, UID, NAME, EMAIL)
        cursor.commit()
    except:
        createTable()
        try:
            command = 'INSERT INTO [SECURITY] VALUES (?,?,?)'
            cursor.execute(command, UID, NAME, EMAIL)
            cursor.commit()
        except:
            pass

def genUid():
	return str(uuid.uuid4().fields[-1])[:5]


def sendEmail(eml, name, loc):
    #message = Mail(
    #    from_email='women2780@gmail.com',
    #    to_emails=eml,
    #    subject=name+' is in a danger.',
    #    html_content=name+' is in a danger. Location https://google.com/maps?q='+loc)
    #try:
    #    sg = SendGridAPIClient(
    #        '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')
    #    response = sg.send(message)
    #except Exception as e:
    #    pass
    payload={'eml':eml, 'nm': name, 'loc': loc}
    r=requests.get('http://20.106.248.18/',params=payload)
    print(r.text)

def sendTelegram(name, loc):
    url='https://api.telegram.org/bot5065626365:AAGaixqWH8xAGaRZpIP-mLykCgz8DDL7YdY/sendMessage'
    msg=name + ' is in danger. http://www.google.com/maps/place/'+loc
    chatid='-601451858'
    param={'chat_id':chatid, 'text':msg}
    r=requests.post(url,data=param)
    print(r.text)

@app.route("/api/WomenSecurity/", methods=["GET","POST"])
def root():
	page=request.args.get('page')
	if page=='index':
		return render_template('index.html')
	if page=='Register':
		return render_template('Register.html')
	if page=='nfc':
		name = request.form['name']
		email = request.form['eml']
		uid = genUid()
		addUser(uid,name,email)
		return render_template('nfc.html',uid=uid)
	if page=='error':
		return render_template('error.html')
	if page=='success':
		return render_template('success.html')
	if page=='thank':
		location=request.args.get('loc')
		id=request.args.get('id')
		nm=getNAME_BY_UID(id)
		eml=getEMAIL_BY_UID(id)
		addCases(id,location)
		sendEmail(eml,nm,location)
		sendTelegram(nm,location)
		return render_template('thank.html')
	if page=='report':
		return render_template('report.html')	

main = func.WsgiMiddleware(app).main

