from django.shortcuts import render
from django.http import HttpResponse

recipes = [
    {
        'categorie': 'Torten',
        'title' : 'Käse-Sahne-Torte',
        'ingredients': 'Sahne, Quark',
        'making': 'Zeug zusammen rühren, backen',
        'time': '3 Stunden'
    },
    {
        'categorie': 'Kuchen',
        'title' : 'Apple Pie',
        'ingredients': 'Äpfel',
        'making': 'Zeug zusammen rühren, backen',
        'time': '1 Stunde'
    }
]

def home(request):
    context = {
        'recipes': recipes
    }
    return render(request, 'recipes/home.html', context)


def about(request):
    return render(request, 'recipes/about.html', {'title': 'About'})
