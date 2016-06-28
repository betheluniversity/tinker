from tinker import app, db
import csv
from tinker.admin.program_search.models import ProgramTag


def create_new_csv_file():
    outfile = open(app.config['PROGRAM_SEARCH_CSV'], 'wb')
    outcsv = csv.writer(outfile)
    rows = []
    records = ProgramTag.query.all()
    rows.append(['key', 'tag', 'outcome', 'other', 'topic'])
    for record in records:
        rows.append([record.key, record.tag, record.outcome, record.other, record.topic])

    outcsv.writerows(iter(rows))
    outfile.close()
    return "<pre>%s</pre>" % str(rows)
