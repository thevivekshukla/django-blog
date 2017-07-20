from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import ( authenticate,
                                    login,
                                    logout,)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import RegisterForm, LoginForm, SuperuserRegisterForm
# Create your views here.



def register_user(request):
    if request.user.is_authenticated() and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("posts:post_list"))

    form = RegisterForm(request.POST or None)
    if request.user.is_superuser:
        form = SuperuserRegisterForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.set_password(form.cleaned_data.get("password"))
        instance.save()
        messages.success(request, "User registered successfully.")
        if request.user.is_superuser:
            return HttpResponseRedirect(reverse("accounts:register"))
        return HttpResponseRedirect(reverse("accounts:login"))

    context = {
        "form":form,
        "title": "Register"
    }

    return render(request, "account_form.html", context)



def user_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("posts:post_list"))

    form = LoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                next_page = request.GET.get("next")
                messages.success(request, "You are successfully logged in.")
                if next_page:
                    return HttpResponseRedirect(next_page)
                return HttpResponseRedirect(reverse("posts:post_list"))
            else:
                messages.error(request, "Your account is no longer active.")
        else:
            messages.error(request, "Invalid credentials")

    context = {
        "title": "Login",
        "form": form,
    }

    return render(request, "account_form.html", context)


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You are successfully logged out.")
    return HttpResponseRedirect(reverse("accounts:login"))
