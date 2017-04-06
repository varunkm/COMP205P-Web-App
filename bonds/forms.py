from django import forms
from django.forms import ModelForm
from models import *
from django.contrib.auth.models import User

class SyndicateForm(ModelForm):
    name=forms.CharField(max_length='20',label='Syndicate Name')
    class Meta:
        model = Syndicate
        exclude = ['owner', 'winnings']
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user')
        super(SyndicateForm,self).__init__(*args,**kwargs)
        self.fields['members'] = forms.ModelMultipleChoiceField(queryset=User.objects.exclude(pk=user.pk))
        
class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email    = forms.EmailField()
    class Meta:
        model = User
        fields=['username','password','first_name','last_name','email']

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields=['language','security_question','answer']
        
