from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, "homepage/home.html") #

def register(request):
    pass

def events(request):
    return render(request, "events/index.html")

# def lostfound(request):
#     return render(request, lost_found/"index.html")