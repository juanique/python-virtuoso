import unittest
from artichoke import Config
from virtuoso.endpoint import Endpoint, ResultSet
from testconfig import ISQLWrapperTestManager
from rdflib import Namespace


class EndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config("local_test_config.ini",
            default_manager=ISQLWrapperTestManager())

    def tearDown(self):
        self.config.save("local_test_config.ini")

class EndpointInitTests(EndpointTestCase):

    def test_init(self):
        "It is initialized using a given host, port and path"

        Endpoint(self.config.host, self.config.endpoint_port, self.config.endpoint_path)

    def test_init_auto(self):
        "It can be initialized using a string containing the endpoints host, port and path"

        url = "http://%s:%s%s"
        url %= (self.config.host, self.config.endpoint_port, self.config.endpoint_path)

        endpoint = Endpoint(url)

        self.assertEquals(endpoint.host, self.config.host)
        self.assertEquals(endpoint.port, self.config.endpoint_port)
        self.assertEquals(endpoint.path, self.config.endpoint_path)
        self.assertEquals(endpoint.get_full_path(), url)

class QueryTests(EndpointTestCase):

    def setUp(self):
        super(QueryTests, self).setUp()
        url = "http://%s:%s%s"
        url %= (self.config.host, self.config.endpoint_port, self.config.endpoint_path)

        self.endpoint = Endpoint(url)

    def test_register_namespace(self):
        "It can register a namespace to remember accross all queries"

        nfo_base_uri = 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#'
        NFO = Namespace(nfo_base_uri)
        self.endpoint.register_namespace("nfo", NFO)

        self.assertEquals(self.endpoint.get_registered_namespaces_header(),
                "PREFIX nfo: <%s>" % nfo_base_uri)


    def test_graph_query(self):
        sparql = "SELECT ?g WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g"
        results = self.endpoint.query(sparql)
        self.assertTrue(isinstance(results, ResultSet))

        for result in results:
            if result['g'].value == "http://www.openlinksw.com/schemas/virtrdf#":
                return

        self.assertTrue(False, "Could not find virutoso schema graph")


if __name__ == "__main__":
    unittest.main()
