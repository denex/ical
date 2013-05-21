from django.test import TestCase


class MyTests(TestCase):

    url_list = [
        ('/about/', 200),
        ('/ical/', 200),
        ('/ical/url/', 200),
        ('/ical/file/', 200),
        ('/ical/get_csv/', 302),
        ('/ical/show_table/', 302),
        ('/ical/download_csv/', 302),
        ('/ical/error/', 200),
    ]

    def test_urls(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        for url, expected_status_code in self.url_list:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, expected_status_code)
            except AssertionError as e:
                print "URL:", url
                raise e

        # response = self.client.post("/my/form/", {"data": "value"})
        # self.assertEqual(
        # response.status_code, 302)  # Redirect on form success

        # response = self.client.post("/my/form/", {})
        # self.assertEqual(
        # response.status_code, 200)  # we get our page back with an error
