from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.core.urlresolvers import reverse

# Imaginary function to handle an uploaded file.
# from somewhere import handle_uploaded_file

from .ical_forms import ICalUrlForm, UploadIcalFileForm

from . import ical
import csv
import os


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
            return HttpResponseRedirect(reverse('ical.ical_views.ical_get_csv'))  # Redirect after POST
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
                return HttpResponseRedirect(reverse('ical.ical_views.ical_error'))
            file_ext = os.path.splitext(filename)[-1]
            if file_ext.lower() != ".ics":
                request.session['error'] = "File '%s' has not extension '.ics'" % (filename)
                return HttpResponseRedirect(reverse('ical.ical_views.ical_error'))
            print "Parsing iCal from Uploaded file:", filename, "size:", file_size
            request.session['ical_src_file'] = filename
            if value:
                lines = ''
                for chunk in value.chunks():
                    lines += chunk
                table = [ev.as_row() for ev in ical.get_events_from_stream(
                    lines.splitlines())]
                if table:
                    request.session['ical_table'] = table
                    return HttpResponseRedirect(reverse('ical.ical_views.ical_show_table'))
            return HttpResponseRedirect(reverse('ical.ical_views.ical_error'))
    form = UploadIcalFileForm()
    return render_to_response('ical_input.html', {'file_form': form}, context_instance=RequestContext(request))


def ical_show_table(request):
    table = request.session.get('ical_table')
    if table:
        filename = request.session.get('ical_src_file')
        source = request.session.get('ical_src_url', filename)
        return render(request, 'table.html', {'table': table, 'source': source})
    return HttpResponseRedirect(reverse('ical.ical_views.ical_index'))


def ical_get_csv(request):
    url = request.session.get('ical_src_url')
    if not url:
        return HttpResponseRedirect(reverse('ical.ical_views.ical_post_url'))
    print "Parsing iCal from URL:", url
    table = [ev.as_row() for ev in ical.getRawEventsFromUrl(url)]
    if table:
        request.session['ical_table'] = table
        return HttpResponseRedirect(reverse('ical.ical_views.ical_show_table'))
    return HttpResponseRedirect(reverse('ical.ical_views.ical_error'))


def ical_download_csv(request):
    table = request.session.get('ical_table')
    if not table:
        return HttpResponseRedirect(reverse('ical.ical_views.ical_index'))

    response = HttpResponse(content_type='text/csv')
    ical_src_file = request.session.get('ical_src_file', "somefilename.csv")
    filename = os.path.splitext(ical_src_file)[0] + '.csv'
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename

    writer = csv.writer(response)
    for row in table:
        writer.writerow(row)
    return response


def ical_error(request):
    return render_to_response('error.html', {'error': request.session.get('error')}, context_instance=RequestContext(request))
