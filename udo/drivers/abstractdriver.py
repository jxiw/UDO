# -----------------------------------------------------------------------
# Copyright (c) 2021    Cornell Database Group
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import logging

class AbstractDriver(object):
    def __init__(self, driver_name, conf, sys_params):
        self.driver_name = driver_name
        self.config = conf
        self.sys_params = sys_params
        self.sys_params_type = len(self.sys_params)
        self.sys_params_space = [len(specific_parameter) for specific_parameter in self.sys_params]

    def __str__(self):
        return self.driver_name

    def connect(self):
        """connect to a DBMS"""
        raise NotImplementedError("%s does not implement connect function" % (self.driver_name))

    def run_queries_with_timeout(self, query_list, timeout):
        """run queries with specific timeout"""
        raise NotImplementedError("%s does not implement run queries with timeout function" % (self.driver_name))

    def run_queries_without_timeout(self, query_list):
        """run queries without specific timeout"""
        raise NotImplementedError("%s does not implement run queries without timeout function" % (self.driver_name))

    def build_index(self, index_creation_sql):
        """build index via SQL"""
        raise NotImplementedError("%s does not implement build index function" % (self.driver_name))

    def drop_index(self, index_drop_sql):
        """drop index via SQL"""
        raise NotImplementedError("%s does not implement drop index function" % (self.driver_name))

    def build_index_command(self, index_to_create):
        """build index command"""
        return None

    def set_system_parameter(self, parameter_sql):
        """switch system parameters via SQL"""
        raise NotImplementedError("%s does not implement set system parameter function" % (self.driver_name))

    def change_system_parameter(self, parameter_choices):
        """change system parameter values using the input parameter choices"""
        for i in range(self.sys_params_type):
            parameter_choice = int(parameter_choices[i])
            parameter_change_sql = self.sys_params[i][parameter_choice]
            logging.info(f"{parameter_change_sql}")
            self.set_system_parameter(parameter_change_sql)

    def get_system_parameter_command(self, parameter_type, parameter_value):
        """get the system parameter command based on the parameter_type and its value"""
        return self.sys_params[parameter_type][parameter_value]

    def get_system_parameter_space(self):
        """return the search space of system parameter"""
        return self.sys_params_space

## CLASS
