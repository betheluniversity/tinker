# Global
import datetime
import HTMLParser

# Packages
from BeautifulSoup import BeautifulStoneSoup
from bu_cascade.asset_tools import find, update
from flask import render_template

# Local
from tinker.tinker_controller import TinkerController


class NewsController(TinkerController):
    def test(self):
        return True

    # limit who can see this. Currently, everyone should be able to
    def inspect_child(self, child, find_all=False, csv=False):
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

        internal_values = self.search_for_key_in_dynamic_md(child, 'unique-news')

        if not workflow_status and 'Homepage' in internal_values:
            try:
                page_values = {
                    'id': child.attrib['id'] or "",
                    'title': child.find('title').text or None,
                    'path': child.find('path').text or None,
                    'image-path': child.find('system-data-structure/media/image/path').text or None,
                    'content': self.get_first_paragraph(self.element_tree_to_html(child.find('system-data-structure/main-content'))) or None,
                    'date': datetime.datetime.fromtimestamp(int(child.find('system-data-structure/publish-date').text)/1000) or None,
                    'created-on': int(child.find('system-data-structure/publish-date').text)/1000 or None
                }
            except:
                page_values = None
        else:
            page_values = None

        return page_values

    def create_single_news_article(self, article_asset, news_article_datetime):
        parser = HTMLParser.HTMLParser()
        try:
            date = news_article_datetime.strftime('%A, %B %-d, %Y')
            path = find(article_asset, 'path', False)
            title = parser.unescape(find(article_asset, 'title', False).decode('utf-8'))

            content_type = find(article_asset, 'contentTypePath', False)

            news_flex_content = find(article_asset, 'email-teaser-paragraph', False)  # get content
            news_content = find(article_asset, 'main-content', False)  # get content
            if content_type == 'News Article - Flex':
                content = news_flex_content
                image_path = find(article_asset, 'feed-image', False)['filePath']
            # todo: this could be removed when we fully launch the new things
            else:
                image_path = find(article_asset, 'image', False)['filePath']
                content = news_content
                tree_content = BeautifulStoneSoup(content, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
                self.fix_hrefs(tree_content)
                content = self.get_first_paragraph(tree_content)

            content = parser.unescape(content.decode('utf-8'))

        except:
            return ''

        return render_template('news/article.html', **locals())

    def get_first_paragraph(self, tree_content):
        return_content = ''
        for paragraph in tree_content.findAll('p'):

            temp_character_count = len(str(paragraph))

            if len(return_content) == 0:
                # use the first paragraph for sure.
                return_content += str(paragraph)
            elif len(return_content) + temp_character_count <= 500:
                # keep adding paragraphs until the limit of 500 characters is reached.
                return_content += str(paragraph)
            else:
                return return_content

        return return_content

    def fix_hrefs(self, tree_content):
        for anchor_tag in tree_content.findAll('a'):
            if anchor_tag['href'][0] == '/':
                anchor_tag['href'] = 'https://www.bethel.edu' + anchor_tag['href']

    def reset_send_email_value(self, page):
        asset, md, sd = page.get_asset()
        update(sd, 'send-email', 'No')
        page.edit_asset(asset)
