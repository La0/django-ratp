# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from ratp.models import RatpStation, RatpLine, RatpLink
from django.contrib.gis.geos import Point
import os
import re
import csv

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--stations',
            action='store',
            dest='stations',
            type='string',
            default=None,
            help='CSV file listing all RATP stations.'
        ),
        make_option('--links',
            action='store',
            dest='links',
            type='string',
            default=None,
            help='CSV file listing all RATP links between lines & stations.'
        )
    )

    def handle(self, stations=None, links=None, *args, **kwargs):
        # Check files exist
        if not stations or not os.path.exists(stations):
            raise CommandError('Invalid stations file.')
        if not links or not os.path.exists(links):
            raise CommandError('Invalid links file.')

        # Load stations
        if False:
          with open(stations, 'rb') as csvfile:
              reader = csv.reader(csvfile, delimiter='#')
              for line in reader:
                  self.build_station(*line)

        # Load links
        with open(links, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter='#')
            for line in reader:
                try:
                    self.build_link(*line)
                except Exception, e:
                    print 'Link failed: %s' % e

    def build_station(self, ratp_id, lat, lng, name, city, network):
        '''
        Build RATP Station from official CSV file input
        '''
        defaults = {
            'name' : name,
            'city' : city,
            'position' : Point(float(lat), float(lng)),
            'network' : network,
        }
        station, _ = RatpStation.objects.get_or_create(ratp_id=ratp_id, defaults=defaults)
        return station


    def build_link(self, ratp_id, line_direction, network):
      '''
      Build an RATP link between a station and a line
      Will create lines when needed
      '''
      # Extract line & directions
      regex = r'(\w+) \((.+)\)'
      res = re.match(regex, line_direction)
      if not res:
          raise Exception('No line/direction extracted')
      line_name, direction = res.groups()

      # Get Ratp line
      line, _ = RatpLine.objects.get_or_create(name=line_name, direction=direction)

      # Get station
      station = RatpStation.objects.get(ratp_id=ratp_id)

      # Build a link
      order = line.stations.count()
      defaults = {
        'order' : order,
      }
      link, created = RatpLink.objects.get_or_create(line=line, station=station, defaults=defaults)
      if not created and link.order != order:
          link.order = order
          link.save()

      return link
