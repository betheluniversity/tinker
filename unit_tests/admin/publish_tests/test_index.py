from . import PublishBaseTestCase


class IndexTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_get("/admin/publish-manager")
        assert b'<h3>Here are the automated publishers</h3>\
<a href=\'/admin/publish-manager/program-feeds\' class="button">Program Feeds</a>\
\
<p>Blocks that are published publish out each page in the relationships tab.</p>\
\
<div id="dialog" class="reveal-modal" data-reveal>\
    <p class=\'dialog-text\'>. . . Loading . . .</p>\
    <a class="close-reveal-modal">&#215;</a>\
</div>\
\
<form action="." id="publish-search-form">\
    <div class="row">\
\
    <div class="large-6 columns">\
      <label>Search by Name\
        <input type="text" class="publish-search" name="publish-search-by-name" id="publish-search-by-name"/>\
      </label>\
    </div>\
    <div class="large-6 columns">\
      <label>Search by Content\
        <input type="text" class="publish-search" name="publish-search-by-content" id="publish-search-by-content"/>\
      </label>\
    </div>\
\
    </div>\
    <div class="row">\
\
    <div class="large-6 columns">\
      <label>Search by Metadata\
        <input type="text" class="publish-search" name="publish-search-by-metadata" id="publish-search-by-metadata"/>\
      </label>\
    </div>\
    <div class="large-6 columns">\
        <p>Publish to:\
            <label><input type="radio" name="publish-to" value="staging" checked> Staging<br /></label>\
            <label><input type="radio" name="publish-to" value="production"> Production and Staging</label>\
        </p>\
    </div>\
\
    </div>\
    <div class="row">\
\
    <div class="large-2 columns">\
        <label>Asset Types: </label>\
    </div>\
    <div class="large-2 columns">\
        <label>\
            <input class="publish-search" type="checkbox" name="publish-pages" value="page" id="publish-pages"\
                   onchange="search()" checked> Pages<br>\
        </label>\
    </div>\
    <div class="large-2 columns">\
        <label>\
            <input class="publish-search" type="checkbox" name="publish-blocks" value="block" id="publish-blocks"\
                   onchange="search()" checked> Blocks<br>\
        </label>\
    </div>\
        <div class="large-2 columns">\
            <label>\
                <input class="publish-search" type="checkbox" name="publish-files" value="file" id="publish-files"\
                       onchange="search()" checked> Files<br>\
            </label>\
        </div>\
    <div class="large-2 columns">\
        <label>\
            <input class="publish-search" type="checkbox" name="publish-folders" value="folder" id="publish-folders"\
                   onchange="search()" checked> Folders<br>\
        </label>\
    </div>\
        <div class="large-2 columns"></div>\
\
    </div>\
\
\
</form>\
\
<div class="row">\
  <div class="large-12 columns">\
    <table>\
      <thead>\
        <tr>\
          <th width="200">Asset Type</th>\
          <th width="600">Page URL</th>\
          <th width="200">Publish</th>\
          <th width="400">Messages</th>\
          <th width="200">More info</th>\
        </tr>\
      </thead>\
      <tbody id="publish-table">\
      </tbody>\
    </table>\
  </div>\
</div>' in response.data
