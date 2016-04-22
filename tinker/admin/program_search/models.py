from tinker import db


class ProgramTag(db.Model):
    __tablename__ = 'program_tag'

    id = db.Column(db.Integer, primary_key=True)
    program = db.column(db.String())
    tag = db.Column(db.String())
    outcome = db.Column(db.Boolean)
    other = db.Column(db.Boolean)
    topic = db.Column(db.Boolean)

    def __init__(self, program, tag, outcome, other, topic):
        self.program = program
        self.tag = tag
        self.outcome = outcome
        self.other = other
        self.topic = topic

    def __repr__(self):
        return '<ProgramTag for %s: %s>' % (self.program, self.tag)

    # # define less than and equal to so they can sort themselves
    # def __lt__(self, other):
    #     return len(self.from_path) < len(other.from_path)
    #
    # def __eq__(self, other):
    #     return self.from_path == other.from_path and self.to_url == other.to_url