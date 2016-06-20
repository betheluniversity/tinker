from tinker import db


class ProgramTag(db.Model):
    __tablename__ = 'program_tag'

    db.UniqueConstraint('key', 'tag')

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String())
    tag = db.Column(db.String())
    outcome = db.Column(db.Boolean)
    other = db.Column(db.Boolean)
    topic = db.Column(db.Boolean)

    def __init__(self, key, tag, outcome, other, topic):
        self.key = key
        self.tag = tag
        self.outcome = outcome
        self.other = other
        self.topic = topic

    def __repr__(self):
        return '<ProgramTag for %s: %s>' % (self.key, self.tag)

    # # define less than and equal to so they can sort themselves
    # def __lt__(self, other):
    #     return len(self.from_path) < len(other.from_path)
    #
    # def __eq__(self, other):
    #     return self.from_path == other.from_path and self.to_url == other.to_url