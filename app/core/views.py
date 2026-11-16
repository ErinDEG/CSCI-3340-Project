from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.

def home(request):
    return render(request, "homepage/home.html") #

def register(request):

    #existing users dont need to register again
    if request.user.is_authenticated:
        return redirect('home')


    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})