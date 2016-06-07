from tinker.tinker_controller import TinkerController

from datetime import datetime


class PublishManagerController(TinkerController):

    def convert_meta_date(self, date):
        dates = date[0]['content'].encode('utf-8').split(" ")
        dates.pop()
        date = " ".join(dates)

        dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
        date_time = datetime.strftime(dt, "%B %e, %Y at %I:%M %p")

        return date_time
