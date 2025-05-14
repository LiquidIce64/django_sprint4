from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


class Registration(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = '/profile/'

    def form_valid(self, form):
        res = super().form_valid(form)
        login(self.request, self.object)
        return res
