__author__ = 'ejc84332'

from flask import Blueprint, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy


from tinker import app, db

redirect_blueprint = Blueprint('redirect_blueprint', __name__,
                               template_folder='templates')

class Redirect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_path = db.Column(db.String(256), unique=True)
    to_url = db.Column(db.String(256))

    def __init__(self, from_path, to_url):
        self.from_path = from_path
        self.to_url = to_url

    def __repr__(self):
        return '<Redirect %s to %s>' % (self.from_path, self.to_url)


@redirect_blueprint.route('/')
def show():
    return render_template('redirects.html')



u = Redirect(from_path="/academics/masters/organizational-leadership/", to_url="http://gs.bethel.edu/academics/masters/strategic-leadership/")
db.session.add(u)
db.session.commit()
u = Redirect(from_path="/academics/masters/organizational-leadership/why-organizational-leadership", to_url="http://gs.bethel.edu/academics/masters/strategic-leadership/why-strategic-leadership")
db.session.add(u)
db.session.commit()
u = Redirect(from_path="/academics/masters/organizational-leadership/program-details", to_url="http://gs.bethel.edu/academics/masters/strategic-leadership/program-details")
db.session.add(u)
db.session.commit()
u = Redirect(from_path="/academics/masters/organizational-leadership/courses", to_url="http://gs.bethel.edu/academics/masters/strategic-leadership/courses")
db.session.add(u)
db.session.commit()
u = Redirect(from_path="/academics/masters/organizational-leadership/careers", to_url="http://gs.bethel.edu/academics/masters/strategic-leadership/careers")
db.session.add(u)
db.session.commit()
u = Redirect(from_path="/academics/masters/organizational-leadership/faculty", to_url="http://gs.bethel.edu/academics/masters/strategic-leadership/faculty")
db.session.add(u)
db.session.commit()
u = Redirect(from_path="/academics/masters/special-education/license-options/ld", to_url="http://gs.bethel.edu/academics/masters/special-education/license-options/")
db.session.add(u)
db.session.commit()
