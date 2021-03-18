from __future__ import with_statement

import logging
import MySQLdb
import time
from .mysqlsysparams import mysql_candidate_dbms_parameter

from .abstractdriver import *


# the DBMS connector for MySQL
class MysqlDriver(AbstractDriver):

    def __init__(self):
        super(MysqlDriver, self).__init__("mysql")

    ## connect to database system
    def connect(self):
        # config to connect dbms
        config = {
            "host": "127.0.0.1",
            "port": 3306,
            "db": "tpch",
            # "db": "imdb",
            "user": "jw2544",
            "passwd": "jw2544"
        }

        self.conn = MySQLdb.connect(config['host'], config['user'], config['passwd'], config['db'])
        self.cursor = self.conn.cursor()
        self.index_creation_format = "CREATE INDEX %s ON %s (%s);"
        self.index_drop_format = "drop index %s;"
        self.is_cluster = True
        self.sys_params = mysql_candidate_dbms_parameter
        self.sys_params_space = [len(specific_parameter) for specific_parameter in self.sys_params]

    def runQueriesWithTimeout(self, query_list, timeout):
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

    def runQueriesWithoutTimeout(self, query_list):
        # run queries without timeout
        return self.runQueriesWithTimeout(query_list, [0 for query in query_list])

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s) USING BTREE;"
        # logging.debug("create index %s" % index_to_create)
        self.cursor.execute(index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2]))
        self.conn.commit()

    def dropIndex(self, index_to_drop):
        """drop index"""
        index_drop_format = "ALTER TABLE %s drop index %s;"
        # logging.debug("drop index %s" % index_to_drop)
        self.cursor.execute(index_drop_format % (index_to_drop[1], index_to_drop[0]))
        self.conn.commit()

    def changeSystemParameter(self, parameter_choices):
        for i in range(self.sys_params_type):
            parameter_choice = int(parameter_choices[i])
            parameter_change_sql = self.sys_params[i][parameter_choice]
            print(parameter_change_sql)
            self.setSystemParameter(parameter_change_sql)

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        self.conn.commit()

## CLASS
