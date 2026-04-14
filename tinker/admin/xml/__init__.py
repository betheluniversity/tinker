from datetime import datetime

from flask import render_template, Response, session
from flask_classy import FlaskView
import requests
import xml.etree.ElementTree as ET
import csv
from tinker import app
import io

from tinker.tinker_controller import admin_permissions


class XMLView(FlaskView):
    route_base = '/admin/xml'

    def before_request(self, name, **kwargs):
        admin_permissions(self)
    def index(self):
        username = session['username']
        return render_template('admin/xml/home.html', **locals())

    def download_proof_points(self):
        try:
            # Send a GET request to fetch the XML data
            response = requests.get(app.config['PROOF_POINT_XML'])
            if response.status_code != 200:
                return f"Failed to retrieve data: {response.status_code}", 500

            # Parse the XML data
            root = ET.fromstring(response.content)

            # Prep csv file in memory
            output = io.StringIO()
            writer = csv.writer(output)

            # Write the header row
            writer.writerow(['Name', 'ID', 'Path', 'Proof Point Text', 'Owner', 'Origin', 'Date Fact Check', 'Notes'])

            # Iterate over each system-block in the XML
            for system_page in root.findall('.//system-block'):
                # Check if the system-data-structure has the definition path "Blocks/Proof Point"
                system_data_structure = system_page.find('system-data-structure')
                if system_data_structure is not None and system_data_structure.get('definition-path') == 'Blocks/Proof Point':
                    name = system_page.find('name').text if system_page.find('name') is not None else ''
                    id_ = system_page.get('id')
                    path = system_page.find('path').text if system_page.find('path') is not None else ''

                    # Find the proof-point element
                    proof_point = system_data_structure.find('proof-point')
                    if proof_point is not None:
                        type_ = proof_point.find('type').text if proof_point.find('type') is not None else ''
                        if type_ == 'Number':
                            # Pull main-text-number and text-below, then combine them
                            number_group = proof_point.find('number-group')
                            if number_group is not None:
                                main_text_number = number_group.find('main-text-number').text if number_group.find(
                                    'main-text-number') is not None else ''
                                text_below = number_group.find('text-below').text if number_group.find(
                                    'text-below') is not None else ''
                                proof_point_text = f"{main_text_number} {text_below}".strip()
                            else:
                                proof_point_text = ''
                        elif type_ == 'Text':
                            # Pull main-text from the text element
                            text_element = proof_point.find('text')
                            if text_element is not None:
                                main_text = text_element.find('main-text').text if text_element.find(
                                    'main-text') is not None else ''
                                proof_point_text = main_text
                            else:
                                proof_point_text = ''
                        else:
                            proof_point_text = ''
                    else:
                        proof_point_text = ''

                    # Pull data from the <info> element
                    info = system_data_structure.find('info')
                    owner = info.find('bethel-owner').text if info is not None and info.find(
                        'bethel-owner') is not None else ''
                    origin = info.find('origin').text if info is not None and info.find('origin') is not None else ''
                    date_fact_check = info.find('date-fact-check').text if info is not None and info.find(
                        'date-fact-check') is not None else ''
                    notes = info.find('notes').text if info is not None and info.find('notes') is not None else ''

                    # Write the row to the CSV
                    writer.writerow([name, id_, path, proof_point_text, owner, origin, date_fact_check, notes])

            # Return the CSV as a downloadable file
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=proof_points.csv'}
            )
        except requests.RequestException as e:
            return f"Error fetching faculty bios XML: {str(e)}", 500
        except ET.ParseError as e:
            return f"Error parsing faculty bios XML: {str(e)}", 500
        except Exception as e:
            return f"Unexpected error: {str(e)}", 500


    def download_faculty_bios(self):
        # Send a GET request to fetch the XML data
        response = requests.get(app.config['FACULTY_BIOS_XML_URL'])
        if response.status_code != 200:
            return f"Failed to retrieve data: {response.status_code}", 500

        # Parse the XML data
        root = ET.fromstring(response.content)

        # Prep csv file in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write the header row
        writer.writerow([
            'Name', 'Title', 'Email', 'Started at Bethel', 'Location',
            'Full/Part Time', 'Highlight', 'School', 'Department',
            'Adjunct', 'Full Time', 'Emeritus/Emerita', 'Job Title',
            'Education School', 'Education Degree', 'Education Year',
            'Page Path', 'Page Link', 'Cascade Link', 'Last Modified', 'Last Modified By',
            'Last Published'
        ])

        for system_page in root.findall('.//system-page'):
            # Get basic system_page info
            name = system_page.findtext('name', '')
            title = system_page.findtext('title', '')
            path = system_page.findtext('path', '')
            link = 'https://www.bethel.edu' + path
            cms_link = 'https://cms.bethel.edu/entity/open.act?id=' + system_page.attrib['id'] + '&type=page'
            last_modified = datetime.fromtimestamp(int(system_page.findtext('last-modified', ''))/1000.0)
            last_modified_by = system_page.findtext('last-modified-by', '')
            last_published = datetime.fromtimestamp(int(system_page.findtext('last-published-on', ''))/1000.0)

            # Find the system-data-structure with Faculty Bio definition
            bio_data = system_page.find(".//system-data-structure[@definition-path='Faculty Bio']")

            if bio_data is not None:
                # Extract faculty bio fields
                first = bio_data.findtext('first', '')
                last = bio_data.findtext('last', '')
                full_name = f"{first} {last}".strip()

                email = bio_data.findtext('email', '').strip()
                started_at_bethel = bio_data.findtext('started-at-bethel', '')
                faculty_location = bio_data.findtext('.//faculty_location/value', '')
                full_or_part = bio_data.findtext('full-or-part', '')
                highlight = bio_data.findtext('highlight', '')

                # Extract job titles info
                job_titles = bio_data.find('job-titles')
                if job_titles is not None:
                    school = job_titles.findtext('school', '')
                    department = job_titles.findtext('department', '')
                    adjunct = job_titles.findtext('adjunct', '')
                    fulltime = job_titles.findtext('fulltime', '')
                    emeritus = job_titles.findtext('emeritus', '')
                    job_title = job_titles.findtext('job_title', '')
                else:
                    school = department = adjunct = fulltime = emeritus = job_title = ''

                # Extract education (just the first one for now)
                education = bio_data.find('education')
                if education is not None:
                    edu_school = education.findtext('school', '')
                    edu_degree = education.findtext('degree-earned', '')
                    edu_year = education.findtext('year', '')
                else:
                    edu_school = edu_degree = edu_year = ''
            else:
                # No bio data found
                full_name = name
                email = started_at_bethel = faculty_location = full_or_part = highlight = ''
                school = department = adjunct = fulltime = emeritus = job_title = ''
                edu_school = edu_degree = edu_year = ''

            # Write the row
            writer.writerow([
                full_name, title, email, started_at_bethel, faculty_location,
                full_or_part, highlight, school, department,
                adjunct, fulltime, emeritus, job_title,
                edu_school, edu_degree, edu_year,
                path, link, cms_link, last_modified, last_modified_by, last_published
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=faculty_bios.csv'}
        )