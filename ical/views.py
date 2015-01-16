#!/usr/bin/python
# encoding: utf-8

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from forms import ICalUrlForm, UploadIcalFileForm

import ical
import csv
import os

from save_xlsx import save_xlsx_as_data


def registration(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        print "NEW USER:", user
        return HttpResponseRedirect(reverse('login'))

    return render_to_response('registration/login.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def ical_index(request):
    initial = {}
    url = request.session.get('ical_src_url')
    if url:
        initial['url'] = url
    url_form = ICalUrlForm(initial=initial)
    file_form = UploadIcalFileForm()
    return render_to_response('ical_input.html',
                              {'url_form': url_form, 'file_form': file_form},
                              context_instance=RequestContext(request))


def ical_post_url(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ICalUrlForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            url = form.cleaned_data['url']
            request.session['ical_src_url'] = url
            request.session['ical_src_file'] = os.path.split(url)[-1]
            return HttpResponseRedirect(reverse('ical_get_csv'))  # Redirect after POST
    else:
        if request.session.get('ical_src_url'):
            form = ICalUrlForm(initial={
                               'url': request.session.get('ical_src_url')})
        else:
            form = ICalUrlForm()  # An unbound form
    return render_to_response('ical_input.html',
                              {'url_form': form},
                              context_instance=RequestContext(request))


def ical_upload_file(request):
    if request.method == 'POST':
        form = UploadIcalFileForm(request.POST, request.FILES)
        if form.is_valid():
            key, [value] = request.FILES.popitem()
            filename = value.name
            file_size = value.size
            if file_size > 1048576:
                request.session['error'] = "File '%s' is too large (%d bytes)" % (
                    filename, file_size)
                return HttpResponseRedirect(reverse('ical_error'))
            file_ext = os.path.splitext(filename)[-1]
            if file_ext.lower() != ".ics":
                request.session['error'] = "File '%s' has not extension '.ics'" % (filename)
                return HttpResponseRedirect(reverse('ical_error'))
            print "Parsing iCal from Uploaded file:", filename, "size:", file_size
            request.session['ical_src_file'] = filename
            if value:
                lines = ''
                for chunk in value.chunks():
                    lines += chunk.decode('utf-8')
                table = [ev.as_tuple() for ev in ical.get_events_from_unicode_stream(lines.splitlines())]
                if table:
                    request.session['ical_table'] = table
                    return HttpResponseRedirect(reverse('ical_show_table'))
            return HttpResponseRedirect(reverse('ical_error'))
    form = UploadIcalFileForm()
    return render_to_response('ical_input.html', {'file_form': form}, context_instance=RequestContext(request))


def ical_show_table(request):
    table = request.session.get('ical_table')
    if table:
        filename = request.session.get('ical_src_file')
        source = request.session.get('ical_src_url', filename)
        return render(request, 'table.html', {'table': table, 'source': source})
    return HttpResponseRedirect(reverse('ical_index'))


def ical_get_csv(request):
    url = request.session.get('ical_src_url')
    if not url:
        return HttpResponseRedirect(reverse('ical_post_url'))
    print "Parsing iCal from URL:", url
    table = [ev.as_tuple() for ev in ical.getRawEventsFromUrl(url)]
    if table:
        request.session['ical_table'] = table
        return HttpResponseRedirect(reverse('ical_show_table'))

    return HttpResponseRedirect(reverse('ical_error'))


@login_required
def ical_download_csv(request):
    table = request.session.get('ical_table')
    if not table:
        return HttpResponseRedirect(reverse('ical_index'))

    response = HttpResponse(content_type='text/csv')
    ical_src_file = request.session.get('ical_src_file', "somefilename.csv")
    filename = os.path.splitext(ical_src_file)[0] + '.csv'
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    writer = csv.writer(response)
    for row in table:
        # Stupid CSV can not handle unicode, coverting to UTF-8
        writer.writerow([i.encode('utf-8') for i in row])
    return response


@login_required
def ical_download_xlsx(request):
    table = request.session.get('ical_table')
    if not table:
        return HttpResponseRedirect(reverse('ical_index'))

    ical_src_file = request.session.get('ical_src_file', "somefilename")
    title = os.path.splitext(ical_src_file)[0]
    filename = title + '.xlsx'
    response = HttpResponse(save_xlsx_as_data(table, title=title), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


def ical_error(request):
    return render_to_response(
        'error.html',
        {'error': request.session.get('error')},
        context_instance=RequestContext(request)
    )
