from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home_view(request, *args, **kwargs):
    # return HttpResponse("<h1>Hello</h1>")
    return render(request, "home.html", {})

def instructions_view(request, *args, **kwargs):
    return render(request, "instructions.html", {})

def about_view(request, *args, **kwargs):
    return render(request, "about.html", {})