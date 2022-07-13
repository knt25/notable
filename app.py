from flask import Flask, abort, render_template, request
import pandas as pd
import datetime

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

if __name__ == "__main__":
    app.run()

appts = pd.read_csv('appointments.csv')
minute_intervals = [00, 15, 30, 45]

@app.route('/get-doctors', methods = ['GET'])
def getDoctors():
    data = pd.read_json('doctors.json')
    return data["doctors"].to_dict()

@app.route('/get-appointments', methods = ['GET'])
def getAppointments():

    doctorID = request.args.get('doctorID')
    date = request.args.get('date')

    appt = appts[appts['doctorID'] == int(doctorID)] #query data based on doctor ID and date
    appt = appt[appt['date'] == date]  
    if len(appt) != 0:
        return appt.to_dict()
    else:
        return ("No appointments found")

@app.route('/delete-appointments', methods = ['DELETE'])
def deleteAppointments():
    id = request.args.get('deleteID')
    index = appts.index[(appts["ID"] == int(id))]
    if len(index) == 0:
        return "No existing appointments with this ID"
    print(index)
    appts.drop(index,axis=0,inplace=True) #drop appt with given id
    appts.to_csv('temp_appointments.csv', mode='w', header=True, index=False) #write updated to temp file
    return 'Your appointment has been deleted!'

@app.route('/post-appointments', methods = ['POST'])
def postAppointments():
    global appts 

    first_name = request.form.get('fname')
    last_name = request.form.get('lname')
    date = request.form.get('date')
    time = request.form.get('time')
    kind = request.form.get('kind')
    doctorID = request.form.get('doctorID')

    my_time = datetime.time.fromisoformat(time)
    if(my_time.minute not in minute_intervals):
        return "Appointments can only start at 15 minute intervals"

    appt = appts[appts['doctorID'] == int(doctorID)] #query data based on doctor, time, and date
    appt = appt[appt['date'] == date]
    appt = appt[appt['time'] == time]
   
    if(len(appt) >= 3):
        return "There are already 3 appointments scheduled with this doctor at this time and date. Please choose a different time."

    id = appts.loc[appts.index[-1], 'ID'] + 1 #get ID of last appointment and increment
    data = [[id, first_name, last_name, date, time, kind, doctorID]]
    new_appt = pd.DataFrame(data, columns=['ID','patient_first','patient_last','date','time','kind','doctorID'])

    appts.to_csv('temp_appointments.csv', mode='w', header=True, index=False) #write existing appointments to temp file
    new_appt.to_csv('temp_appointments.csv', mode='a', header=False, index=False) #append new appointment to temp file

    appts = pd.read_csv('temp_appointments.csv') #update appts

    return 'Your appointment has been created!'