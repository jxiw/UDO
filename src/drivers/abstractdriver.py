## ==============================================
## AbstractDriver
## ==============================================
class AbstractDriver(object):
    def __init__(self, name, conf):
        self.name = name
        self.config = conf
        
    def __str__(self):
        return self.driver_name

    def connect(self):
        """connect to a DBMS"""
        return None

    def run_queries_with_timeout(self, query_list, timeout):
        """run queries with specific timeout"""
        return None

    def run_queries_without_timeout(self, query_list):
        """run queries without specific timeout"""
        return None

    def build_index(self, index_creation_sql):
        """build index"""
        return None

    def drop_index(self, index_drop_sql):
        """drop index"""
        return None

    def set_system_parameter(self, parameter_sql):
        """switch system parameters"""
        return None

    def change_system_parameter(self, parameter_choices):
        return None

    def get_system_parameter_space(self):
        """get the space of system parameters"""
        return None

## CLASS