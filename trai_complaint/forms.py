from django import forms

class MySignupForm(forms.Form):
	required_css_class = 'required'
	first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name','autofocus': 'autofocus'}))
	last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

	def __init__(self,*args,**kwargs):
		super(MySignupForm,self).__init__(*args,**kwargs)

	def signup(self, request, user):
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
