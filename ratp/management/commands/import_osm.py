# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from ratp.models import RatpStation, RatpLine, RatpLink
from ratp.osm import OsmNode, OsmRelation, osm_load_ratp

class Command(BaseCommand):

    # All imported stations
    stations = {}

    def handle(self, stations=None, links=None, *args, **kwargs):

        # Load nodes
        xml = osm_load_ratp('metro') # Metro only to start
        for node in xml.findall('node'):
            n = OsmNode(xml=node)
            self.stations[n.osm_id] = n

        print 'Loaded %d stations' % (len(self.stations),)

        # Load relations
        for rel in xml.findall('relation'):
            self.build_relation(rel)


    def build_relation(self, xml):
        '''
        Parse a RATP relation between nodes
        '''
        relation = OsmRelation(xml=xml)

        # Only use routes
        if not relation.is_route:
            return

        print '-' * 80
        print 'Relation: %s' % relation
        from pprint import pprint
        pprint(relation.tags)
        for osm_id in relation.list_nodes():
            station = self.stations.get(osm_id)
            if not station:
                station = OsmNode(osm_id=osm_id)

            print ' > Node %s' % station
