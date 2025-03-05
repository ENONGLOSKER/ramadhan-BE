from django import forms
from .models import JadwalSalat

class UploadJadwalSalatForm(forms.Form):
    file = forms.FileField(label="Upload File Excel")