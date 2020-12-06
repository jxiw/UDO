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
            "db": "tpch_py",
            "user": "postgres",
            "passwd": "jw2544"
        }
        #
        # self.conn = psycopg2.connect("dbname='%s' user='%s'" % (config["db"], config["user"]))
        # self.conn.autocommit = True
        # self.cursor = self.conn.cursor()

    ## ----------------------------------------------
    ## tpch queries
    ## ----------------------------------------------
    def runQueries(self):
        queries = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12",
                   "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22"]
        self.cursor.execute("set statement_timeout=10000")
        run_time = []
        for query in queries:
            try:
                start_time = time.time()
                query_sql = constants.QUERIES[query]
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
            except QueryCanceledError:
                print("timeout")
                duration = constants.timeout
            run_time.append(duration)
        self.cursor.execute("set statement_timeout=0")
        print(run_time)
        return run_time

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s);"
        logging.debug("create index %s", index_to_create)
        # self.cursor.execute(index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2]))
        # self.conn.commit()

    def dropIndex(self, index_to_drop):
        """drop index"""
        index_drop_format = "drop index %s;"
        logging.debug("drop index %s", index_to_drop)
        # self.cursor.execute(index_drop_format % (index_to_drop[0]))
        # self.conn.commit()

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        # self.cursor.execute(parameter_sql)
        # self.conn.commit()

## CLASS
