from django.shortcuts import render


def error404(request, exception):
    template_name = 'pages/404.html'
    return render(request, template_name)


def error403(request, exception):
    template_name = 'pages/403csrf.html'
    return render(request, template_name)


def error500(request):
    template_name = 'pages/500.html'
    return render(request, template_name)
