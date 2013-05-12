from django import forms


class UploadIcalFileForm(forms.Form):
    file_data = forms.FileField(label="iCal file", max_length=1048576)


class ICalUrlForm(forms.Form):
    url = forms.URLField(label="iCal file URL")
