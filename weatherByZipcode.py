
import requests
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from WeatherApiKey import API_KEY
def getWeatherByZipcode(zipcode):
    
    country_code = 'us'
   # zipcod is  passed as argument
    
    # call API and convert response into Python dictionary
    url = f'http://api.openweathermap.org/data/2.5/weather?zip={zipcode},{country_code}&appid={API_KEY}'
    response = requests.get(url).json()
    
    # error like unknown zipcode, inavalid api key
    if response.get('cod') != 200:
        message = response.get('message', '')
        return  False

    current_temperature = response.get('main', {}).get('temp')
    current_feels_like = response.get('main', {}).get('feels_like')
    current_temp_min= response.get('main', {}).get('temp_min')
    current_temp_max = response.get('main', {}).get('temp_max')
    current_temp_pressure= response.get('main', {}).get('pressure')
    current_temp_humidity= response.get('main', {}).get('humidity')
    current_city = response.get('name')
    if current_temperature:
        current_temperature_Fahrenheit = round(current_temperature  -255.372 , 2)
        current_feels_like_Fahrenheit = round( current_feels_like -255.372 , 2)
        current_temp_min_Fahrenheit = round(current_temp_min  -255.372 , 2)
        current_temp_man_Fahrenheit = round(current_temp_max -255.372 , 2)
        
       # stringDes = str(Current_des)
        stringTemp= str(current_temperature_Fahrenheit)
        stringFL= str(current_temperature_Fahrenheit)
        stringMin= str(current_temperature_Fahrenheit)
        stringMax= str(current_temperature_Fahrenheit)
        stringPress = str(current_temp_pressure)
        stringHum = str(current_temp_humidity)
        city = str(current_city)
        print(city)
        return """ <div class="col-lg-3 col-md-6 mb-4">
    <div class="card h-100">

    
        <div class="card-body">
            <h3 class="card-title">""" +city+"""</h3>
           
            <p class="card-text"> Temp: """ +stringTemp+ """  F </p>
            <p class="card-text"> Temp Feels Like: """ +stringFL+ """  F </p>
            <p class="card-text"> Temp min: """ +stringMin+ """  F </p>
            <p class="card-text"> Temp Max: """ +stringMax+ """  F </p>
            <p class="card-text"> Pressure: """ +stringPress+ """   </p>
            <p class="card-text"> Humidnity: """ +stringHum+ """   </p>
        </div>
        <div class="card-footer">
            <a href="#" class="btn btn-primary">Find Out More!</a>
        </div>
    </div>
 
</div>"""
    else:
        return False
