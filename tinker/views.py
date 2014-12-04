# python

# flask
from flask import render_template
from flask import session
from flask import send_file

# tinker
from tinker import app


@app.route('/')
def home():
    # index page for adding events and things
    return render_template('home.html', **locals())


@app.route('/about')
def about():
    return render_template('about-page.html', **locals())


@app.route('/get-image/<image_name>')
def get_image(image_name):
    return send_file('images/' + image_name, mimetype='image/png')


@app.route('/test')
def test():
    session.clear()
    return "done"

@app.route("/caleb")
def faculty_bio_caleb_test():
    import csv     # imports the csv module
    import sys      # imports the sys module

    gorirollist = []

    gorirol = open("/Users/ces55739/Desktop/gorirol.csv", 'rb') # opens the csv file
    eann = open("/Users/ces55739/Desktop/eann.csv", 'rb') # opens the csv file
    try:
        reader = csv.reader(gorirol)  # creates the reader object
        gorirollist1, gorirollist2 = zip(*reader)

        reader = csv.reader(eann)  # creates the reader object
        eann1, eann2 = zip(*reader)
    finally:
        gorirol.close()      # closing
        eann.close()      # closing

    ## GORIROL PIDM
    goriroldict = dict()
    for count in range(0,len(gorirollist1)):
        if gorirollist1[count] in goriroldict:
            # append the new number to the existing array at this slot
            goriroldict[gorirollist1[count]].append(gorirollist2[count])
        else:
            # create a new array in this slot
            goriroldict[gorirollist1[count]] = [gorirollist2[count]]

    ## E-Prefs
    eanndict = dict()
    for count in range(0,len(eann1)):
        tempvalues = eann2[count].split(',')
        for value in tempvalues:
            if value=='STUDENT-CAS' or value=='STUDENT-CAS' or value=='STUDENT-GS' or value=='STUDENT-BSOE-TRADITIONAL' or value=='STUDENT-BSOE-DISTANCE' or value=='STUDENT-BSSD-DISTANCE' or value== 'STUDENT-BSSD-TRADITIONAL' or value=='STUDENT-BSSP-TRADITIONAL' or value=='STUDENT-BSSP-DISTANCE' or value=='STAFF-SE' or value=='STAFF-STP' or value=='STAFF-SD' or value=='SPONSORED-STAFF' or value=='SPONSORED-FACULTY' or value=='FACULTY-BSOE' or value=='FACULTY-CAS' or value=='FACULTY-CAPS' or value=='FACULTY-BSSP' or value=='FACULTY-GS' or value=='FACULTY-BSSD':
                if eann1[count] in eanndict.keys():
                    eanndict[eann1[count]].append(value)
                else:
                    eanndict[eann1[count]] = [value]

    finaldict = dict()
    for key in goriroldict:
        if key in eanndict:
            if sorted(goriroldict[key]) == sorted(eanndict[key]):
                finaldict[key] = goriroldict[key]

    goriroltotal = len(goriroldict)
    eanntotal = len(eanndict)
    finaltotal = len(finaldict)

    return render_template('caleb-test.html',**locals())