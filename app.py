import requests
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
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

            login = auth.sign_in_with_email_and_password(username , password )
            
            loginSession = login #sets the global to be passed in  to the render template
            
            userInfo = db.child('users').child(login['localId']).child('zipcode').get()
            userVals = userInfo.val()
            weatherInfo = []
            interVal = None
            if userVals != None:
                for i in userVals:
                    interVal = getWeatherByZipcode(i)
                    weatherInfo.append(interVal)

                return render_template('home.html', loginID = loginSession, len = len(weatherInfo), result = weatherInfo )
            else:
                return render_template('home.html', loginID = loginSession)
           

    return render_template('login.html', error = error)

@app.route('/register', methods = ['GET', 'POST'])
def register( ):
    from app import loginSession
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
    from app import loginSession
    longitude=""
    latitude =""
    name = ""
    if request.method == 'POST':
        if request.form[ 'submit_button'] == 'Submit':
           
           zip = request.form['inputZip']

          
           geoLoc = getZipGeoLoc(zip)
           newTemp = getWeatherByGeoLocation(geoLoc[1], geoLoc[0])
           print("cool story bro")
           if (geoLoc != False):
                longitude = geoLoc[1]
                latitude = geoLoc[0]
           else:
               longitude = ""
               latitude = ""
           if (newTemp != False):
            TempAll.append(newTemp)
            print(longitude,latitude)
            updateIndex(TempAll, longitude, latitude)

        if request.form[ 'submit_button']== 'FindZip':
            city =request.form['inputCity']
            state =request.form['inputState']
            resZipcode = getZipcode( city , state)
            stringResZipcode = str(resZipcode)
            print(stringResZipcode)
            return updateZipcodeList(stringResZipcode)
    
    return render_template('home.html', loginID = loginSession, len = len(TempAll),result = TempAll)

def updateIndex(TempAll, longitude, latitude):
    return render_template('home.html', loginID = loginSession, len = len(TempAll),  result = TempAll, contentLongit = longitude, contentLat =  latitude)

def updateZipcodeList(Zipcode):
    return render_template('home.html', loginID = loginSession, len = len(TempAll), result = TempAll,  zipcode = Zipcode)

def logedINWithToken():
     return render_template('home.html', loginID = loginSession, len = len(TempAll), result = TempAll,  zipcode = Zipcode)







if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)



