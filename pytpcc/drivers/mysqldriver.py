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
    def runQueries(self):
        queries = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12",
                   "q13", "q14", "q15", "q16", "q17", "q18", "q19", "q20", "q21", "q22"]
        invoke_time = time.time()
        for query in queries:
            query_sql = constants.QUERIES[query]
            self.cursor.execute(query_sql)
        finish_time = time.time()
        return (finish_time - invoke_time)

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s) USING BTREE;"
        logging.debug("create index %s" % index_to_create)
        self.cursor.execute(index_creation_format%(index_to_create[0], index_to_create[1], index_to_create[2]))
        self.conn.commit()

    def dropIndex(self, index_to_drop):
        """drop index"""
        index_drop_format = "ALTER TABLE %s drop index %s;"
        logging.debug("drop index %s" % index_to_drop)
        self.cursor.execute(index_drop_format%(index_to_drop[0], index_to_drop[1]))
        self.conn.commit()

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        self.conn.commit()

## CLASS
