from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^login/$',  login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^registration/$', 'ical.views.registration', name='registration'),
    url(r'^profile/$', TemplateView.as_view(template_name='registration/login.html'), name='profile'),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^ical/$', 'ical.views.ical_index', name='ical_index'),
    url(r'^ical/url/$', 'ical.views.ical_post_url', name='ical_post_url'),
    url(r'^ical/file/$', 'ical.views.ical_upload_file', name='ical_upload_file'),
    url(r'^ical/get_csv/$', 'ical.views.ical_get_csv', name='ical_get_csv'),
    url(r'^ical/show_table/$', 'ical.views.ical_show_table', name='ical_show_table'),
    url(r'^ical/download_csv/$', 'ical.views.ical_download_csv', name='ical_download_csv'),
    url(r'^ical/download_xlsx/$', 'ical.views.ical_download_xlsx', name='ical_download_xlsx'),
    url(r'^ical/error/$', 'ical.views.ical_error', name='ical_error'),
)
