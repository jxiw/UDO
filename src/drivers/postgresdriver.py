from __future__ import with_statement

import logging
import time

import psycopg2
from psycopg2._psycopg import InternalError
from psycopg2._psycopg import QueryCanceledError

from .abstractdriver import *


# the DBMS connector for Postgres
class PostgresDriver(AbstractDriver):

    def __init__(self, conf, sys_params):
        super(PostgresDriver, self).__init__("postgres", conf, sys_params)

    ## connect to database system
    def connect(self):
        # config to connect dbms
        self.conn = psycopg2.connect("dbname='%s' user='%s'" % (self.config["db"], self.config["user"]))
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        self.index_creation_format = "CREATE INDEX %s ON %s (%s);"
        self.index_drop_format = "drop index %s;"
        self.is_cluster = True
        self.retrieve_table_name_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        self.cardinality_format = "select count(*) from %s;"
        self.cluster_indices_format = "CLUSTER %s ON %s;"

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
                # print("query sql:", query_sql)
                # print("current timeout:", current_timeout)
                current_timeout = current_timeout
                self.cursor.execute("set statement_timeout=%d" % (current_timeout * 1000))
                start_time = time.time()
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
            except QueryCanceledError:
                # print("timeout")
                duration = current_timeout
            except InternalError:
                # error to run the query, set duration to a large number
                print("Internal Error for query%s" % query_sql)
                duration = current_timeout * 1000
            # print("duration:", duration)
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
            self.cursor.execute(self.cluster_indices_format % (index_to_create[0], index_to_create[1]))
        # self.conn.commit()

    def build_index_command(self, index_to_create):
        """build index"""
        index_sql = self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2])
        cluster_sql = self.cluster_indices_format % (index_to_create[0], index_to_create[1])
        return f"{index_sql} \n {cluster_sql}"

    def drop_index(self, index_to_drop):
        """drop index"""
        index_sql = self.index_drop_format % (index_to_drop[0])
        logging.debug("drop index %s", index_sql)
        self.cursor.execute(index_sql)
        # self.conn.commit()

    # def get_system_parameter_command(self, parameter_type, parameter_value):
    #     return self.sys_params[parameter_type][parameter_value]

## CLASS
