import unittest
from artichoke import Config
from virtuoso import ISQLWrapper, ISQLWrapperException
from testconfig import ISQLWrapperTestManager


class ISQLWrapperTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config("local_test_config.ini",
            default_manager=ISQLWrapperTestManager())

    def tearDown(self):
        self.config.save("local_test_config.ini")


class BasicTests(ISQLWrapperTestCase):

    def test_testsuite(self):
        self.assertEqual(2, 1+1);

    def test_init(self):
        "It is initalized by giving the server's hostname, username and pass."

        ISQLWrapper(self.config.host, self.config.user, self.config.password)


class CommandsTests(ISQLWrapperTestCase):

    def setUp(self):
        super(CommandsTests, self).setUp()
        self.isql = ISQLWrapper(self.config.host, self.config.user, self.config.password)

    def test_execute_script(self):
        "It can execute a given script"

        result = self.isql.execute_script("fixtures/status.sql")
        self.assertTrue(result.startswith("Connected to OpenLink Virtuoso"))

    def test_execute_bad_script(self):
        "Executing bad scripts should raise a ISQLWrapperException"

        self.assertRaises(ISQLWrapperException, self.isql.execute_script,
            "fixtures/bad_script.sql")

    def test_execute_cmd(self):
        "It can execute a given command string."

        result = self.isql.execute_cmd("status();")
        self.assertTrue(result.startswith("Connected to OpenLink Virtuoso"))

    def test_semicolon(self):
        "Final semicolon is optional"

        result = self.isql.execute_cmd("status()")
        self.assertTrue(result.startswith("Connected to OpenLink Virtuoso"))


if __name__ == "__main__":
    unittest.main()
