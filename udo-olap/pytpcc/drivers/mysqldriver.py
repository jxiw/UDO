from __future__ import with_statement

import logging
import MySQLdb
import time
import constants

class MysqlDriver():

    ## ----------------------------------------------
    ## loadConfig
    ## ----------------------------------------------
    def connect(self):
        # config to connect dbms
        config = {
            "host": "127.0.0.1",
            "port": 3306,
            "db": "tpch",
            "user": "jw2544",
            "passwd": "jw2544"
        }

        self.conn = MySQLdb.connect(config['host'], config['user'], config['passwd'], config['db'])
        self.cursor = self.conn.cursor()

    ## ----------------------------------------------
    ## tpch queries
    ## ----------------------------------------------
    # def runQueries(self):
    #     queries = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12",
    #                "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22"]
    #     invoke_time = time.time()
    #     for query in queries:
    #         query_sql = constants.QUERIES[query]
    #         self.cursor.execute(query_sql)
    #     finish_time = time.time()
    #     return (finish_time - invoke_time)

    def runQueries(self, query_list, timeout):
        run_time = []
        for query, current_timeout in zip(query_list, timeout):
            try:
                current_timeout = current_timeout
                self.cursor.execute("SET SESSION MAX_EXECUTION_TIME=%d" % (current_timeout * 1000))
                start_time = time.time()
                query_sql = constants.QUERIES[query]
                self.cursor.execute(query_sql)
                finish_time = time.time()
                duration = finish_time - start_time
                print("query run:%s"%duration)
            except MySQLdb.OperationalError as oe:
                print(oe)
                print("timeout")
                duration = current_timeout
            run_time.append(duration)
        print(run_time)
        # reset back to normal configuraiton
        try:
            self.cursor.execute("SET SESSION MAX_EXECUTION_TIME=0")
            self.cursor.execute("drop view if exists REVENUE0;")
        except MySQLdb.OperationalError as oe:
            print(oe)
        return run_time

    def runQueriesWithoutTimeout(self):
        queries = list(constants.QUERIES.keys())
        # run_time = []
        # for query in queries:
        #     query_sql = constants.QUERIES[query]
        #     start_time = time.time()
        #     self.cursor.execute(query_sql)
        #     finish_time = time.time()
        #     duration = finish_time - start_time
        #     run_time.append(duration)
        # print(run_time)

        timeout = [10.693569898605347, 0.11094331741333008, 3.72650408744812, 1.0694530010223389, 1.0730197429656982, 2.2397916316986084, 2.0279834270477295, 3.822448968887329, 7.970007419586182, 1.4352169036865234, 0.515200138092041, 2.6003406047821045, 12.872627019882202, 2.3702046871185303, 0.0011920928955078125, 0.46315932273864746, 0.7527892589569092, 2.645094633102417, 0.23529434204101562, 0.8605573177337646, 10.454352855682373, 0.16903018951416016]
        return self.runQueries(queries,  timeout)

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s) USING BTREE;"
        # logging.debug("create index %s" % index_to_create)
        self.cursor.execute(index_creation_format%(index_to_create[0], index_to_create[1], index_to_create[2]))
        self.conn.commit()

    def dropIndex(self, index_to_drop):
        """drop index"""
        index_drop_format = "ALTER TABLE %s drop index %s;"
        # logging.debug("drop index %s" % index_to_drop)
        self.cursor.execute(index_drop_format%(index_to_drop[1], index_to_drop[0]))
        self.conn.commit()

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        self.conn.commit()

## CLASS
