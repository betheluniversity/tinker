__author__ = 'ces55739'

# flask
from flask import Blueprint

# tinker
from tinker.tools import *
from cascade_publish import *
from tinker.web_services import *

publish_blueprint = Blueprint('publish', __name__, template_folder='templates')

@publish_blueprint.route("/")
def publish_home():



    return render_template('publish-home.html', **locals())


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
        if result.path.siteName == "Public" and "_testing/" not in result.path.path:
            final_results.append(result)

    results = final_results
    return render_template('publish-table.html', **locals())