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
import time

import psycopg2
from psycopg2._psycopg import InternalError
from psycopg2._psycopg import QueryCanceledError

from .abstractdriver import *

class PostgresDriver(AbstractDriver):
    """the DBMS driver for Postgres"""

    def __init__(self, conf, sys_params):
        super(PostgresDriver, self).__init__("postgres", conf, sys_params)

    def connect(self):
        """connect to a database"""
        self.conn = psycopg2.connect("dbname='%s' user='%s'" % (self.config["db"], self.config["user"]))
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        self.index_creation_format = "CREATE INDEX %s ON %s (%s);"
        self.index_drop_format = "drop index %s;"
        self.is_cluster = False
        self.retrieve_table_name_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        self.cardinality_format = "select count(*) from %s;"
        self.cluster_indices_format = "CLUSTER %s ON %s;"
        self.enable_index_format = "update pg_index set indisvalid = true where indexrelid = '%s'::regclass;"
        self.disable_index_format = "update pg_index set indisvalid = false where indexrelid = '%s'::regclass;"

    def cardinalities(self):
        """get cardinality of the connected database"""
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
        """run queries with a timeout"""
        run_time = []
        for query_sql, current_timeout in zip(query_list, timeout):
            try:
                # logging.debug(f"query sql: {query_sql}")
                logging.debug(f"current timeout: {current_timeout}")
                self.cursor.execute("set statement_timeout = %d" % (current_timeout * 1000))
                start_time = time.time()
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
            except QueryCanceledError:
                duration = current_timeout
            except InternalError:
                # error to run the query, set duration to a large number
                logging.debug(f"Internal Error for query {query_sql}")
                duration = current_timeout * 1000
            logging.debug(f"duration: {duration}")
            run_time.append(duration)
        # reset the timeout to the default configuration
        self.cursor.execute("set statement_timeout=0;")
        self.cursor.execute("drop view if exists REVENUE0;")
        return run_time

    def run_queries_with_total_timeout(self, query_list, timeout):
        """run queries with a timeout"""
        run_time = []
        current_timeout = timeout
        total_runtime = 0
        for query_sql in query_list:
            try:
                logging.debug(f"current timeout: {current_timeout}")
                self.cursor.execute("set statement_timeout = %d" % (current_timeout * 1000))
                start_time = time.time()
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
            except QueryCanceledError:
                total_runtime = timeout
                break
            except InternalError:
                # error to run the query, set duration to a large number
                logging.debug(f"Internal Error for query {query_sql}")
                total_runtime = timeout * 1000
                break
            logging.debug(f"duration: {duration}")
            run_time.append(duration)
            current_timeout = current_timeout - duration
            total_runtime += duration
        # reset the timeout to the default configuration
        self.cursor.execute("set statement_timeout=0;")
        self.cursor.execute("drop view if exists REVENUE0;")
        logging.debug(f"runtime {run_time}")
        return total_runtime

    def run_queries_without_timeout(self, query_list):
        """run queries without timeout"""
        return self.run_queries_with_timeout(query_list, [0] * len(query_list))

    def build_index(self, index_to_create):
        """build index"""
        index_sql = self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2])
        logging.debug(f"create index {index_sql}")
        self.cursor.execute(index_sql)
        # if we consider the cluster indices
        if self.is_cluster:
            self.cursor.execute(self.cluster_indices_format % (index_to_create[0], index_to_create[1]))
        # self.conn.commit()

    def build_index_command(self, index_to_create):
        """build index command"""
        index_sql = self.index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2])
        if self.is_cluster:
            cluster_sql = self.cluster_indices_format % (index_to_create[0], index_to_create[1])
            return f"{index_sql} \n {cluster_sql}"
        else:
            return index_sql

    def drop_index(self, index_to_drop):
        """drop index"""
        index_sql = self.index_drop_format % (index_to_drop[0])
        logging.debug(f"drop index {index_sql}")
        self.cursor.execute(index_sql)
        # self.conn.commit()

    def set_system_parameter(self, parameter_sql):
        """switch system parameters"""
        logging.info(f"{parameter_sql}")
        self.cursor.execute(parameter_sql)
        # self.conn.commit()

    def analyze_queries_cost(self, query_sqls):
        """analyze cost of queries"""
        total_cost = []
        for analyze_sql in query_sqls:
            analyze_sql = f"explain (format json) {analyze_sql}"
            self.cursor.execute(analyze_sql)
            total_cost.append((self.cursor.fetchone())[0][0]['Plan']['Total Cost'])
        logging.info(f"estimate costs {total_cost}")
        return total_cost

    def enable_indices(self, index_to_enable):
        """enable indices"""
        index_sql = self.enable_index_format % (index_to_enable[0])
        logging.info(f"enable: {index_sql}")
        self.cursor.execute(index_sql)

    def disable_indices(self, index_to_disable):
        """disable indices"""
        index_sql = self.disable_index_format % (index_to_disable[0])
        logging.info(f"disable: {index_sql}")
        self.cursor.execute(index_sql)

    def close(self):
        """close the connection"""
        self.cursor.close()
        self.conn.close()

## CLASS
