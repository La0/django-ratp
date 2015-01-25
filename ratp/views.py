from django.views.generic import ListView
from ratp.models import RatpLine


class RatpLinesView(ListView):
    '''
    List all lines and their stations
    '''
    template_name = 'ratp/lines.html'
    context_object_name = 'lines'

    def get_queryset(self):
        lines = RatpLine.objects.order_by('name')
        return lines
