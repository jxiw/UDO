import sqlparse

def get_table_name(tokens):
    for token in reversed(tokens):
        if token.ttype is None:
            return token.value
    return " "

schema= '''
CREATE TABLE WAREHOUSE (
  W_ID SMALLINT DEFAULT '0' NOT NULL,
  W_NAME VARCHAR(16) DEFAULT NULL,
  W_STREET_1 VARCHAR(32) DEFAULT NULL,
  W_STREET_2 VARCHAR(32) DEFAULT NULL,
  W_CITY VARCHAR(32) DEFAULT NULL,
  W_STATE VARCHAR(2) DEFAULT NULL,
  W_ZIP VARCHAR(9) DEFAULT NULL,
  W_TAX FLOAT DEFAULT NULL,
  W_YTD FLOAT DEFAULT NULL
);

CREATE TABLE DISTRICT (
  D_ID TINYINT DEFAULT '0' NOT NULL,
  D_W_ID SMALLINT DEFAULT '0' NOT NULL REFERENCES WAREHOUSE (W_ID),
  D_NAME VARCHAR(16) DEFAULT NULL,
  D_STREET_1 VARCHAR(32) DEFAULT NULL,
  D_STREET_2 VARCHAR(32) DEFAULT NULL,
  D_CITY VARCHAR(32) DEFAULT NULL,
  D_STATE VARCHAR(2) DEFAULT NULL,
  D_ZIP VARCHAR(9) DEFAULT NULL,
  D_TAX FLOAT DEFAULT NULL,
  D_YTD FLOAT DEFAULT NULL,
  D_NEXT_O_ID INT DEFAULT NULL
);

CREATE TABLE ITEM (
  I_ID INTEGER DEFAULT '0' NOT NULL,
  I_IM_ID INTEGER DEFAULT NULL,
  I_NAME VARCHAR(32) DEFAULT NULL,
  I_PRICE FLOAT DEFAULT NULL,
  I_DATA VARCHAR(64) DEFAULT NULL
);

CREATE TABLE CUSTOMER (
  C_ID INTEGER DEFAULT '0' NOT NULL,
  C_D_ID TINYINT DEFAULT '0' NOT NULL,
  C_W_ID SMALLINT DEFAULT '0' NOT NULL,
  C_FIRST VARCHAR(32) DEFAULT NULL,
  C_MIDDLE VARCHAR(2) DEFAULT NULL,
  C_LAST VARCHAR(32) DEFAULT NULL,
  C_STREET_1 VARCHAR(32) DEFAULT NULL,
  C_STREET_2 VARCHAR(32) DEFAULT NULL,
  C_CITY VARCHAR(32) DEFAULT NULL,
  C_STATE VARCHAR(2) DEFAULT NULL,
  C_ZIP VARCHAR(9) DEFAULT NULL,
  C_PHONE VARCHAR(32) DEFAULT NULL,
  C_SINCE TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  C_CREDIT VARCHAR(2) DEFAULT NULL,
  C_CREDIT_LIM FLOAT DEFAULT NULL,
  C_DISCOUNT FLOAT DEFAULT NULL,
  C_BALANCE FLOAT DEFAULT NULL,
  C_YTD_PAYMENT FLOAT DEFAULT NULL,
  C_PAYMENT_CNT INTEGER DEFAULT NULL,
  C_DELIVERY_CNT INTEGER DEFAULT NULL,
  C_DATA VARCHAR(500)
);

CREATE TABLE HISTORY (
  H_C_ID INTEGER DEFAULT NULL,
  H_C_D_ID TINYINT DEFAULT NULL,
  H_C_W_ID SMALLINT DEFAULT NULL,
  H_D_ID TINYINT DEFAULT NULL,
  H_W_ID SMALLINT DEFAULT '0' NOT NULL,
  H_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  H_AMOUNT FLOAT DEFAULT NULL,
  H_DATA VARCHAR(32) DEFAULT NULL
);

CREATE TABLE STOCK (
  S_I_ID INTEGER DEFAULT '0' NOT NULL REFERENCES ITEM (I_ID),
  S_W_ID SMALLINT DEFAULT '0 ' NOT NULL REFERENCES WAREHOUSE (W_ID),
  S_QUANTITY INTEGER DEFAULT '0' NOT NULL,
  S_DIST_01 VARCHAR(32) DEFAULT NULL,
  S_DIST_02 VARCHAR(32) DEFAULT NULL,
  S_DIST_03 VARCHAR(32) DEFAULT NULL,
  S_DIST_04 VARCHAR(32) DEFAULT NULL,
  S_DIST_05 VARCHAR(32) DEFAULT NULL,
  S_DIST_06 VARCHAR(32) DEFAULT NULL,
  S_DIST_07 VARCHAR(32) DEFAULT NULL,
  S_DIST_08 VARCHAR(32) DEFAULT NULL,
  S_DIST_09 VARCHAR(32) DEFAULT NULL,
  S_DIST_10 VARCHAR(32) DEFAULT NULL,
  S_YTD INTEGER DEFAULT NULL,
  S_ORDER_CNT INTEGER DEFAULT NULL,
  S_REMOTE_CNT INTEGER DEFAULT NULL,
  S_DATA VARCHAR(64) DEFAULT NULL
);

CREATE TABLE ORDERS (
  O_ID INTEGER DEFAULT '0' NOT NULL,
  O_C_ID INTEGER DEFAULT NULL,
  O_D_ID TINYINT DEFAULT '0' NOT NULL,
  O_W_ID SMALLINT DEFAULT '0' NOT NULL,
  O_ENTRY_D TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  O_CARRIER_ID INTEGER DEFAULT NULL,
  O_OL_CNT INTEGER DEFAULT NULL,
  O_ALL_LOCAL INTEGER DEFAULT NULL
);

CREATE TABLE NEW_ORDER (
  NO_O_ID INTEGER DEFAULT '0' NOT NULL,
  NO_D_ID TINYINT DEFAULT '0' NOT NULL,
  NO_W_ID SMALLINT DEFAULT '0' NOT NULL
);

CREATE TABLE ORDER_LINE (
  OL_O_ID INTEGER DEFAULT '0' NOT NULL,
  OL_D_ID TINYINT DEFAULT '0' NOT NULL,
  OL_W_ID SMALLINT DEFAULT '0' NOT NULL,
  OL_NUMBER INTEGER DEFAULT '0' NOT NULL,
  OL_I_ID INTEGER DEFAULT NULL,
  OL_SUPPLY_W_ID SMALLINT DEFAULT NULL,
  OL_DELIVERY_D TIMESTAMP DEFAULT NULL,
  OL_QUANTITY INTEGER DEFAULT NULL,
  OL_AMOUNT FLOAT DEFAULT NULL,
  OL_DIST_INFO VARCHAR(32) DEFAULT NULL
);
'''

