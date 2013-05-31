from __future__ import with_statement

from .settings import PROJECT_ROOT

import os

from django.test import TestCase
from django.core.urlresolvers import reverse


class MyTests(TestCase):

    urls_with_redirect = [
        ('/', ''),
        ('/about/', ''),
        ('/ical/', ''),
        ('/ical/url/', ''),
        ('/ical/file/', ''),
        ('/ical/get_csv/', '/ical/url/'),
        ('/ical/show_table/', '/ical/'),
        ('/ical/download_csv/', '/ical/'),
        ('/ical/error/', ''),
    ]

    def test_urls(self):
        for url, _ in self.urls_with_redirect:
            response = self.client.get(url, follow=True)
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError, ae:
                print "URL:", url
                raise ae

        for url, redirect in self.urls_with_redirect:
            response = self.client.get(url)
            if redirect:
                try:
                    self.assertRedirects(response, redirect)
                except AssertionError, ae:
                    print "URL:", url, redirect
                    raise ae
            else:
                self.assertEqual(response.status_code, 200)

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
        # Must redirect to 'ical_show_table'
        self.assertRedirects(response, reverse('ical_get_csv'), target_status_code=302)
        # Must show table
        response = self.client.get(reverse('ical_show_table'))
        self.assertEqual(response.status_code, 200)
        # Download as CSV
        response = self.client.get(reverse('ical_download_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], ('attachment; filename="%s"' % filename))

    def test_upload_form(self):
        file_path = os.path.join(PROJECT_ROOT, '..', "test_ics")
        files = os.listdir(file_path)
        for file_name in files:
            filename = os.path.splitext(file_name)[0] + '.csv'
            full_file_name = os.path.join(file_path, file_name)
            with open(full_file_name) as ical:
                response = self.client.post(reverse('ical_upload_file'), {'file_data': ical})
                self.assertRedirects(response, reverse('ical_show_table'))
            # Download as CSV
            response = self.client.get(reverse('ical_download_csv'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Disposition'], ('attachment; filename="%s"' % filename))

    def test_ical_test_forms(self):
        response = self.client.get(reverse('ical_index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ical_post_url'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('ical_upload_file'), {})
        self.assertEqual(response.status_code, 200)
