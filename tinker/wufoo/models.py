__author__ = 'ejc84332'

from tinker import app
from tinker import db


class FormInfo(db.Model):

    hash = db.Column(db.String(24), primary_key=True)
    preload_info = db.Column(db.String(256))
    paypal_name = db.Column(db.String(24))
    paypal_budget_number = db.Column(db.String(24))
    sync_status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<FormInfo %r>' % self.hash + " " + self.preload_info

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'hash'         : self.hash,
           'preload_info': self.preload_info,
           'paypal_name'  : self.paypal_name,
           'paypal_budget_number'  : self.paypal_budget_number,
           'sync_status'  : self.sync_status,
        }