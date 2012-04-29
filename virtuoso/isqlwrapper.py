import tempfile
import subprocess
import os
from rdflib import Graph

class ISQLWrapperException(Exception):
    pass

class ISQLWrapper(object):

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

    def clean_graph(self, graph_name):
        self.execute_cmd("SPARQL CLEAR GRAPH <%s>" % graph_name)

    def execute_script(self, script):
        cmd = ["isql-vt", self.hostname, self.username, self.password, script]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out, err = process.communicate()

        if err:
            raise ISQLWrapperException(err)

        return out

    def execute_cmd(self, cmd):
        if not cmd.endswith(";"):
            cmd = "%s;" % cmd
        #print ">>%s" % cmd

        tf_query = tempfile.NamedTemporaryFile()
        tf_query.write(cmd)
        tf_query.flush()
        result = self.execute_script(tf_query.name)
        tf_query.close()
        return result

    def sparql_query(self, query):
        if not query.endswith(";"):
            query = "%s;" % query

        return self.execute_cmd("SPARQL "+query)

    def load_file(self, filename, graph):
        cmd = "DB.DBA.RDF_LOAD_RDFXML_MT( file_to_string_output('%s'), '', '%s', 1 );"
        cmd %= (os.path.abspath(filename), graph)
        return self.execute_cmd(cmd)


    def insert(self, graph, subject_or_graph, p=None, o=None):
        if p is not None: #we have s, p, o
            s = subject_or_graph
            graph_data = Graph()
            graph_data.add((s,p,o))
            self.insert(graph, graph_data )
        else: #we have a graph
            graph_data = subject_or_graph
            tf_data = tempfile.NamedTemporaryFile()
            tf_data.write(graph_data.serialize(format='xml'))
            tf_data.flush()
            self.load_file(tf_data.name, graph)

    def delete(self, graph, triples, p = None, o = None):
        if p is not None:
            return self.delete(graph, [[triples,p,o]])

        for t in triples:
            sub, pred, obj = tuple(t)

            obj_is_uri = obj.__class__.__name__ == "URIRef"
            sub_is_uri = sub.__class__.__name__ == "URIRef"

            pred = "<%s>" % pred

            if sub_is_uri:
                sub = "<%s>" % sub

            if not obj_is_uri:
                obj_filter = "FILTER regex(?o, '^%s')" % obj
            else:
                obj = "<%s>" % obj
                obj_filter = "FILTER (?o = %s)" % obj


            #TODO: find a good way to delete literals!!
            sparql = """
                SPARQL DELETE FROM <%s>
                {?s ?p ?o}
                WHERE
                { ?s ?p ?o .
                        FILTER (?s = %s) .
                        FILTER (?p = %s) .
                        %s .
                };
                """ % (graph, sub, pred, obj_filter)

            self.execute_cmd(sparql)
