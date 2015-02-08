# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from ratp.osm import OsmNode, OsmRelation, osm_load_ratp
import logging

logger = logging.getLogger('ratp')

class Command(BaseCommand):

    # All imported stations
    stations = {}

    def handle(self, stations=None, links=None, *args, **kwargs):

        # Load nodes
        network = 'metro' # Metro only to start
        xml = osm_load_ratp(network)
        for node in xml.findall('node'):
            n = OsmNode(xml=node)
            self.stations[n.osm_id] = n

        # Load relations
        for rel in xml.findall('relation'):
            self.build_relation(rel, network)

    def build_relation(self, xml, network):
        '''
        Parse a RATP relation between nodes
        '''
        relation = OsmRelation(xml=xml)

        # Only use routes
        if not relation.is_route:
            return

        # Build object in db
        line = relation.get_ratp_line(network)
        logger.info('Line: %s' % line)

        # Delete all links between stations & line
        line.links.all().delete()

        nodes = relation.list_nodes()
        for i, osm_id in enumerate(nodes):
            node = self.stations.get(osm_id)
            if not node:
                node = OsmNode(osm_id=osm_id)
            if not node.is_subway():
                continue

            try:
                # Build object in db
                station = node.get_ratp_station(network)

                logger.info('Station %s' % station)

                # Check station is not already in line
                if line.stations.filter(pk=station.pk).count() > 0:
                    raise Exception('Already in line')

                # Append station to line
                line.add_station(station)

            except Exception, e:
                logger.error('Node %d failure : %s' % (osm_id, e.message))
