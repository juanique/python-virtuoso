from artichoke import DefaultManager
from artichoke.helpers import read

class ISQLWrapperTestManager(DefaultManager):

    def Global__host(self):
        query = "Select test virtuso host"
        default = "localhost"

        return read(query, default=default)

    def Global__user(self):
        query = "Select test virtuso user"
        default = "dba"

        return read(query, default=default)

    def Global__password(self):
        query = "Select test virtuso password"
        return read(query)

    def Global__graph(self):
        query = "Select test graph name"
        default = "https://github.com/juanique/artichoke/test"

        return read(query, default=default)

    def Global__endpoint_port(self):
        query = "Select endpoint port"
        default = 8890

        return read(query, default=default)

    def Global__endpoint_path(self):
        query = "Select endpoint path"
        default = "/sparql"

        return read(query, default=default)
