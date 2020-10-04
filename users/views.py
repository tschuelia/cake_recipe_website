from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import UserRegisterForm, UserUpdateForm


def send_registration_information(username):
    content = f"Ein neuer Nutzer hat sich auf rezepte.juliaschmid.com registriert: {username}."
    send_mail("Neuer User", content, settings.FROM_EMAIL, settings.ADMIN_EMAILS)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            send_registration_information(username)
            messages.success(
                request,
                f"Account für {username} erstellt! Du kannst dich jetzt anmelden!",
            )
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f"Deine Mail-Adresse wurde geändert!")
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)

    context = {
        "u_form": u_form,
    }

    return render(request, "users/profile.html", context)