parse = sqlparse.parse(schema)
for stmt in parse:
    # Get all the tokens except whitespaces
    tokens = [t for t in sqlparse.sql.TokenList(stmt.tokens) if t.ttype != sqlparse.tokens.Whitespace]
    is_create_stmt = False
    for i, token in enumerate(tokens):
        # Is it a create statements ?
        if token.match(sqlparse.tokens.DDL, 'CREATE'):
            is_create_stmt = True
            continue

        # If it was a create statement and the current token starts with "("
        if is_create_stmt and token.value.startswith("("):
            # Get the table name by looking at the tokens in reverse order till you find
            # a token with None type
            # print(f"table: {get_table_name(tokens[:i])}")
            print(f"'{get_table_name(tokens[:i])}':")
            print("[")
            # Now parse the columns
            txt = token.value
            columns = txt[1:txt.rfind(")")].replace("\n", "").split(",")
            for column in columns:
                c = ' '.join(column.split()).split()
                c_name = c[0].replace('\"', "")
                c_type = c[1]  # For condensed type information
                # OR
                # c_type = " ".join(c[1:]) # For detailed type information
                # print(f"column: {c_name}")
                # print(f"date type: {c_type}")
                print(f"'{c_name}',")
            # print("---" * 20)
            print("],")
            break