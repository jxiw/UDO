from __future__ import with_statement

import logging
import MySQLdb
import time
from .mysqlsysparams import mysql_candidate_dbms_parameter

from .abstractdriver import *

# the DBMS connector for MySQL
class MysqlDriver(AbstractDriver):

    def __init__(self, conf):
        super(MysqlDriver, self).__init__("mysql", conf)

    ## connect to database system
    def connect(self):
        # config to connect dbms
        # config = {
        #     "host": "127.0.0.1",
        #     "port": 3306,
        #     "db": "tpch",
        #     # "db": "imdb",
        #     "user": "jw2544",
        #     "passwd": "jw2544"
        # }

        self.conn = MySQLdb.connect(self.config['host'], self.config['user'], self.config['passwd'], self.config['db'])
        self.cursor = self.conn.cursor()
        self.index_creation_format = "CREATE INDEX %s ON %s (%s) USING BTREE;"
        self.index_drop_format = "ALTER TABLE %s drop index %s;"
        self.is_cluster = True
        self.sys_params = mysql_candidate_dbms_parameter
        self.sys_params_space = [len(specific_parameter) for specific_parameter in self.sys_params]
        self.retrieve_table_name_sql = "show tables;"
        self.cardinality_format = "select count(*) from %s;"

    def cardinalities(self):
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
                print(oe)
                print("timeout")
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
        # run queries without timeout
        return self.run_queries_with_timeout(query_list, [0 for query in query_list])

    def build_index(self, index_to_create):
        """build index"""
        # logging.debug("create index %s" % index_to_create)
        self.cursor.execute(self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2]))
        self.conn.commit()

    def drop_index(self, index_to_drop):
        """drop index"""
        # logging.debug("drop index %s" % index_to_drop)
        self.cursor.execute(self.index_drop_format % (index_to_drop[1], index_to_drop[0]))
        self.conn.commit()

    def change_system_parameter(self, parameter_choices):
        for i in range(self.sys_params_type):
            parameter_choice = int(parameter_choices[i])
            parameter_change_sql = self.sys_params[i][parameter_choice]
            print(parameter_change_sql)
            self.set_system_parameter(parameter_change_sql)

    def set_system_parameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        self.conn.commit()

## CLASS
