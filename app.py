import requests
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, url_for, session
from flask_session import Session
from geoLocationByZip import getZipGeoLoc
from flask_mysqldb import MySQL
import json
import os
import sqlite3
from GetTemp import GetTemp
from ValidateCity import ValiddateCity
from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import Length, AnyOf
from oauthlib.oauth2 import WebApplicationClient
from GetZipCode import getZipcode
from weatherByGeoLocation import getWeatherByGeoLocation
from collections import OrderedDict
from weatherByZipcode import getWeatherByZipcode


from getpass import getpass
from firebase_admin import credentials 
from FireConfig import firebaseConfig # imports the firebase API key <<NOT SAFE FOR GITHUB>>
import pyrebase

loginSession = False
#on how to retrieve data
# userInfo = db.child('users').child(login['localId']).child('zipcode').get()
#myZipcodeList = userInfo.val()
#for i in myZipcodeList

#how to enter in data 
#zipcodearr = [9999,9999,4444]
# data = db.child('users').child(login['localId']).child('zipcode').set(zipcodeArray)


firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

#Temp1 = GetTemp("Dallas")
#Temp2 = GetTemp("Denver")
TempAll = {}

app = Flask(__name__)

sess = Session()
app.config.from_object(__name__)

#auth = firebase.auth()
#database = firebase.database()
@app.route('/login', methods = ['GET', 'POST'])
def login(  ):
    error = None
    if request.method == "POST":
        print("you have enter login")
        if request.form ['submit'] == 'signin':
            print("To be developed later")
            username = request.form['username'] #not the safest methond ... 
            password = request.form['password']

            try:
                auth.sign_in_with_email_and_password(username , password )
            except:
                error = 'login fail'
                print(' login fail')
                return render_template('login.html', error = error)

            loginInfo = auth.sign_in_with_email_and_password(username , password )
            session['logininfo'] = loginInfo
            return redirect(url_for('.logedinWithToken'))

            
           

    return render_template('login.html', error = error)

@app.route('/register', methods = ['GET', 'POST'])
def register( ):
    
    message = None
    if request.method == "POST":
        print("you have enter register")


        if request.form ['submit'] == 'submitRegister':
            newEmail = request.form['userEmail']
            password1 = request.form['password1']
            password2 = request.form['password2'] #unsafe i know 
            emailChars = ['@', '.']

            if( '@' in newEmail and '.' in newEmail ): # checks if email is in valid formant 
                print("clear")
            else:
                message = "not a vaild email!"
                return render_template('register.html', message = message)

            if(password1 != password2): # checks if passwords mastch
                message = "passwords do not match!"
                return render_template('register.html', message = message)
            try:
                tempUser =  auth.create_user_with_email_and_password(newEmail, password1)
                auth.send_email_verification(tempUser['idToken'])
                message = "please go to your eamil to verified"
                return render_template('register.html', message = message)
            except:
                print("ERROR HAS OCCURE ")
                message = "email is alreadly in the system"
                return render_template('register.html', message = message)




    return render_template('register.html', message = message)

@app.route('/logout', methods = ['GET', 'POST'])
def logout(): #my logout method
    from app import loginSession
    message = None
    if (loginSession == False):
        message = ' you must log in first'
    else:
        message = ' you have loged out! '
        loginSession = False

    return render_template('logout.html', message = message)


      
        

@app.route('/',  methods=['GET', 'POST']) # main page 
def index(): 
    
    
    return render_template('home.html', loginID = loginSession, len = len(TempAll),result = TempAll)

def updateIndex(TempAll, longitude, latitude):
    return render_template('home.html', loginID = loginSession, len = len(TempAll),  result = TempAll, contentLongit = longitude, contentLat =  latitude)

def updateZipcodeList(Zipcode):
    return render_template('home.html', loginID = loginSession, len = len(TempAll), result = TempAll,  zipcode = Zipcode)

