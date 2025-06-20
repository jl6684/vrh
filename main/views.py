from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def assortments(request):
    return render(request, 'assortments.html')

def band(request):
    return render(request, 'band.html')

def contact(request):
    return render(request, 'contact.html')

def female(request):
    return render(request, 'female.html')

def male(request):
    return render(request, 'male.html')

def others(request):
    return render(request, 'others.html')

def recycling(request):
    return render(request, 'recycling.html')

def terms_and_conditions(request):
    return render(request, 't&c.html')
