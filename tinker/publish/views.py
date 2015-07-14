__author__ = 'ces55739'
# python
from BeautifulSoup import *
import urllib
from datetime import datetime


# flask
from flask import Blueprint

# tinker
from tinker.tools import *
from cascade_publish import *
from tinker.web_services import *

publish_blueprint = Blueprint('publish', __name__, template_folder='templates')


@publish_blueprint.route("/")
def publish_home():
    get_user()
    username = session['username']

    if username == 'celanna' or username == 'ces55739':
        return render_template('publish-home.html', **locals())
    else:
        abort(403)


@publish_blueprint.route('/search', methods=['post'])
def publish_search():
    name = request.form['name']
    content = request.form['content']
    metadata = request.form['metadata']

    # test search info
    results = search(name, content, metadata)
    if results.matches is None or results.matches == "":
        results = []
    else:
        results = results.matches.match

    final_results = []
    for result in results:
        if result.path.siteName == "Public" and (not re.match("_", result.path.path) or re.match("_shared-content", result.path.path) or re.match("_homepages", result.path.path) ):
            final_results.append(result)

    results = final_results
    return render_template('publish-table.html', **locals())


@publish_blueprint.route('/publish/<destination>/<type>/<id>', methods=['get', 'post'])
def publish_publish(destination, type, id, ):
    if destination == "staging":
        destination = "staging.bethel.edu"
    elif destination == "production":
        destination = "Production bethel.edu"
    else:
        # default: Empty string means publish to all
        destination = ""

    if type == "block":
        try:
            relationships = list_relationships(id, type)
            pages = relationships.subscribers.assetIdentifier
            for page in pages:
                resp = publish(page.id, "page", destination)
            if 'success = "false"' in str(resp):
                return resp['message']
        except:
            return "Failed"
    else:
        resp = publish(id, type, destination)
        print resp
        if 'success = "false"' in str(resp):
            return resp['message']

    return "Publishing. . ."


@publish_blueprint.route("/more_info", methods=['post'])
def publish_more_info():
    type = request.form['type']
    id = request.form['id']

    resp = read(id, type)

    #page
    if type == 'page':
        try:
            info = resp.asset.page
            md = info.metadata
            ext = 'php'
        except:
            return "Not a valid type. . ."
    #block
    elif type == 'block':
        try:
            info = resp.asset.xhtmlDataDefinitionBlock
            md = info.metadata
            ext = ""
        except:
            return "Not a valid type. . ."
    # Todo: file
    else:
        return "Not a valid type. . ."

    # name
    if info.name:
        name = info.name
    # title
    if md.title:
        title = md.title
    # path
    if info.path:
        path = info.path

        if ext != "":
            try:
                www_publish_date = 'N/A'
                staging_publish_date = 'N/A'
                #prod
                # www publish date
                page3 = urllib.urlopen("https://www.bethel.edu/"  + path + '.' + ext).read()
                soup3 = BeautifulSoup(page3)
                date = soup3.findAll(attrs={"name":"date"})
                if date:
                    www_publish_date = convert_meta_date(date)

                # staging
                page3 = urllib.urlopen("https://staging.bethel.edu/"  + path + '.' + ext).read()
                soup3 = BeautifulSoup(page3)
                date = soup3.findAll(attrs={"name":"date"})
                if date:
                    staging_publish_date = convert_meta_date(date)

            except:
                www_publish_date = 'N/A'
                staging_publish_date = 'N/A'
    # description
    if md.metaDescription:
        description = md.metaDescription



    return render_template("publish-more-info.html", **locals())


def convert_meta_date(date):
    dates = date[0]['content'].encode('utf-8').split(" ")
    dates.pop()
    date = " ".join(dates)

    dt = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
    date_time = datetime.datetime.strftime(dt, "%B %e, %Y at %I:%M %p")

    return date_time