from __future__ import with_statement

import logging
import psycopg2
import time

from psycopg2._psycopg import QueryCanceledError

import constants


class PostgresDriver():

    ## ----------------------------------------------
    ## loadConfig
    ## ----------------------------------------------
    def connect(self):
        # config to connect dbms
        config = {
            "host": "127.0.0.1",
            "db": "tpch",
            # "db": "imdb",
            "user": "postgres",
            "passwd": "jw2544"
        }

        self.conn = psycopg2.connect("dbname='%s' user='%s'" % (config["db"], config["user"]))
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    ## ----------------------------------------------
    ## tpch queries
    ## ----------------------------------------------
    # def runQueries(self):
    #     queries = list(constants.QUERIES.keys())
    #     # self.cursor.execute("set statement_timeout=%d"%(constants.timeout * 1000))
    #     run_time = []
    #     for query in queries:
    #         try:
    #             start_time = time.time()
    #             query_sql = constants.QUERIES[query]
    #             self.cursor.execute(query_sql)
    #             finish_time = time.time()
    #             duration = finish_time - start_time
    #         except QueryCanceledError:
    #             print("timeout")
    #             duration = constants.timeout
    #         run_time.append(duration)
    #     # self.cursor.execute("set statement_timeout=0")
    #     print(run_time)
    #     return run_time

    def runQueries(self, query_list, timeout):
        run_time = []
        for query, current_timeout in zip(query_list, timeout):
            try:
                current_timeout = current_timeout
                self.cursor.execute("set statement_timeout=%d" % (current_timeout * 1000))
                start_time = time.time()
                query_sql = constants.QUERIES[query]
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
            except QueryCanceledError:
                print("timeout")
                duration = current_timeout
            run_time.append(duration)
        self.cursor.execute("set statement_timeout=0")
        print(run_time)
        return run_time

    def runQueriesWithoutTimeout(self):
        queries = list(constants.QUERIES.keys())
        run_time = []
        time_out = 4
        for query in queries:
            try:
                query_sql = constants.QUERIES[query]
                self.cursor.execute("set statement_timeout=%d" % (time_out * 1000))
                start_time = time.time()
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
                run_time.append(duration)
            except QueryCanceledError:
                print("timeout")
                run_time.append(time_out)
        self.cursor.execute("set statement_timeout=0")
        print(run_time)
        return sum(run_time)

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s);"
        logging.debug("create index %s", index_to_create)
        self.cursor.execute(index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2]))
        # cluster_indices_format = "CLUSTER %s ON %s"
        # self.cursor.execute(cluster_indices_format % (index_to_create[0], index_to_create[1]))
        # self.conn.commit()

    def dropIndex(self, index_to_drop):
        """drop index"""
        index_drop_format = "drop index %s;"
        logging.debug("drop index %s", index_to_drop)
        self.cursor.execute(index_drop_format % (index_to_drop[0]))
        # self.conn.commit()

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        # self.conn.commit()

## CLASS
