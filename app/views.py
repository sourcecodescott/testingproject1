"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db
from flask import render_template, request, redirect, url_for, flash, json, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from forms import ProfileForm
from app.models import UserProfile
from werkzeug.utils import secure_filename
import time
import os
import random

###
# Routing for your application.
###

@app.route('/')
def home():
    """ Render website's home page."""
    return render_template('home.html')

@app.route('/profile/', methods=['GET', 'POST'])
def new_profile():
    """ Render a page for adding a user profile """
    
    # Generate form
    form = ProfileForm()
    # Check request type
    if request.method == "POST":
        # Validate form
        if form.validate_on_submit():
            # Get form values
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            username = request.form['username']
            age = request.form['age']
            biography = request.form['biography']
            gender = request.form['gender']
            # Uploads folder
            imageFolder = app.config["UPLOAD_FOLDER"]
            # Get picture file
            imageFile = request.files['image']
            # Check if empty
            if imageFile.filename == '':
                # Store default profile pic in DB
                imageName = "profile_pic.jpg"
            else:
                # Secure file
                imageName = secure_filename(imageFile.filename)
                # Save to uploads directory
                imageFile.save(os.path.join(imageFolder, imageName))
            # Loop to find a unique id
            while True:
                # Generate a random userid
                userid = random.randint(620000000, 620099999)
                # Search for this userid
                result = UserProfile.query.filter_by(userid=userid).first() 
                # Check if not found
                if result is None:
                    # Unique; Exit loop
                    break
            # Generate the date the user was created on
            created_on = timeinfo()
            # Store data in database
            profile = UserProfile(userid,first_name,last_name,username,age,gender,biography,imageName,created_on)
            db.session.add(profile)
            db.session.commit()
            # Flash success message
            flash('Profile has been created', 'success')
            # Redirect to list of profiles
            return redirect(url_for('list_profiles'))
        
    # Display any errors in form
    flash_errors(form)
            
    return render_template('new_profile.html', form=form)

@app.route('/profiles', methods=['GET','POST'])
def list_profiles():
    """ Render a page for viewing a list of all user profiles """
    
    # Get all user profiles from database
    profiles = db.session.query(UserProfile).all()
    
    if request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
        # Initialize a profile list
        profileList = []
        # Get each profile
        for profile in profiles:
            # Create dictionary format
            profileDict = {'username': profile.username, 'userid': profile.userid}
            # Add to list of profiles
            profileList.append(profileDict)
        # Convert list to JSON data
        #jsonProfiles = json.dumps(profileList)
        # Generate JSON output
        return jsonify(users=profileList)
    else:
        if not profiles:
            flash('No users have been added. Add a user below.', 'danger')
            return redirect(url_for('new_profile'))
        return render_template('list_profiles.html', profiles=profiles)
    
    
@app.route('/profile/<userid>', methods=['GET','POST'])
def view_profile(userid):
    """ Render an individual user profile page """
    
    # Search for given userid
    user_profile = UserProfile.query.filter_by(userid=userid).first()
    # Check if found
    if user_profile is not None:
        # Check request type
        if request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
            # Generate JSON output
            return jsonify(userid=user_profile.userid, username=user_profile.username, image=user_profile.image, gender=user_profile.gender, age=user_profile.age, profile_created_on=user_profile.created_on )
        else:
            # Render user's profile page
            return render_template('view_profile.html', user_profile=user_profile)
    else: # Not found
        # Check request type
        if request.method == 'GET':
            
            # Flash error message
            flash('Sorry! User does not exist.','danger')
            
            # Redirect to list of users
            return redirect(url_for('list_profiles'))
           
        elif  request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
            # Return empty set (null)
            return jsonify(user_profile)
    

###
# The functions below should be applicable to all Flask apps.
###

def timeinfo():
    """ Returns the current datetime """
    return time.strftime("%d %b %Y")

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
