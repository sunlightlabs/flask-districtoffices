from flask import Flask, Response, redirect, render_template
from sunlightapi import sunlight, SunlightApiError
import csv
import json
import os

PWD = os.path.abspath(os.path.dirname(__file__))
OFFICES = {}

sunlight.apikey = 'a25cc8b1f8bc16b4fdbfc23995516049'

# Load district offices from CSV and store in memory

infile = open(os.path.join(PWD, 'data', 'directory-clean.csv'))

for record in csv.reader(infile):
    if record[0] not in OFFICES:
        OFFICES[record[0]] = []
    OFFICES[record[0]].append({
        'address': record[1],
        'latitude': record[2],
        'longitude': record[3],
        'phone': record[4],
    })

infile.close()

def legislator_to_dict(legislator):
    return {
        'title': legislator.title,
        'firstname': legislator.firstname,
        'lastname': legislator.lastname,
        'bioguide_id': legislator.bioguide_id,
        'district': legislator.district,
        'party': legislator.party,
        'offices': OFFICES.get(legislator.bioguide_id, []),
    }

#
# the app
#

app = Flask(__name__)

@app.route("/zipcode/<zipcode>")
def by_zipcode(zipcode):

    print zipcode

    members = []

    for legislator in sunlight.legislators.allForZip(zipcode):

        if legislator.in_office:
            members.append(legislator_to_dict(legislator))

    return Response(json.dumps(members), mimetype='application/json')

@app.route("/member/<bioguide_id>")
def by_member(bioguide_id):

    legislator = sunlight.legislators.get(bioguide_id=bioguide_id, in_office=True)
    member = legislator_to_dict(legislator)

    return Response(json.dumps(member), mimetype='application/json')

@app.route("/embed")
def embed():
    return render_template('index.html')

@app.route("/")
def index():
    return redirect('/embed')


if __name__ == '__main__':
    app.run(debug=True, port=8000)