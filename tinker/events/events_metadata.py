metadata_list = ['general',
                 'offices',
                 'cas_departments',
                 'internal',
                 'adult_undergrad_program',
                 'graduate_program',
                 'seminary_program']

page_values = ['author',
                'id',
                'title',
                'created-on',
                'path',
                'is_published',
                'event-dates']

# from events_metadata import page_values
#                 print page_values
#                 update(page_values, 'author', author)
#                 update(page_values, 'id', child.attrib['id'] or None)
#                 update(page_values, 'title', child.find('title').text or None)
#                 update(page_values, 'created-on', child.find('created-on').text or None)
#                 update(page_values, 'path', 'https://www.bethel.edu' + child.find('path').text or None)
#                 update(page_values, 'is_published', is_published)
#                 update(page_values, 'event-dates', "<br/>".join(dates_str))
#                 print page_values
