#python imports 
from flask import Flask, render_template, redirect, url_for, request
import os
import os.path
from train import trainprog 
import subprocess 
import sys
import glob
import select
import cv2
import config
import face
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
#Iniates the addlinuxuser.sh script and passes values from form 
@app.route('/linuxuser', methods=['POST'])
def my_form_post():
	username = request.form['uname']
	x = username
	passwd = request.form['pass']
	return str(subprocess.check_call(["./shell/addlinuxuser.sh", x,passwd], shell=False)) and redirect(url_for('new'))
#==================================================================================================
 #Remove linux user html
@app.route('/removelinuxuser', methods=['GET'])
def remove_form():
	return render_template('remove.html')

#Iniates the removelinux.sh script and passes values from the form  
@app.route('/removelinuxuser', methods=['POST'])
def remove_form_post():
	username = request.form['uname']
	x = username
	passwd = request.form['pass']
	return str(subprocess.check_call(["./shell/removelinuxuser.sh", x,passwd], shell=False)) and redirect(url_for('admin'))
#==========================================================================================

#Admin add new user function to positive image repo 
@app.route("/capture", methods =['GET','POST'])
def admincapture():	
	if request.method == 'GET':
		

		# Prefix for positive training image filenames.
		POSITIVE_FILE_PREFIX = 'positive_'
		camera = config.get_camera()
		# Create the directory for positive training images if it doesn't exist.
		if not os.path.exists(config.POSITIVE_DIR):
			os.makedirs(config.POSITIVE_DIR)
		# Find the largest ID of existing positive images.
		# Start new images after this ID value.
		files = sorted(glob.glob(os.path.join(config.POSITIVE_DIR, 
			POSITIVE_FILE_PREFIX + '[0-9][0-9][0-9].pgm')))
		count = 0
		if len(files) > 0:
			# Grab the count from the last filename.
			count = int(files[-1][-7:-4])+1
		
		while True:
			
			print 'Capturing image...'
			
			image = camera.read()
			# Convert image to grayscale.
			image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
			# Get coordinates of single face in captured image.
			result = face.detect_single(image)
			if result is None:
				print 'Could not detect single face!  Check the image in capture.pgm' \
						  ' to see what was captured and try again with only one face visible.'
				return 'Could not detect single face!  Check the image in capture.pgm' \
						  ' to see what was captured and try again with only one face visible.'
				break
				#continue
			x, y, w, h = result
				# Crop image as close as possible to desired face aspect ratio.
				# Might be smaller if face is near edge of image.
			crop = face.crop(image, x, y, w, h)
				# Save image to file.
			filename = os.path.join(config.POSITIVE_DIR, POSITIVE_FILE_PREFIX + '%03d.pgm' % count)
			cv2.imwrite(filename, crop)
			print 'Found face and wrote training image', filename
			return 'Found face and wrote training image'
			
			if True:
				print"succesful capture"
				delay() 
			if True: 
				return redirect(url_for('/new'))



			#<----*****THis count will need to be edited --> 
			count += 1

			if count >4:
				break
#===========================================================================================================
#permissions
@app.route('/permissions')
def permissions():
	return render_template('permissions.html')

@app.route('/permissions',methods=['POST','GET'])
def permissions_post():
	username = request.form['username']
	if request.form["submit"] == 'levela':
		return str(subprocess.check_call(["./shell/levela.sh", username], shell=False)) and redirect(url_for('permissions'))
	elif request.form["submit"] == 'levelb':
		return str(subprocess.check_call(["./shell/levelb.sh", username], shell=False)) and redirect(url_for('permissions'))
	elif request.form["submit"] == 'levelc':
		return str(subprocess.check_call(["./shell/levelc.sh", username], shell=False))	and redirect(url_for('permissions'))
#=======================================================================================

#Runs the Train Data program -->sends admin to admin logout screen --> need to pass error message from train data prog..
@app.route("/trainprog", methods = ['GET',"POST"])
def train():
	if request.method == 'GET':
		trainprog()
		return render_template('train.html')

#User login/ recog function face regonization 
@app.route("/acct", methods = ['GET',"POST"])
def comp():
	#import cv2
	#import config
	#import face
	# Load training data into model
	print 'Loading training data...'
	model = cv2.createEigenFaceRecognizer()
	model.load(config.TRAINING_FILE)
	print 'Training data loaded!'
	# Initialize camera.
	camera = config.get_camera()
	print 'Capturing Profile...'
	
	while True:
			image = camera.read()
				# Convert image to grayscale.
			image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
				# Get coordinates of single face in captured image.
			result = face.detect_single(image)
			if result is None:
				print 'Could not detect one face!  Check the image capture.pgm' 
				return "User Not Detected"
				
				break
			x, y, w, h = result
				# Crop and resize image to face.
			crop = face.resize(face.crop(image, x, y, w, h))
				# Test face against model.
			label, confidence = model.predict(crop)
			print 'Predicted {0} face with confidence {1} (lower is more confident).'.format(
					'POSITIVE' if label == config.POSITIVE_LABEL else 'NEGATIVE', 
					confidence)
			#user_login for the redirect refers to the def user_login not /user_login
			
			#return redirect(url_for('user_login'))

			if label == config.POSITIVE_LABEL and confidence < config.POSITIVE_THRESHOLD:
				
					
				break
					
			else:
				print 'Did not recognize face!'
				return 'User Not Accepted !'

#User login page after face recgonize 
#@app.route('/user_login', methods=['GET','POST'])
#def user_login():
	#return str(subprocess.check_call(["./shell/userlogin.sh"], shell=False))

#end of app
  #end of app
if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')

