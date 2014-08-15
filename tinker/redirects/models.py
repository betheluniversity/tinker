from tinker import db

class BethelRedirect(db.Model):
    from_path = db.Column(db.String(256), primary_key=True)
    to_url = db.Column(db.String(256))

    def __init__(self, from_path, to_url):
        self.from_path = from_path
        self.to_url = to_url

    def __repr__(self):
        return '<Redirect %s to %s>' % (self.from_path, self.to_url)

    ##define less than and equal to so they can sort themselves
    def __lt__(self, other):
        return len(self.from_path) < len(other.from_path)

    def __eq__(self, other):
        return self.from_path == other.from_path and self.to_url == other.to_url