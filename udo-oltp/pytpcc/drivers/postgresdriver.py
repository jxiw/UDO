from __future__ import with_statement

import logging
import psycopg2
import time

from psycopg2._psycopg import QueryCanceledError

import constants
from .abstractdriver import *


class PostgresDriver(AbstractDriver):
    DEFAULT_CONFIG = {
        "host": ("The hostname to postgres", "127.0.0.1"),
        "db": ("database name", "tpcc"),
        "user": ("user name", "postgres")
    }

    def __init__(self, ddl):
        super(PostgresDriver, self).__init__("postgres", ddl)
        logging.debug(ddl)

    ## ----------------------------------------------
    ## makeDefaultConfig
    ## ----------------------------------------------
    def makeDefaultConfig(self):
        return PostgresDriver.DEFAULT_CONFIG

    ## ----------------------------------------------
    ## loadConfig
    ## ----------------------------------------------
    def connect(self):
        # config to connect dbms
        config = {
            "host": "127.0.0.1",
            "db": "tpcc",
            "user": "postgres",
            "passwd": "jw2544"
        }

        self.conn = psycopg2.connect("dbname='%s' user='%s'" % (config["db"], config["user"]))
        self.cursor = self.conn.cursor()

    ## ----------------------------------------------
    ## loadConfig
    ## ----------------------------------------------
    def loadConfig(self, config):
        for key in PostgresDriver.DEFAULT_CONFIG.keys():
            assert key in config, "Missing parameter '%s' in %s configuration" % (key, self.name)

        self.conn = psycopg2.connect("dbname='%s' user='%s'" % (config["db"], config["user"]))
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

    ## ----------------------------------------------
    ## doDelivery
    ## ----------------------------------------------
    def doDelivery(self, params):
        w_id = params["w_id"]
        o_carrier_id = params["o_carrier_id"]
        proc_num = params["procInfo"]["delivery"]
        proc_args = [w_id, o_carrier_id, constants.DISTRICTS_PER_WAREHOUSE]
        self.cursor.callproc('delivery_%d' % proc_num, proc_args)
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
        # the one is the return value => for postgres no need for return value
        # proc_args.append(0)
        proc_num = params["procInfo"]["new_order"]
        self.cursor.callproc('new_order_%d' % proc_num, proc_args)
        self.conn.commit()

    ## ----------------------------------------------
    ## dORDERSStatus
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
        self.cursor.callproc('payment_%d' % proc_num, proc_args)
        self.conn.commit()

    ## ----------------------------------------------
    ## doStockLevel
    ## ----------------------------------------------
    def doStockLevel(self, params):
        w_id = params["w_id"]
        d_id = params["d_id"]
        threshold = params["threshold"]
        proc_args = [w_id, d_id, threshold]
        self.cursor.callproc('stock_level', proc_args)
        self.conn.commit()

    def buildIndex(self, index_to_create):
        """build index"""
        index_creation_format = "CREATE INDEX %s ON %s (%s);"
        logging.debug("create index %s", index_to_create)
        self.cursor.execute(index_creation_format % (index_to_create[0], index_to_create[1], index_to_create[2]))
        cluster_indices_format = "CLUSTER %s ON %s"
        self.cursor.execute(cluster_indices_format % (index_to_create[0], index_to_create[1]))
        self.conn.commit()

    def dropIndex(self, index_to_drop):
        """drop index"""
        index_drop_format = "drop index %s;"
        logging.debug("drop index %s", index_to_drop)
        self.cursor.execute(index_drop_format % (index_to_drop[0]))
        self.conn.commit()

    def setSystemParameter(self, parameter_sql):
        """parameter change"""
        logging.debug("change system parameter %s" % parameter_sql)
        self.cursor.execute(parameter_sql)
        self.conn.commit()

    def resetDatabase(self):
        """reload the database table from table copies"""
        self.cursor.execute("DROP TABLE IF EXISTS HISTORY;")
        self.cursor.execute("DROP TABLE IF EXISTS NEW_ORDER;")
        self.cursor.execute("DROP TABLE IF EXISTS ORDER_LINE;")
        self.cursor.execute("DROP TABLE IF EXISTS ORDERS;")
        self.cursor.execute("DROP TABLE IF EXISTS CUSTOMER;")
        self.cursor.execute("DROP TABLE IF EXISTS DISTRICT;")
        self.cursor.execute("DROP TABLE IF EXISTS STOCK;")
        self.cursor.execute("DROP TABLE IF EXISTS ITEM;")
        self.cursor.execute("DROP TABLE IF EXISTS WAREHOUSE;")
        self.cursor.execute("CREATE TABLE HISTORY AS TABLE HISTORY_COPY;")
        self.cursor.execute("CREATE TABLE NEW_ORDER AS TABLE NEW_ORDER_COPY;")
        self.cursor.execute("CREATE TABLE ORDER_LINE AS TABLE ORDER_LINE_COPY;")
        self.cursor.execute("CREATE TABLE ORDERS AS TABLE ORDERS_COPY;")
        self.cursor.execute("CREATE TABLE CUSTOMER AS TABLE CUSTOMER_COPY;")
        self.cursor.execute("CREATE TABLE DISTRICT AS TABLE DISTRICT_COPY;")
        self.cursor.execute("CREATE TABLE STOCK AS TABLE STOCK_COPY;")
        self.cursor.execute("CREATE TABLE ITEM AS TABLE ITEM_COPY;")
        self.cursor.execute("CREATE TABLE WAREHOUSE AS TABLE WAREHOUSE_COPY;")
        ########
        self.cursor.execute("ALTER TABLE WAREHOUSE ADD PRIMARY KEY (W_ID);")
        self.cursor.execute("ALTER TABLE DISTRICT ADD PRIMARY KEY (D_W_ID,D_ID);")
        self.cursor.execute("ALTER TABLE ITEM ADD PRIMARY KEY (I_ID);")
        self.cursor.execute("ALTER TABLE CUSTOMER ADD PRIMARY KEY (C_W_ID,C_D_ID,C_ID);")
        self.cursor.execute("ALTER TABLE STOCK ADD PRIMARY KEY (S_W_ID,S_I_ID);")
        self.cursor.execute("ALTER TABLE ORDERS ADD PRIMARY KEY (O_W_ID,O_D_ID,O_ID);")
        self.cursor.execute("ALTER TABLE NEW_ORDER ADD PRIMARY KEY (NO_W_ID, NO_D_ID, NO_O_ID);")
        self.cursor.execute("ALTER TABLE ORDER_LINE ADD PRIMARY KEY (OL_W_ID,OL_D_ID,OL_O_ID,OL_NUMBER);")
        self.cursor.execute(
            "ALTER TABLE CUSTOMER ADD CONSTRAINT C_FKEY_D FOREIGN KEY (C_W_ID, C_D_ID) REFERENCES DISTRICT (D_W_ID, D_ID);")
        self.cursor.execute(
            "ALTER TABLE HISTORY ADD CONSTRAINT H_FKEY_C FOREIGN KEY (H_C_W_ID, H_C_D_ID, H_C_ID) REFERENCES CUSTOMER (C_W_ID, C_D_ID, C_ID);")
        self.cursor.execute(
            "ALTER TABLE HISTORY ADD CONSTRAINT H_FKEY_D FOREIGN KEY (H_W_ID, H_D_ID) REFERENCES DISTRICT (D_W_ID, D_ID);")
        self.cursor.execute(
            "ALTER TABLE ORDERS ADD CONSTRAINT O_FKEY_C FOREIGN KEY (O_W_ID, O_D_ID, O_C_ID) REFERENCES CUSTOMER (C_W_ID, C_D_ID, C_ID);")
        self.cursor.execute(
            "ALTER TABLE NEW_ORDER ADD CONSTRAINT NO_FKEY_O FOREIGN KEY (NO_W_ID, NO_D_ID, NO_O_ID) REFERENCES ORDERS (O_W_ID, O_D_ID, O_ID);")
        self.cursor.execute(
            "ALTER TABLE ORDER_LINE ADD CONSTRAINT OL_FKEY_O FOREIGN KEY (OL_W_ID, OL_D_ID, OL_O_ID) REFERENCES ORDERS (O_W_ID, O_D_ID, O_ID);")
        self.cursor.execute(
            "ALTER TABLE ORDER_LINE ADD CONSTRAINT OL_FKEY_S FOREIGN KEY (OL_SUPPLY_W_ID, OL_I_ID) REFERENCES STOCK (S_W_ID, S_I_ID);")
        self.conn.commit()

        ## CLASS
