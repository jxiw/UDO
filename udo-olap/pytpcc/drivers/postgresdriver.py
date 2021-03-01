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
        # run_time = []
        # for query in queries:
        #     try:
        #         query_sql = constants.QUERIES[query]
        #         self.cursor.execute("set statement_timeout=%d" % (4 * 1000))
        #         start_time = time.time()
        #         self.cursor.execute(query_sql)
        #         finish_time = time.time()
        #         duration = finish_time - start_time
        #         run_time.append(duration)
        #     except QueryCanceledError:
        #         print("timeout")
        #         run_time.append(4)
        # self.cursor.execute("set statement_timeout=0")
        # print(run_time)
        # return sum(run_time)

        # default_timeout for postgres
        default_timeout = [2.114644765853882, 0.3178749084472656, 0.8655669689178467, 0.27109265327453613,
                            1.0132851600646973, 0.3362388610839844, 0.6741001605987549, 0.4631633758544922,
                            1.3484652042388916, 0.7488498687744141, 0.12991714477539062, 0.9270060062408447,
                            1.2022361755371094, 0.3823051452636719, 0.7328939437866211, 0.6157047748565674,
                            1.9892585277557373, 3.471993923187256, 0.4750077724456787, 1.323035717010498,
                            0.8502225875854492, 0.41719698905944824]
        return self.runQueries(queries, [timeout * 1 for timeout in default_timeout])

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s);"
        logging.debug("create index %s", index_to_create)
        self.cursor.execute(index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2]))
        cluster_indices_format = "CLUSTER %s ON %s"
        self.cursor.execute(cluster_indices_format % (index_to_create[0], index_to_create[1]))
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
