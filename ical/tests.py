import os

from django.test import TestCase
from django.core.urlresolvers import reverse


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
        # self.assertEqual(response.status_code, 302)  # Redirect on form
        # success

        # response = self.client.post("/my/form/", {})
        # self.assertEqual(response.status_code, 200)  # we get our page back
        # with an error

    def test_url_form(self):
        url = "http://www.google.com/calendar/ical/350imrtqvd076a106dbdfofagk%40group.calendar.google.com/public/basic.ics"
        file_name = os.path.split(url)[-1]
        filename = os.path.splitext(file_name)[0] + '.csv'

        # POST empty url
        response = self.client.post(reverse('ical_post_url'), {})
        self.assertEqual(response.status_code, 200)

        # GET url
        response = self.client.get(reverse('ical_post_url'), {'url': url})
        self.assertEqual(response.status_code, 200)

        # POST valid URL
        response = self.client.post(reverse('ical_post_url'), {'url': url})
        # Session vars must be set up
        self.assertEqual(self.client.session['ical_src_url'], url)
        self.assertEqual(self.client.session['ical_src_file'], file_name)
        # Must redirect to 'ical_show_table'
        self.assertRedirects(response, reverse('ical.ical_views.ical_get_csv'), target_status_code=302)
        # 'ical_table' must exists in session
        self.assertTrue(self.client.session['ical_table'])
        # Must show table
        response = self.client.get(reverse('ical_show_table'))
        self.assertEqual(response.status_code, 200)
        # Download as CSV
        response = self.client.get(reverse('ical_download_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], ('attachment; filename="%s"' % filename))
