# # forms.py
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#
# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     name = forms.CharField(required=True)
#
#     class Meta:
#         model = User
#         fields = ("username", "email", "name", "password1", "password2")
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         user.name = self.cleaned_data["name"]
#         if commit:
#             user.save()
#         return user