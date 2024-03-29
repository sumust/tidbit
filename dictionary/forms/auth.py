from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import SelectDateWidget
from django.utils.translation import gettext, gettext_lazy as _

from dictionary.models import AccountTerminationQueue, Author


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": (
            _(
                "Login unsuccessful. Please check your email and password."
            )
        )
    }
    remember_me = forms.BooleanField(required=False, label=_("Remember Me"))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text=_("A valid email address is required for registration."),
        label=_("email"),
    )
    gender = forms.ChoiceField(choices=Author.Gender.choices, label=_("gender"))
    birth_date = forms.DateField(widget=SelectDateWidget(years=range(2006, 1900, -1)), label=_("birth date"))
    terms_conditions = forms.BooleanField(required=True)

    class Meta:
        model = Author
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )
        labels = {"username": _("nickname")}


class ResendEmailForm(forms.Form):
    email = forms.EmailField(max_length=254, label=_("the email address you used to register your account"))

    def clean(self):
        if not self.errors:
            try:
                author = Author.objects.get(email=self.cleaned_data.get("email"))
                if author.is_active:
                    raise forms.ValidationError(gettext("this email has already been confirmed."))
            except Author.DoesNotExist as exc:
                raise forms.ValidationError(gettext("this email does not exist.")) from exc

        super().clean()


class ChangeEmailForm(forms.Form):
    email1 = forms.EmailField(max_length=254, label=_("new email address"))
    email2 = forms.EmailField(max_length=254, label=_("new email address (again)"))
    password_confirm = forms.CharField(label=_("confirm your password"), strip=False, widget=forms.PasswordInput)

    def clean(self):
        form_data = self.cleaned_data

        if form_data.get("email1") != form_data.get("email2"):
            raise forms.ValidationError(gettext("the emails did not match."))

        if Author.objects.filter(email=form_data.get("email1")).exists():
            raise forms.ValidationError(gettext("this email is already in use."))

        super().clean()


class TerminateAccountForm(forms.ModelForm):
    password_confirm = forms.CharField(label=_("confirm your password"), strip=False, widget=forms.PasswordInput)

    class Meta:
        model = AccountTerminationQueue
        fields = ("state",)