@app.route('/LoggedIN',  methods=['GET', 'POST'])
def logedinWithToken():
    print("LOGGED IN")
    login = session.get('logininfo', None)
    userInfo = db.child('users').child(login['localId']).child('zipcode').get()
    userVals = userInfo.val()
    deleteList = []
    weatherInfo = []
    interVal = None

    if request.method == "POST":
        print("listing for the data submit")
       # print(request.form.get['submit'])
        if request.form ['submit_button'] == 'Submit':
            return enterNewZipcode()
        if request.form['submit_button'] == 'FindZip':
            return findZipByCityAndState()
        if request.form['submit_button'] == 'deleteZip':
            print("is this button press? ")
            return deleteZipCodeEntry()



   
    if userVals != None:
        for i in userVals:
            interVal = getWeatherByZipcode(i)
            weatherInfo.append(interVal)
            print('has info')
        return render_template('home.html', loginID = login, len = len(weatherInfo), result = weatherInfo, Zipcodes = userVals )
                               
    else:
        print('no login info')
        return render_template('home.html', loginID = login )

def enterNewZipcode():
    zipcode =""
    message =""
    newZipcode =""
    weatherInfo = []
    login = session.get('logininfo', None)
    userInfo = db.child('users').child(login['localId']).child('zipcode').get()
    userVals = userInfo.val()
    newZipcode = request.form["inputZip"]
    
    print(newZipcode)

    if (newZipcode == None):
        #print(newZipcode)
        message = "zipcode was not entered!"
        return render_template('home.html' )
    else:
        zipcode1 = newZipcode
        newWeatherInfo = getWeatherByZipcode(newZipcode)
        
        if userVals != None:
            for i in userVals:
                interVal = getWeatherByZipcode(i)
                weatherInfo.append(interVal)
                print('has info')
            weatherInfo.append(newWeatherInfo)
            userVals.append(zipcode1)# adding array to be updated to the db 
            db.child('users').child(login['localId']).child('zipcode').set(userVals) #updates the Database
            return render_template('home.html', loginID = login, len = len(weatherInfo), result = weatherInfo, Zipcodes = userVals )
        else:
            print('no previous infomation info')
            userVals = []
            userVals.append(zipcode1)# adding array to be updated to the db 
            weatherInfo.append(newWeatherInfo)
            db.child('users').child(login['localId']).child('zipcode').set(userVals)#updates the Database
            return render_template('home.html', loginID = login, len = len(weatherInfo), result = weatherInfo, Zipcodes = userVals)



def findZipByCityAndState():
    
    state = request.form["inputState"]
    city = request.form["inputCity"]
    zipcode =""
    message = ""
    weatherInfo = []
    if(state == None or city == None):
        print("no city or state was entered")
        message = "no city or state was entered"
        return render_template('home.html' )
    else:
        print("city AND state was entered")
        zipcode = getZipcode(city,state )
        login = session.get('logininfo', None)
        userInfo = db.child('users').child(login['localId']).child('zipcode').get()
        userVals = userInfo.val()
        weatherInfo = []
        interVal = None
        return render_template('home.html', loginID = login, len = len(weatherInfo), result = weatherInfo, zipcode = zipcode )
        


def deleteZipCodeEntry():
    print("delete button has been pushed!")
    targetZip = request.form["ZipList"]
    login = session.get('logininfo', None)
    userInfo = db.child('users').child(login['localId']).child('zipcode').get()
    userVals = userInfo.val()
    print(userVals)
    print(targetZip)
   
    if (targetZip == None):
        message = "no Zipcode was selected"
        return message
    if(targetZip in userVals):
        userVals.remove(targetZip)
        db.child('users').child(login['localId']).child('zipcode').set(userVals)
        userInfo = db.child('users').child(login['localId']).child('zipcode').get()
        userVals = userInfo.val()
        weatherInfo = []
        if userVals != None:
            for i in userVals:
                interVal = getWeatherByZipcode(i)
                weatherInfo.append(interVal)
                print('has info')
            return render_template('home.html', loginID = login, len = len(weatherInfo), result = weatherInfo )
        else:
            print('no login info')
            return render_template('home.html', loginID = login )
    else:
        print ("not in the list")
        message = " not in the list"
        return message 


     





if __name__ == '__main__':
    app.secret_key='secret123'
    app.config['SESSION_TYPE'] = 'filesystem'
    
    sess.init_app(app)
    app.run(debug=True)






