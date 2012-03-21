import unittest
from artichoke import Config
from virtuoso.endpoint import Endpoint
from virtuoso import ISQLWrapper
from testconfig import ISQLWrapperTestManager
from rdflib import Namespace, Literal


class DataTestCae(unittest.TestCase):

    def setUp(self):
        self.config = Config("local_test_config.ini",
            default_manager=ISQLWrapperTestManager())

        url = "http://%s:%s%s"
        url %= (self.config.host, self.config.endpoint_port, self.config.endpoint_path)

        self.endpoint = Endpoint(url)
        self.isql = ISQLWrapper(self.config.host, self.config.user, self.config.password)
        self.isql.execute_cmd("SPARQL CLEAR GRAPH <%s>" % self.config.graph)


    def tearDown(self):
        self.config.save("local_test_config.ini")
        self.isql.execute_cmd("SPARQL CLEAR GRAPH <%s>" % self.config.graph)



    def test_delete_uri(self):
        "Inserts a triple into the triplestore"

        ns = Namespace("https://github.com/juanique/artichoke/ns#")
        graph = self.config.graph

        results = self.endpoint.query("SELECT * FROM <%s> WHERE {?s ?p ?o}" % graph)
        self.assertEquals(results.total_rows, 0)

        self.isql.insert(graph,
            ns["subject"], ns["predicate"], ns["object"])

        self.isql.delete(graph,
            ns["subject"], ns["predicate"], ns["object"])

        results = self.endpoint.query("SELECT * FROM <%s> WHERE {?s ?p ?o}" % graph)
        self.assertEquals(results.total_rows, 0)

    def test_delete_literal(self):
        "Inserts a triple into the triplestore"

        ns = Namespace("https://github.com/juanique/artichoke/ns#")
        graph = self.config.graph

        results = self.endpoint.query("SELECT * FROM <%s> WHERE {?s ?p ?o}" % graph)
        self.assertEquals(results.total_rows, 0)

        self.isql.insert(graph,
            ns["subject"], ns["predicate"], Literal("Hello"))

        self.isql.delete(graph,
            ns["subject"], ns["predicate"], Literal("Hello"))

        results = self.endpoint.query("SELECT * FROM <%s> WHERE {?s ?p ?o}" % graph)
        self.assertEquals(results.total_rows, 0)


    def test_insert(self):
        "Inserts a triple into the triplestore"

        ns = Namespace("https://github.com/juanique/artichoke/ns#")
        graph = self.config.graph

        self.isql.insert(graph,
            ns["subject"], ns["predicate"], ns["object"])
        results = self.endpoint.query("SELECT * FROM <%s> WHERE {?s ?p ?o}" % graph)

        self.assertEquals(results.total_rows, 1)
        self.assertEquals(results[0]['s'].value, str(ns["subject"]))
        self.assertEquals(results[0]['p'].value, str(ns["predicate"]))
        self.assertEquals(results[0]['o'].value, str(ns["object"]))

if __name__ == "__main__":
    unittest.main()
