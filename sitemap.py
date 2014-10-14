#!/Users/ejc84332/envs/tinker/bin/python
import os.path

from tinker.web_services import *
from tinker import app
from flask import Response


###Just putting this here to work on it. Move out of tinker once the Cascade stuff is more portable
def inspect_folder(folder_id):
    folder = read(folder_id, type="folder")
    md = folder.asset.folder.metadata.dynamicFields
    md = get_md_dict(md)
    if ('hide-from-sitemap' in md.keys() and md['hide-from-sitemap'] == "Do not hide") or 'hide-from-sitemap' not in md.keys():
        children = folder.asset.folder.children
        if not children:
            app.logger.info("folder has no children %s" % folder.asset.folder.path)
            yield
        else:
            for child in children['child']:
                if child['type'] == 'page':
                    for item in inspect_page(child['id']):
                        yield item
                elif child['type'] == 'folder':
                    app.logger.info("looking in folder %s" % child.path.path)
                    for item in inspect_folder(child['id']):
                        yield item


def get_md_dict(md):
    data = {}
    if not md:
        return data
    for field in md.dynamicField:
        try:
            data[field.name] = field.fieldValues.fieldValue[0].value
        except:
            data[field.name] = None

    return data


def inspect_page(page_id):
    page = read(page_id)
    md = page.asset.page.metadata.dynamicFields
    md = get_md_dict(md)
    if 'hide-from-sitemap' in md.keys() and md['hide-from-sitemap'] == "Hide":
        return
    path = page.asset.page.path
    ##Is this page currently published to production?
    if not os.path.exists('/var/www/cms.pub/%s.php' % path):
        return
    ret = ["<url>"]
    ret.append("<loc>https://www.bethel.edu/%s</loc>" % path)
    date = page.asset.page.lastModifiedDate

    ret.append("<lastmod>%s-%s-%s</lastmod>" % (date.year, date.month, date.day))
    ret.append("</url>")
    yield "\n".join(ret)


@app.route('/sitemap')
def sitemap():
    base_folder = "ba134b8e8c586513100ee2a7637628a4"
    base_folder = "c1b35e288c5865133a5d3f893471aefd"
    ##base_folder = read(base_folder, type="folder")
    with open('/var/www/staging/public/_testing/jmo/sitemap.xml', 'w') as file:
        file.write("{}\n".format('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'))
        for item in inspect_folder(base_folder):
            file.write("{}\n".format(item))
        file.write("{}\n".format('</urlset>'))


if __name__ == "__main__":
    sitemap()