from __future__ import with_statement

from settings import PROJECT_ROOT

import os

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class SmokeTest(TestCase):

    urls_with_redirect = [
        ('/', ''),
        ('/about/', ''),
        ('/ical/', ''),
        ('/ical/url/', ''),
        ('/ical/file/', ''),
        ('/ical/get_csv/', '/ical/url/'),
        ('/ical/show_table/', '/ical/'),
        ('/ical/download_csv/', '/login/?next=/ical/download_csv/'),
        ('/ical/download_xlsx/', '/login/?next=/ical/download_xlsx/'),
        ('/ical/error/', ''),
    ]

    def test_all_urls(self):
        for url, _ in self.urls_with_redirect:
            response = self.client.get(url, follow=True)
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError:
                print "URL:", url
                raise

        for url, redirect in self.urls_with_redirect:
            response = self.client.get(url)
            if redirect:
                try:
                    self.assertRedirects(response, redirect)
                except AssertionError:
                    print "URL:", url, redirect
                    raise
            else:
                self.assertEqual(response.status_code, 200)

    def test_urls_reverse(self):
        response = self.client.get(reverse('ical_index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('ical_post_url'), {})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('ical_upload_file'), {})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)


class iCalTests(TestCase):

    def setUp(self):
        self.admin_password = 'pass'
        self.admin = User.objects.create_superuser(
            'root', 'root@example.com', self.admin_password)

    def test_registration(self):
        username = "user"
        password = "pass"
        response = self.client.post(reverse('registration'), {'username': username, 'password1': password, 'password2': password})
        self.assertRedirects(response, reverse('login'))
        self.assertEquals(User.objects.latest('pk').username, username)

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
        # Trying download as CSV without login
        response = self.client.get(reverse('ical_download_csv'))
        login_url = '%s?next=%s' % (reverse('login'), reverse('ical_download_csv'))
        self.assertRedirects(response, login_url)
        # Login and download
        response = self.client.post(login_url, {'username': self.admin.username, 'password': self.admin_password}, follow=True)
        self.assertEqual(response['Content-Disposition'], (
            'attachment; filename="%s"' % filename))

    def test_upload_file_form(self):
        self.client.login(username=self.admin.username, password=self.admin_password)
        file_path = os.path.join(PROJECT_ROOT, '..', "test_ics")
        files = os.listdir(file_path)
        for file_name in files:
            full_file_name = os.path.join(file_path, file_name)
            with open(full_file_name) as ical:
                response = self.client.post(reverse('ical_upload_file'), {'file_data': ical})
                self.assertRedirects(response, reverse('ical_show_table'))
            # Download as CSV
            filename = os.path.splitext(file_name)[0] + '.csv'
            response = self.client.get(reverse('ical_download_csv'))
            self.assertIn('Content-Disposition', response)
            self.assertEqual(response['Content-Disposition'], ('attachment; filename="%s"' % filename))
            # Download as XLSX
            filename = os.path.splitext(file_name)[0] + '.xlsx'
            response = self.client.get(reverse('ical_download_xlsx'))
            self.assertIn('Content-Disposition', response)
            self.assertEqual(response['Content-Disposition'], ('attachment; filename="%s"' % filename))
