from django.shortcuts import render


def about_view(request):
    """ A view to return the about page """
    return render(request, 'about/about.html', {'active_link': 'about'})