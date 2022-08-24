from django.views.generic import TemplateView
from assa.spotistats.models import SpotiStats
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


class SpotiStatsView(LoginRequiredMixin, TemplateView):
    model = SpotiStats
    template_name = "spotistats/spotistats.html"


spotistats_view = SpotiStatsView.as_view()


def auth(request):
    # https://stackoverflow.com/a/57071533
    if not request.user.is_authenticated:
        return render(request, "account/login.html")
    else:  # nobody gets here unless they log in
        data = SpotiStats.objects.all()
        return render(request, "spotistats/api/auth.html", {'auth': data})
