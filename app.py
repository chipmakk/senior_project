#python imports 
from flask import Flask, render_template, redirect, url_for, request

#define the application
app = Flask(__name__)

#App Home page 
@app.route ('/')
def home():
	return render_template("index.html")
#=========================================================================================
#Admin login page w/ form 
@app.route("/adminlogin", methods =['GET','POST'])
def adminlogin():
	error = None
	if request.method == 'POST':
		#if uname and pw does not equal specified value then error is prompted 
		if request.form['username'] !='admin' or request.form ['password'] !='admin':
			error = 'Invalid Credentials. Try again'
		#if uname and pw does equal specified value then redirect to Admin option page
		else: 
			return redirect(url_for('admin'))
	#renders adminlogin forms
	return render_template('adminlogin.html', error=error)

#admin option page with 3 functions 
@app.route("/admin", methods = ['GET','POST'])
def admin():
	return render_template('adminopt.html')

#=========================================================================================
#user Home login page linked to capture profile page 
@app.route("/user", methods =['GET','POST']) 
def add():
	return render_template('facelogin.html')
	
#=========================================================================================
#Admin --> new user page with 3 functions one for linux acct - image repo-- premissions
@app.route("/new", methods =['GET','POST'])
def new():
	return render_template('addusers.html')
	
#Form for adding a new linux user html
@app.route("/linuxuser")
def my_form():
	return render_template('linuxuser.html')

  

  #end of app
if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')

