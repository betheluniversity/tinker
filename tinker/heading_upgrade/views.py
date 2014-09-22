__author__ = 'ejc84332'

#python
import re
import smtplib

from flask import Blueprint, render_template, abort, request, redirect
from BeautifulSoup import BeautifulSoup

from tinker import app, db, tools
from tinker.web_services import *


heading_upgrade = Blueprint('heading_upgrade', __name__,
                               template_folder='templates')


def inspect_folder(folder_id):

    folder = read(folder_id, type="folder")
    children = folder['asset']['folder']['children']['child']
    resp = []
    for child in children:
        if child['type'] == 'page':
            resp.append(inspect_page(child['id']))
            break
        elif child['type'] == 'folder':
            resp.append(inspect_folder(child['id']))

    return "<pre>" + "\n".join(resp) + "</pre>"


def inspect_page(page_id):
    page = read(page_id)
    return str(page)

@heading_upgrade.route('/')
def show():

    start_folder_id = '221eb5918c58651326c0f0dfe69e3c6d'
    # for page in pages:
    #     data = read_path('_testing/jmo/test-page')

    resp = inspect_folder(start_folder_id)

    return resp