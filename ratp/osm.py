import xml.etree.ElementTree as ET
import requests
from django.contrib.gis.geos import Point

# OSM config
XAPI_URL = 'http://open.mapquestapi.com/xapi/api/0.6/*[type:RATP=%s]'
OSM_URL = 'http://www.openstreetmap.org/api/0.6'

def osm_load(url):
    '''
    Helper to download an OpenStreetMap xml
    '''
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('Invalid xapi source')
    return ET.fromstring(resp.content)

def osm_load_ratp(ratp_type):
    '''
    Load OpenStreetMap xml defined objects
    which belongs to the RATP type
    '''
    return osm_load(XAPI_URL % ratp_type)

class OsmBase:
    osm_id = None
    osm_prefix = None
    xml = None

    # Data
    tags = {}

    def __init__(self, osm_id=None, xml=None):
        self.osm_id = osm_id

        if xml is not None:
            # Use xml data
            self.xml = xml
        elif osm_id is not None:
            # Load from OSM
            url = '%s/%s/%d' % (OSM_URL, self.osm_prefix, self.osm_id)
            self.xml = osm_load(url).find(self.osm_prefix)

        # Always parse
        self.parse()

    def parse(self):
        if self.xml is None:
            raise Exception('Missing xml source')

        # Load tags
        self.tags = dict([(t.attrib['k'], t.attrib['v']) for t in self.xml.findall('tag')])

        # Use id
        self.osm_id = int(self.xml.attrib['id'])

class OsmNode(OsmBase):
    '''
    Represents a single OpenStreetMap node
    usually a station stop for this app
    '''
    osm_prefix = 'node'

    def __str__(self):
      return self.tags.get('name', 'Node #%d' % self.osm_id)

    @property
    def point(self):
        return Point()

class OsmRelation(OsmBase):
    '''
    Represents a relationship between
    OpenStreetMap nodes
    '''
    osm_prefix = 'relation'

    def __str__(self):
      if 'from' in self.tags and 'to' in self.tags:
          return '%s - %s' % (self.tags['from'], self.tags['to'])
      return self.tags.get('name', 'Relation #%d' % self.osm_id)

    @property
    def is_route(self):
        return self.tags.get('type') == 'route'

    def list_nodes(self):
        # List the nodes needed
        return [int(node.attrib['ref']) for node in self.xml.findall('member[@type="node"]')]
