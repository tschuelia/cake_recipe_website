from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, "recipes/404.html",)


def permission_denied(request, exception):
    return render(request, "recipes/403.html")
