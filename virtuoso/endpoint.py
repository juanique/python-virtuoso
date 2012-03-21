from xml.dom import minidom
from webclient import WebClient
import re, urllib


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

    def __getitem__(self, item):
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

    def __getitem__(self, item):
        return ResultRow(self.results[item])

    def __iter__(self):
        return self

    def next(self):
        if not self.can_read():
            raise StopIteration
        else:
            return self.get_row()


class Endpoint(object):

    def __init__(self, host, port=None, path=None):
        if not port and not path:
            matches = re.search("http://(\w+)(:\d+)?(.+)", host)
            host = matches.group(1)
            port = int(matches.group(2)[1:])
            path = matches.group(3)

        self.host = host
        self.path = path
        self.port = port

        self.webclient = WebClient(host=host, port=port)
        self.registered_namespaces = {}

    def register_namespace(self, prefix, namespace):
        self.registered_namespaces[prefix] = namespace

    def get_registered_namespaces_header(self):

        header_items = []
        for prefix, ns in self.registered_namespaces.items():
            ns_name = ns.encode()
            header_items.append('PREFIX %s: <%s>' % (prefix, ns_name))

        return '\n'.join(header_items)

    def get_full_path(self):
        return "http://%s:%s%s" % (self.host, self.port, self.path)

    @staticmethod
    def get_query_path(query, base_path, output):
        return "%s?query=%s&format=%s" % (base_path, urllib.quote(query), output)

    def query(self, query, output="ResultSet"):
        #print ">>%s" % query

        query = "%s\n%s" % (self.get_registered_namespaces_header(), query)

        if output == "ResultSet":
            request_format = "xml"
        else:
            request_format = output

        url = Endpoint.get_query_path(query, self.path, request_format)

        response = self.webclient.get(url)

        if output == 'ResultSet':
            return ResultSet(response.content)
        elif output == "json":
            return response.data
