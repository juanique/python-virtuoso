###Introduction

This is a Virtuoso wrapper library for python. It wraps the `isql-vt` shell to perform load and delete data operations and uses the SPARQL endpoint to perform queries.

###Requirements

- python-webclient : https://github.com/juanique/python-webclient
- python-artichoke : https://github.com/juanique/artichoke (for unit testing)

###Usage

####SPARQL Query

    from virtuoso import Virtuoso

    #Init the triplestore with the host, username, password, endpoint port and endpoint
    #path
    triplestore = Virtuoso("localhost", "dba", "mypassword", 8890, "/sparql")

    results = triplestore.query("SELECT * WHERE {?s ?p ?o}")
    for row in results:
        print row["s"].value, row["p"].value, row["o"].value

####Insert and delete data

    from rdflib import Namespace, Literal

    graph = "http://my-graph"
    ns = Namespace("http://my-name-space.com/#")

    #Insert a triple into the triplestore
    # <http://my-name-space.com/#user123> <http://my-name-space.com/#user123>
    triplestore.insert(graph, ns["user123"], ns["name"], Literal("Juan"))

    #Deleting the triple just inserted
    triplestore.delete(graph, ns["user123"], ns["name"], Literal("Juan"))

    #Clean the whole graph
    triplestore.clean_graph(graph)
