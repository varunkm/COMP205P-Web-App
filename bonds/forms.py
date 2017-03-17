from django import forms
from django.forms import ModelForm
from models import *

class SyndicateForm(ModelForm):
    name=forms.CharField(max_length='20',label='Syndicate Name')
    class Meta:
        model = Syndicate
        exclude = ['owner', 'winnings']
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user')
        super(SyndicateForm,self).__init__(*args,**kwargs)
        self.fields['members'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(pk=user.pk))
        
