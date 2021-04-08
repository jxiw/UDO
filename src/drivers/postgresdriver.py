from __future__ import with_statement

import logging
import psycopg2
import time
from .postgressysparams import pg_candidate_dbms_parameter

from psycopg2._psycopg import QueryCanceledError
from .abstractdriver import *

# the DBMS connector for Postgres
class PostgresDriver(AbstractDriver):

    def __init__(self, conf):
        super(PostgresDriver, self).__init__("postgres", conf)

    ## connect to database system
    def connect(self):
        # config to connect dbms
        self.conn = psycopg2.connect("dbname='%s' user='%s'" % (self.config["db"], self.config["user"]))
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        self.index_creation_format = "CREATE INDEX %s ON %s (%s);"
        self.index_drop_format = "drop index %s;"
        self.is_cluster = True
        self.sys_params = pg_candidate_dbms_parameter
        self.sys_params_type = len(self.sys_params)
        self.sys_params_space = [len(specific_parameter) for specific_parameter in self.sys_params]
        self.retrieve_table_name_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        self.cardinality_format = "select count(*) from %s;"

    def cardinalities(self):
        self.cursor.execute(self.retrieve_table_name_sql)
        dbms_tables = []
        cardinality_info = {}
        for table in self.cursor.fetchall():
            dbms_tables.append(table)
        for table in dbms_tables:
            self.cursor.execute(self.cardinality_format % table)
            result = self.cursor.fetchone()
            cardinality = result[0]
            cardinality_info[table[0].lower()] = cardinality
        return cardinality_info

    def run_queries_with_timeout(self, query_list, timeout):
        run_time = []
        for query_sql, current_timeout in zip(query_list, timeout):
            try:
                current_timeout = current_timeout
                self.cursor.execute("set statement_timeout=%d" % (current_timeout * 1000))
                start_time = time.time()
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
            except QueryCanceledError:
                print("timeout")
                duration = current_timeout
            run_time.append(duration)
        # reset the timeout to the default configuration
        self.cursor.execute("set statement_timeout=0;")
        self.cursor.execute("drop view if exists REVENUE0;")
        print(run_time)
        return run_time

    def run_queries_without_timeout(self, query_list):
        return self.run_queries_with_timeout(query_list, [0 for query in query_list])

    def build_index(self, index_to_create):
        """build index"""
        index_sql = self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2])
        logging.debug("create index %s", index_sql)
        self.cursor.execute(index_sql)
        # if we consider the cluster indices
        if self.is_cluster:
            cluster_indices_format = "CLUSTER %s ON %s"
            self.cursor.execute(cluster_indices_format % (index_to_create[0], index_to_create[1]))
        # self.conn.commit()

    def drop_index(self, index_to_drop):
        """drop index"""
        index_sql = self.index_drop_format % (index_to_drop[0])
        logging.debug("drop index %s", index_sql)
        self.cursor.execute(index_sql)
        # self.conn.commit()

    def set_system_parameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        # self.conn.commit()

    def change_system_parameter(self, parameter_choices):
        for i in range(self.sys_params_type):
            parameter_choice = int(parameter_choices[i])
            parameter_change_sql = self.sys_params[i][parameter_choice]
            print(parameter_change_sql)
            self.set_system_parameter(parameter_change_sql)

    def get_system_parameter_space(self):
        return self.sys_params_space

## CLASS
