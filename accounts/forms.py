from django import forms
from django.contrib.auth import ( authenticate,
                                    login,
                                    logout,
                                    get_user_model,
                                    )


User = get_user_model()

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Email Address")
    email2 = forms.EmailField(label="Confirm email")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta():
        model = User
        fields = [ "first_name",
                    "last_name",
                    "username",
                    "email",
                    "email2",
                    "password",
                    ]


    def clean_email2(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")

        if email != email2:
            raise forms.ValidationError("Email does not match.")

        check_email = User.objects.filter(email=email)
        if check_email.exists():
            raise forms.ValidationError("This email is already registered with us.")

        return email



class SuperuserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label="Email Address")
    email2 = forms.EmailField(label="Confirm email")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta():
        model = User
        fields = [ "first_name",
                    "last_name",
                    "username",
                    "is_staff",
                    "email",
                    "email2",
                    "password",
                    ]


    def clean_email2(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")

        if email != email2:
            raise forms.ValidationError("Email does not match.")

        check_email = User.objects.filter(email=email)
        if check_email.exists():
            raise forms.ValidationError("This email is already registered with us.")

        return email




class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError("Invalid username and password.")
        if not user.is_active:
            raise forms.ValidationError("This account is not active.")

        return super(LoginForm, self).clean(*args, **kwargs)
