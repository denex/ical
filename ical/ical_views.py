from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

# Imaginary function to handle an uploaded file.
# from somewhere import handle_uploaded_file

from ical_uploadform import UploadFileForm


def ical(request):
    return render_to_response('ical_input.html', {},
                              context_instance=RequestContext(request))


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form})
