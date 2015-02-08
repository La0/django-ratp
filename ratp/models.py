# coding=utf-8
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _


RATP_NETWORKS = (
  ('metro', _('Metro')),
  ('rer', _('RER')),
  ('bus', _('Bus')),
)


class RatpLine(models.Model):
    '''
    Represents a transport line, full of stations
    Unique name & network
    '''
    name = models.CharField(max_length=50)
    network = models.CharField(max_length=10, choices=RATP_NETWORKS)
    color = models.CharField(max_length=6, default="ffffff") # Html colour code

    class Meta:
        unique_together = (('name', 'network'), )

    def __unicode__(self):
        return u'%s %s' % (self.network, self.name)

    @property
    def links_ordered(self):
        return self.links.order_by('order')

    def add_station(self, station, order=None):
        '''
        Add a station to this line
        Append when no order given
        '''
        if order is None:
            agg = self.links.aggregate(max_order=models.Max('order'))
            order = agg['max_order'] is not None and agg['max_order'] + 1 or 0
        return RatpLink.objects.create(line=self, station=station, order=order)


class RatpStation(models.Model):
    '''
    Ratp station, on one of the following network:
     * metro (subway)
     * rer (suburb train)
     * bus
    '''
    osm_id = models.BigIntegerField(unique=True)
    ratp_id = models.IntegerField(null=True, blank=True)
    network = models.CharField(max_length=10, choices=RATP_NETWORKS)
    name = models.CharField(max_length=255)
    zone = models.IntegerField(default=1)
    lines = models.ManyToManyField(RatpLine, through='ratp.RatpLink', related_name='stations')
    position = models.PointField() # GPS position

    def __unicode__(self):
        return u'%s: %s' % (self.network, self.name)


class RatpLink(models.Model):
    '''
    A link between a station and a line
    Any station can be on multiple lines
    '''
    line = models.ForeignKey(RatpLine, related_name='links')
    station = models.ForeignKey(RatpStation, related_name='links')
    order = models.IntegerField(default=0)

    # Reachable neighbors
    neighbors = models.ManyToManyField(RatpStation)

    class Meta:
      ordering = ('order', )
