from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('ical.ical_views',
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^ical/$', 'ical'),
)
