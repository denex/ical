from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'ical.ical_views',

    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^ical/$', 'ical_index', name='ical_index'),
    url(r'^ical/url/$', 'ical_post_url', name='ical_post_url'),
    url(r'^ical/file/$', 'ical_upload_file', name='ical_upload_file'),
    url(r'^ical/get_csv/$', 'ical_get_csv'),
    url(r'^ical/show_table/$', 'ical_show_table', name='ical_show_table'),
    url(r'^ical/download_csv/$', 'ical_download_csv', name='ical_download_csv'),
)
