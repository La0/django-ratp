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
    Unique name & direction
    '''
    name = models.CharField(max_length=50)
    direction = models.CharField(max_length=255)
    network = models.CharField(max_length=10, choices=RATP_NETWORKS)

    class Meta:
        unique_together = (('name', 'direction'), )

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.direction)

    @property
    def links_ordered(self):
        return self.links.order_by('order')


class RatpStation(models.Model):
    '''
    Ratp station, on one of the following network:
     * metro (subway)
     * rer (suburb train)
     * bus
    '''
    ratp_id = models.IntegerField(unique=True)
    network = models.CharField(max_length=10, choices=RATP_NETWORKS)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    lines = models.ManyToManyField(RatpLine, through='ratp.RatpLink', related_name='stations')
    position = models.PointField()

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

    class Meta:
      ordering = ('order', )
