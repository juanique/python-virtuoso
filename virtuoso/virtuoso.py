from endpoint import Endpoint
from isqlwrapper import ISQLWrapper

class Virtuoso(object):

    def __init__(self, hostname, username, password, port_or_endpoint=None, path=None):
        self.isql = ISQLWrapper(hostname, username, password)

        if type(port_or_endpoint) == str: #full endpoint path
            self.endpoint = Endpoint(port_or_endpoint)
        elif type(port_or_endpoint) == int: #just the port
            self.endpoint = Endpoint(hostname, port_or_endpoint, path)
        else:
            raise Exception("Incorrect endpoint url or port.")

    def query(self, *args, **kwargs):
        return self.endpoint(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.isql.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.isql.delete(*args, **kwargs)

    def clean_graph(self, *args, **kwargs):
        return self.isql.clea_graph(*args, **kwargs)
