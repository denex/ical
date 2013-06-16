# -*- coding: utf-8 -*-
import lettuce

from lxml import html
from django.test.client import Client
from nose.tools import assert_equals

@lettuce.before.all
def set_browser():
    lettuce.world.browser = Client()


@lettuce.step(u'Given I access the url "([^"]*)"')
def given_i_access_the_url_group1(step, url):
    response = lettuce.world.browser.get(url)
    lettuce.world.dom = html.fromstring(response.content)


@lettuce.step(u'When I upload CSV file')
def when_i_upload_csv_file(step):
    assert False, 'This step must be implemented'


@lettuce.step(u'Then I see table with events')
def then_i_see_table_with_events(step):
    assert False, 'This step must be implemented'
