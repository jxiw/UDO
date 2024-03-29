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

import json
import re
import time

import MySQLdb

from .abstractdriver import *


class MysqlDriver(AbstractDriver):
    """the DBMS driver for MySQL"""

    def __init__(self, conf, sys_params):
        super(MysqlDriver, self).__init__("mysql", conf, sys_params)

    def connect(self):
        """connect to a database"""
        self.conn = MySQLdb.connect(self.config['host'], self.config['user'], self.config['passwd'], self.config['db'])
        self.cursor = self.conn.cursor()
        self.index_creation_format = "CREATE INDEX %s ON %s (%s) USING BTREE;"
        self.index_drop_format = "ALTER TABLE %s drop index %s;"
        # self.is_cluster = True
        self.sys_params_type = len(self.sys_params)
        self.sys_params_space = [len(specific_parameter) for specific_parameter in self.sys_params]
        self.retrieve_table_name_sql = "show tables;"
        self.cardinality_format = "select count(*) from %s;"
        self.innodb_buffer_pattern = re.compile("set global innodb_buffer_pool_size = (.*);")
        self.select_innodb_buffer_value_sql = "select @@innodb_buffer_pool_size;"

    def cardinalities(self):
        """get cardinality of the connected database"""
        self.cursor.execute(self.retrieve_table_name_sql)
        dbms_tables = []
        cardinality_info = {}
        for (table_name,) in self.cursor:
            dbms_tables.append(table_name)
        for table in dbms_tables:
            self.cursor.execute(self.cardinality_format % table)
            result = self.cursor.fetchone()
            cardinality = result[0]
            cardinality_info[table] = cardinality
        return cardinality_info

    def run_queries_with_timeout(self, query_list, timeout):
        """run queries with a timeout"""
        run_time = []
        for query_sql, current_timeout in zip(query_list, timeout):
            try:
                current_timeout = current_timeout
                self.cursor.execute("SET SESSION MAX_EXECUTION_TIME=%d" % (current_timeout * 1000))
                start_time = time.time()
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
                print("query run:%s" % duration)
            except MySQLdb.OperationalError as oe:
                # print(oe)
                # print("timeout")
                duration = current_timeout
            run_time.append(duration)
        print(run_time)
        # reset back to default configuraiton
        try:
            self.cursor.execute("SET SESSION MAX_EXECUTION_TIME=0")
            self.cursor.execute("drop view if exists REVENUE0;")
        except MySQLdb.OperationalError as oe:
            print(oe)
        return run_time

    def run_queries_without_timeout(self, query_list):
        """run queries without timeout"""
        return self.run_queries_with_timeout(query_list, [0 for query in query_list])

    def build_index(self, index_to_create):
        """build index"""
        index_sql = self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2])
        logging.debug(f"create index {index_sql}")
        self.cursor.execute(index_sql)
        self.conn.commit()

    def build_index_command(self, index_to_create):
        """build index command"""
        index_sql = self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2])
        return index_sql

    def drop_index(self, index_to_drop):
        """drop index"""
        index_sql = self.index_drop_format % (index_to_drop[1], index_to_drop[0])
        logging.debug(f"drop index {index_sql}")
        self.cursor.execute(index_sql)
        self.conn.commit()

    def change_system_parameter(self, parameter_choices):
        """change system parameter values using the input parameter choices"""
        for i in range(self.sys_params_type):
            parameter_choice = int(parameter_choices[i])
            parameter_change_sql = self.sys_params[i][parameter_choice]
            self.set_system_parameter(parameter_change_sql)
            if "innodb_buffer_pool_size" in parameter_change_sql:
                # wait finish until it get effective
                value_to_change = int(self.innodb_buffer_pattern.findall(parameter_change_sql)[0])
                # verify whether the value is changed or not
                while True:
                    self.cursor.execute(self.select_innodb_buffer_value_sql)
                    current_value = (self.cursor.fetchall())[0][0]
                    if value_to_change == current_value:
                        break
                    else:
                        time.sleep(3)
                        self.set_system_parameter(parameter_change_sql)

    def set_system_parameter(self, parameter_sql):
        """switch system parameters"""
        try:
            logging.debug(f"set system parameter {parameter_sql}")
            self.cursor.execute(parameter_sql)
            self.conn.commit()
        except MySQLdb.OperationalError as oe:
            print(oe)

    def analyze_queries_cost(self, query_sqls):
        """analyze cost of queries"""
        total_cost = []
        for analyze_sql in query_sqls:
            analyze_sql = f"EXPLAIN FORMAT=JSON {analyze_sql}"
            self.cursor.execute(analyze_sql)
            plan = json.loads((self.cursor.fetchone())[0])
            total_cost.append(float(plan['query_block']['cost_info']['query_cost']))
        logging.info(f"estimate costs {total_cost}")
        return total_cost

    def close(self):
        """close the connection"""
        self.cursor.close()
        self.conn.close()

## CLASS
