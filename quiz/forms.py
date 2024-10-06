# quiz/forms.py
from django import forms
from .models import QuizBank, Profile

class JSONUploadForm(forms.Form):
    json_file = forms.FileField(label='Upload JSON File')
    quiz_bank = forms.ModelChoiceField(queryset=QuizBank.objects.all(), label='Select Quiz Bank')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'bio']
