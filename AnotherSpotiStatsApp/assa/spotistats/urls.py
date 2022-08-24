from django.urls import path
from assa.spotistats.views import spotistats_view, auth

app_name = "spotistats"
urlpatterns = [
    path('', spotistats_view, name='spotistats'),
    path('auth', auth, name='auth'),
]
