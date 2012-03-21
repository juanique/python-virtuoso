import tempfile
import urllib

from xml.dom import minidom
from subprocess import call
from rdflib import Graph, Namespace

NFO = Namespace('http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#')
NIE = Namespace('http://www.semanticdesktop.org/ontologies/2007/01/19/nie#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
CLIP = Namespace('http://www.rdfclip.com/resource/')
CLIPS = Namespace('http://www.rdfclip.com/schema#')
XMLS = Namespace('http://www.w3.org/2001/XMLSchema#')
UCHILE = Namespace('http://www.rdfclip.com/schema/uchile#')

registered_namespaces = {
        'nfo': NFO,
        'rdfs' : RDFS, 
        'rdf' : RDF,
        'clip' : CLIP,
        'clips' : CLIPS,
        'xmls' : XMLS,
        'nie' : NIE,
        'uchile' : UCHILE,
        }

hachoir_mapping = {
    'description' : RDFS['comment'],
    'duration' : NFO['duration'],
    'width' : NFO['horizontalResolution'],
    'height' : NFO['verticalResolution'],
    'frame_rate' : NFO['frameRate'],
    'bit_rate' : NFO['averageBitrate'],
    'comment' : RDFS['comment'],
    'compression' : NFO['codec'],
    'nb_channel' : NFO['channels'],
    'mime_type' : RDF['type'],

    #Classes by  mimetype
    'video/x-msvideo' : NFO['Video'],
}

def abbreviate(uri):
    for prefix, ns in registered_namespaces.items():
        ns_name = ns.encode()
        if uri[:len(ns_name)] == ns_name:
            return "%s:%s" % (prefix, uri[len(ns_name):])
    raise Exception("Tried to abbreviate an URI from an unregistered namespace (%s)." % uri)

class ResultValue:

    def __init__(self, dom):
        self.type = dom.tagName
        self.value = unicode(dom.firstChild.data)

class ResultRow:
    
    def __init__(self, dom):
        self.dom = dom
        dom_fields = self.dom.getElementsByTagName('binding')
        self.values = {}
        for element in dom_fields:
            name = element.getAttribute("name")
            dom_value = element.firstChild

            self.values[name] = ResultValue(dom_value)

    def __getitem__(self,item):
        return self.values[item]

    def get(self, item, default):
        try:
            return self[item]
        except KeyError:
            return default
    

class ResultSet:

    def __init__(self, data):
        self.dom = minidom.parseString(data)
        self.results = self.dom.getElementsByTagName('result')
        self.current_row = 0
        self.total_rows = len(self.results)

    def get_row(self):
        row = self.results[self.current_row]
        self.current_row += 1
        return ResultRow(row)

    def can_read(self):
        return self.current_row < self.total_rows

    def __iter__(self):
        return self

    def next(self):
        if not self.can_read():
            raise StopIteration
        else:
            return self.get_row()


class SparqlProxy:

    def __init__(self, default_endpoint='http://localhost:8890/sparql'):
        self.default_endpoint = default_endpoint

        header_items = []
        for prefix, ns in registered_namespaces.items():
            ns_name = ns.encode()
            header_items.append('prefix %s: <%s>' % (prefix, ns_name))

        self.namespaces_header = '\n'.join(header_items)


    def get_url(self,query, endpoint, output):
        return "%s?query=%s&format=%s" % (endpoint, urllib.quote(query), output)

    def query(self, query, endpoint=None, output='json', include_namespaces = True):
        if include_namespaces:
            query = "%s\n%s" % (self.namespaces_header, query)


        request_output = output
        if output == 'ResultSet':
            request_output = 'xml'

        if endpoint is None:
            endpoint = self.default_endpoint
       
        url = self.get_url(query, endpoint, request_output)

        data = url
        #TODO use webclient to implement this
        #open_url(url)
        if output == 'ResultSet':
            return ResultSet(data)
        return data

class PHPProxy(SparqlProxy):

    def __init__(self, proxy_url = 'http://localhost:8890/sparql', default_endpoint='http://localhost:8890/sparql'):
        self.proxy_url = proxy_url
        super(self, default_endpoint)

    def get_url(self, query, endpoint, output):
        return '%s?query=%s&service_uri=%s&output=%s' % (self.proxy_url, urllib.quote(query), urllib.quote(endpoint), urllib.quote(output))



class TripleStore:

    def __init__(self, hostname, username, password, work_dir):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.work_dir = work_dir

    def execute(self,script):
        call(["isql-vt", self.hostname, self.username, self.password, script])

    def load_file(self,filename, g):
        tf_query = tempfile.NamedTemporaryFile(dir=self.work_dir)
        virtuoso_command = "DB.DBA.RDF_LOAD_RDFXML_MT( file_to_string_output('%s'), '', '%s', 1 );" % (filename, g)
        tf_query.write(virtuoso_command)
        tf_query.flush()
        self.execute(tf_query.name)
        tf_query.close()

    def query(self, q):
        tf_query = tempfile.NamedTemporaryFile(dir=self.work_dir)
        tf_query.write(q)
        tf_query.flush()
        self.execute(tf_query.name)
        tf_query.close()

    def insert(self, g, data, p = None, o = None):
        if p is not None:
            s = data
            graph_data = Graph()
            graph_data.add((s,p,o))
            self.insert(g, graph_data )
        else:
            tf_data = tempfile.NamedTemporaryFile(dir=self.work_dir)
            tf_data.write(data.serialize(format='xml'))
            tf_data.flush()
            self.load_file(tf_data.name, g)

    def delete(self, g, triples, p = None, o = None):
        if p is not None:
            return self.delete([[triples,p,o]])

        for t in triples:
            if (isinstance(t[2],str) or isinstance(t[2],unicode)) and t[2][0] != '<':
                c = "FILTER regex(?o, '%s')" % t[2]
            else:
                c = "FILTER (?o = %s)" % t[2]

            #TODO: find a good way to delete literals!!
            sparql = """
                SPARQL MODIFY GRAPH <http://www.rdfclip.com/data>
                DELETE { ?s ?p ?o}
                INSERT {}
                FROM <http://www.rdfclip.com/data>
                WHERE
                { ?s ?p ?o .
                        FILTER (?s = %s) .
                        FILTER (?p = %s) .
                        %s . };
                """ % (t[0],t[1],c)
            self.query(sparql)
