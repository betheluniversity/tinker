import datetime
from createsend import *

# flask
from flask import render_template, session

# tinker
from tinker.tinker_controller import TinkerController


class NewsController(TinkerController):
    def test(self):
        return True

    # limit who can see this. Currently, everyone should be able to
    def inspect_child(self, child, find_all=False):
        try:
            return self._iterate_child_xml(child)
        except AttributeError:
            # not a valid e-ann block
            return None

    # gather data from the article
    def _iterate_child_xml(self, child):
        try:
            workflow_status = child.find('workflow').find('status').text
        except AttributeError:
            workflow_status = None

        if not workflow_status:
            try:
                page_values = {
                    'id': child.attrib['id'] or "",
                    'title': child.find('title').text or None,
                    'path': child.find('path').text or None,
                    'image-path': child.find('system-data-structure/media/image/path').text or None,
                    'content': self.element_tree_to_html(child.find('system-data-structure/main-content')) or None,
                    'date': datetime.datetime.fromtimestamp(int(child.find('system-data-structure/publish-date').text)/1000) or None,
                    'created-on': int(child.find('system-data-structure/publish-date').text)/1000 or None
                }
            except:
                page_values = None
        else:
            page_values = None

        return page_values

    def create_single_news_article(self, article):
        date = article['date'].strftime('%A, %B %-d, %Y')
        return render_template('news-article.html', **locals())
