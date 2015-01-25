from django.conf.urls import patterns, url
from ratp import views

urlpatterns = patterns('',

    # List all lines
    url(r'^/?$', views.RatpLinesView.as_view(), name='lines'),
)
