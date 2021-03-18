## ==============================================
## AbstractDriver
## ==============================================
class AbstractDriver(object):
    def __init__(self, name, ddl):
        self.name = name
        self.driver_name = "%sDriver" % self.name.title()
        self.ddl = ddl
        
    def __str__(self):
        return self.driver_name

    def connect(self):
        """connect to a DBMS"""
        return None

    def runQueriesWithTimeout(self, query_list, timeout):
        """run queries with specific timeout"""
        return None

    def runQueriesWithoutTimeout(self, query_list):
        """run queries without specific timeout"""
        return None

    def buildIndex(self, index_creation_sql):
        """build index"""
        return None

    def dropIndex(self, index_drop_sql):
        """drop index"""
        return None

    def setSystemParameter(self, parameter_sql):
        """switch system parameters"""
        return None

    def getSystemParameterSpace(self):
        """get the space of system parameters"""
        return None

## CLASS