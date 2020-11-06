from __future__ import with_statement

import logging
import MySQLdb
from pprint import pprint, pformat

import constants
from .abstractdriver import *

class MysqlDriver(AbstractDriver):
    DEFAULT_CONFIG = {
        "host": ("The hostname to mysql", "127.0.0.1"),
        "port": ("The port number to mysql", 3306),
        "db": ("datbase name", "tpcc_py"),
        "user": ("user name", "jw2544"),
        "passwd": ("password", "jw2544")
    }

    def __init__(self, ddl):
        super(MysqlDriver, self).__init__("mysql", ddl)
        logging.debug(ddl)

    ## ----------------------------------------------
    ## makeDefaultConfig
    ## ----------------------------------------------
    def makeDefaultConfig(self):
        return MysqlDriver.DEFAULT_CONFIG

    ## ----------------------------------------------
    ## loadConfig
    ## ----------------------------------------------
    def loadConfig(self, config):
        for key in MysqlDriver.DEFAULT_CONFIG.keys():
            assert key in config, "Missing parameter '%s' in %s configuration" % (key, self.name)

        self.conn = MySQLdb.connect(config['host'], config['user'], config['passwd'], config['db'])
        self.cursor = self.conn.cursor()
        if config["reset"]:
            logging.debug("Deleting database '%s'" % config['db'])
            self.cursor.execute("Drop database %s" % config['db'])

    ## ----------------------------------------------
    ## loadTuples
    ## ----------------------------------------------
    def loadTuples(self, tableName, tuples):
        if len(tuples) == 0: return

        p = ["%s"] * len(tuples[0])
        sql = "INSERT INTO %s VALUES (%s)" % (tableName, ",".join(p))
        logging.debug("sql:" + sql)
        self.cursor.executemany(sql, tuples)
        logging.debug("Loaded %d tuples for tableName %s" % (len(tuples), tableName))
        self.conn.commit()
        return

    # ## ==============================================
    # ## loadStart
    # ## ==============================================
    # def loadStart(self):

    def loadFinish(self):
        sql = "ALTER TABLE ORDER_LINE ADD CONSTRAINT OL_FKEY_S FOREIGN KEY (OL_SUPPLY_W_ID, OL_I_ID) REFERENCES STOCK (S_W_ID, S_I_ID)"
        self.cursor.execute(sql)
        self.conn.commit()
        return

    ## ----------------------------------------------
    ## doDelivery
    ## ----------------------------------------------
    def doDelivery(self, params):
        w_id = params["w_id"]
        o_carrier_id = params["o_carrier_id"]
        proc_num = params["procInfo"]["delivery"]
        proc_args = [w_id, o_carrier_id, constants.DISTRICTS_PER_WAREHOUSE]
        self.cursor.callproc('delivery_%d'%proc_num, proc_args)
        self.conn.commit()

    ## ----------------------------------------------
    ## doNewOrder
    ## ----------------------------------------------
    def doNewOrder(self, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        c_id = params["c_id"]
        i_ids = params["i_ids"]
        i_w_ids = params["i_w_ids"]
        i_qtys = params["i_qtys"]
        all_local = True
        for i in range(len(i_ids)):
            ## Determine if this is an all local order or not
            all_local = all_local and i_w_ids[i] == w_id
        item_cnt = len(i_ids)
        proc_args = [w_id, d_id, c_id, int(all_local), item_cnt]
        # print proc_args
        for i in range(item_cnt):
            proc_args.append(i_ids[i])
            proc_args.append(i_w_ids[i])
            proc_args.append(i_qtys[i])
        for i in range(item_cnt, constants.MAX_OL_CNT):
            proc_args.append(0)
            proc_args.append(0)
            proc_args.append(0)
        #the one is the return value
        proc_args.append(0)
        proc_num =  params["procInfo"]["new_order"]
        self.cursor.callproc('new_order_%d' % proc_num, proc_args)
        self.conn.commit()

    ## ----------------------------------------------
    ## doOrderStatus
    ## ----------------------------------------------
    def doOrderStatus(self, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        c_id = params["c_id"]
        c_last = params["c_last"]
        proc_args = [c_id, w_id, d_id, c_last]
        self.cursor.callproc('order_status', proc_args)
        self.conn.commit()

    ## ----------------------------------------------
    ## doPayment
    ## ----------------------------------------------
    def doPayment(self, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        h_amount = params["h_amount"]
        c_w_id = params["c_w_id"]
        c_d_id = params["c_d_id"]
        c_id = params["c_id"]
        c_last = params["c_last"]
        proc_num = params["procInfo"]["payment"]
        proc_args = [w_id, d_id, c_id, c_w_id, c_d_id, c_last, h_amount]
        self.cursor.callproc('payment_%d'%proc_num, proc_args)
        self.conn.commit()

    ## ----------------------------------------------
    ## doStockLevel
    ## ----------------------------------------------
    def doStockLevel(self, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        threshold = params["threshold"]
        low_stock = 0
        proc_args = [w_id, d_id, threshold, low_stock]
        self.cursor.callproc('order_status', proc_args)
        self.conn.commit()

    def buildIndex(self, index_creation_sql):
        """build index"""
        logging.debug("create index %s" % index_creation_sql)
        self.cursor.execute(index_creation_sql)

    def dropIndex(self, index_drop_sql):
        """drop index"""
        logging.debug("drop index %s" % index_drop_sql)
        self.cursor.execute(index_drop_sql)

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)

## CLASS
