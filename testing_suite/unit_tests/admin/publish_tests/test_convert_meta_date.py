from publish_controller_base import PublishControllerBaseTestCase


class ConvertMetaDateTestCase(PublishControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConvertMetaDateTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_convert_meta_date_valid(self):
        # This object is a BeautifulSoup.ResultSet object in the live code, but I can test it in this function
        # with a dictionary inside a list.
        #                 [<meta content="Thu, 06 Jul 2017 10:30:50 -0500" name="date" />]
        date_to_convert = [{'content': "Thu, 06 Jul 2017 09:50:36 -0500", 'name': "date"}]
        response = self.controller.convert_meta_date(date_to_convert)
        self.assertEqual(response, 'July  6, 2017 at 09:50 AM')

    def test_convert_meta_date_invalid(self):
        date_to_convert = []
        self.assertRaises(IndexError, self.controller.convert_meta_date, date_to_convert)

        date_to_convert = [{}]
        self.assertRaises(KeyError, self.controller.convert_meta_date, date_to_convert)

        date_to_convert = [{'content': ''}]
        self.assertRaises(ValueError, self.controller.convert_meta_date, date_to_convert)
