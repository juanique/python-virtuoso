import unittest
from artichoke import Config
from virtuoso.endpoint import Endpoint
from virtuoso import ISQLWrapper
from testconfig import ISQLWrapperTestManager
from rdflib import Namespace, Literal


class DataTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config("local_test_config.ini",
            default_manager=ISQLWrapperTestManager())

        url = "http://%s:%s%s"
        url %= (self.config.host, self.config.endpoint_port,
            self.config.endpoint_path)

        self.endpoint = Endpoint(url)
        self.isql = ISQLWrapper(self.config.host, self.config.user,
            self.config.password)
        self.isql.execute_cmd("SPARQL CLEAR GRAPH <%s>" % self.config.graph)

    def assertGraphHasNumberOfTriples(self, n):
        sparql_query = "SELECT * FROM <%s> WHERE {?s ?p ?o}" % self.config.graph
        results = self.endpoint.query(sparql_query)
        self.assertEquals(results.total_rows, n)

    def assertGraphIsEmpty(self):
        self.assertGraphHasNumberOfTriples(0)

    def tearDown(self):
        self.config.save("local_test_config.ini")
        self.isql.execute_cmd("SPARQL CLEAR GRAPH <%s>" % self.config.graph)

    def test_delete_uri(self):
        "Inserts a triple into the triplestore"

        ns = Namespace("https://github.com/juanique/artichoke/ns#")
        graph = self.config.graph

        self.assertGraphIsEmpty()

        self.isql.insert(graph,
            ns["subject"], ns["predicate"], ns["object"])

        self.isql.delete(graph,
            ns["subject"], ns["predicate"], ns["object"])

        self.assertGraphIsEmpty()

    def test_delete_literal(self):
        "Inserts a triple into the triplestore"

        ns = Namespace("https://github.com/juanique/artichoke/ns#")
        graph = self.config.graph

        self.assertGraphIsEmpty()

        self.isql.insert(graph,
            ns["subject"], ns["predicate"], Literal("Hello"))

        self.isql.delete(graph,
            ns["subject"], ns["predicate"], Literal("Hello"))

        self.assertGraphIsEmpty()

    def test_insert(self):
        "Inserts a triple into the triplestore"

        ns = Namespace("https://github.com/juanique/artichoke/ns#")
        graph = self.config.graph

        self.isql.insert(graph,
            ns["subject"], ns["predicate"], ns["object"])

        query = "SELECT * FROM <%s> WHERE {?s ?p ?o}" % graph
        results = self.endpoint.query(query)

        self.assertGraphHasNumberOfTriples(1)
        self.assertEquals(results[0]['s'].value, str(ns["subject"]))
        self.assertEquals(results[0]['p'].value, str(ns["predicate"]))
        self.assertEquals(results[0]['o'].value, str(ns["object"]))

if __name__ == "__main__":
    unittest.main()
