from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.POST.get("next") or "dashboard")
        messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login_signup.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Đăng ký thành công! Bạn đã được đăng nhập.")
            return redirect("dashboard")
        messages.error(request, "Có lỗi trong form đăng ký.")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/login_signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
