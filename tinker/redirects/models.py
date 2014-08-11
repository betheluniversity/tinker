from tinker import db

class BethelRedirect(db.Model):
    from_path = db.Column(db.String(256), primary_key=True)
    to_url = db.Column(db.String(256))

    def __init__(self, from_path, to_url):
        self.from_path = from_path
        self.to_url = to_url

    def __repr__(self):
        return '<Redirect %s to %s>' % (self.from_path, self.to_url)