from django import forms
from models import Game
import datetime

class NewGameForm(forms.Form):
    name = forms.CharField(label='Game Name', max_length=100)
    invite = forms.ChoiceField(label='Who Do You Want To Invite?', choices=[(0, 'Anyone'), (1, 'Only people I follow who also follow me')], widget=forms.RadioSelect(attrs={'class':'nobullet'}))
    start = forms.DateTimeField(label="Start date and time", initial=datetime.datetime.now(), help_text="You can change this value to start in the future to allow your friends time to join.")
    send_tweet = forms.BooleanField(required=False, label='Send Tweet', help_text="If you check this box a tweet will be sent to your timeline inviting your friends and followers to join the game.")
    
    def __init__(self, *args, **kwargs):
        self.httprequest = kwargs.pop('httprequest', None)
        super(NewGameForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        if self.httprequest:
            # only allow 5 games per person for now
            games = Game.objects.filter(admin=self.httprequest.user)
            if len(games) >= 5: #shouldn't be hardcoded
                raise forms.ValidationError('Users are limited to creating a maximum of 5 games. If You would like to create more, contact the site admin.')
        return self.cleaned_data
        
    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            if Game.objects.get(name__iexact=name):
                raise forms.ValidationError("The name %s has been taken." % name)
        except Game.DoesNotExist:
            pass            
        # Always return the cleaned data, whether you have changed it or
        # not.
        return name

class SearchForm(forms.Form):
    name = forms.CharField(label='Game To Search For', max_length=100)


