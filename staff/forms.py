from django import forms
from .models import HubSessions

class HubSessionsForm(forms.ModelForm):
    class Meta:
        model = HubSessions
        fields = ['guest_name', 'loyalty_card_holder', 'session_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'my-3 block w-full px-3 py-2 bg-transparent border-2 border-[#BEBEBE] text-black rounded-md focus:border-transparent focus:outline-none focus:ring focus:ring-fuchsia-400 placeholder-gray-300'})



