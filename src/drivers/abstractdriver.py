## ==============================================
## AbstractDriver
## ==============================================
class AbstractDriver(object):
    def __init__(self, name, conf, sys_params):
        self.name = name
        self.config = conf
        self.sys_params = sys_params
        self.sys_params_type = len(self.sys_params)
        self.sys_params_space = [len(specific_parameter) for specific_parameter in self.sys_params]

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

    def build_index_command(self, index_to_create):
        """build index command"""
        return None

    def set_system_parameter(self, parameter_sql):
        """switch system parameters"""
        self.cursor.execute(parameter_sql)
        # self.conn.commit()

    def change_system_parameter(self, parameter_choices):
        for i in range(self.sys_params_type):
            parameter_choice = int(parameter_choices[i])
            parameter_change_sql = self.sys_params[i][parameter_choice]
            print(parameter_change_sql)
            self.set_system_parameter(parameter_change_sql)

    def get_system_parameter_command(self, parameter_type, parameter_value):
        return self.sys_params[parameter_type][parameter_value]

    def get_system_parameter_space(self):
        return self.sys_params_space

## CLASS
