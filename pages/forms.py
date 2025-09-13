
# ===========================================
# fitness/forms.py
# ===========================================
from dataclasses import dataclass
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(min_length=1)
    password = forms.CharField(widget=forms.PasswordInput, min_length=1)

class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4)
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8)
    public = forms.BooleanField(required=False)

class ExerciseForm(forms.Form):
    type_id = forms.IntegerField()
    class_id = forms.IntegerField()
    weight = forms.FloatField(min_value=0)
    date = forms.CharField()
    note = forms.CharField(required=False)
    public = forms.BooleanField(required=False)

class ExerciseEditForm(forms.Form):
    type_id = forms.IntegerField()
    weight = forms.FloatField(min_value=0)
    date = forms.CharField()
    note = forms.CharField(required=False)

class ExerciseTypeAddForm(forms.Form):
    name = forms.CharField()

class CommentForm(forms.Form):
    comment = forms.CharField()