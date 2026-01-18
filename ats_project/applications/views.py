from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import ShortlistedCandidate, HoldCandidate, RejectedCandidate


# ---------------- AUTH ---------------- #

def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=email).exists():
            return render(request, "signup.html", {"error": "User already exists"})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        return redirect("dashboard")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- DASHBOARD ---------------- #

@login_required
def dashboard(request):
    context = {
        "shortlisted": ShortlistedCandidate.objects.count(),
        "hold": HoldCandidate.objects.count(),
        "rejected": RejectedCandidate.objects.count(),
    }
    return render(request, "dashboard.html", context)


@login_required
def shortlisted_view(request):
    data = ShortlistedCandidate.objects.all()
    return render(request, "shortlisted.html", {"data": data})


@login_required
def hold_view(request):
    data = HoldCandidate.objects.all()
    return render(request, "hold.html", {"data": data})


@login_required
def rejected_view(request):
    data = RejectedCandidate.objects.all()
    return render(request, "rejected.html", {"data": data})
