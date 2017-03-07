from django import forms
from django.forms import ModelForm
from models import *

class SyndicateForm(ModelForm):
    name=forms.CharField(max_length='20',label='Syndicate Name')
    class Meta:
        model = Syndicate
        exclude = ['owner', 'winnings']
    def __init__(self,*args,**kwargs):
        userprofile = kwargs.pop('userprofile')
        super(SyndicateForm,self).__init__(*args,**kwargs)
        self.fields['members'] = forms.ModelMultipleChoiceField(queryset=UserProfile.objects.exclude(pk=userprofile.pk))
        
