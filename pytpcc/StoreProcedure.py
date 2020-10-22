import MySQLdb
import itertools

config = {
    "host": "localhost",
    "port": 3306,
    "db": "tpcc_py",
    "user": "jw2544",
    "passwd": "jw2544"
}

conn = MySQLdb.connect(config['host'], config['user'], config['passwd'], config['db'])
cursor = conn.cursor()

TXN_UNIT = {
    "DELIVERY": [
        """
            /* 0 */
		    SELECT no_o_id
		    INTO tmp_o_id
		    FROM new_order
		    WHERE no_w_id = in_w_id AND no_d_id = tmp_d_id ORDER BY NO_O_ID ASC limit 1;
        """,
        """
            /* 1 */
		   DELETE FROM new_order 
		   WHERE no_o_id = tmp_o_id 
			 AND no_w_id = in_w_id 
			 AND no_d_id = tmp_d_id;
        """,
        """
            /* 2 */
		   SELECT o_c_id
		   INTO out_c_id
		   FROM orders
		   WHERE o_id = tmp_o_id
			 AND o_w_id = in_w_id
			 AND o_d_id = tmp_d_id;
        """,
        """
           /* 3 */
		   UPDATE orders
		   SET o_carrier_id = in_o_carrier_id
		   WHERE o_id = tmp_o_id
			 AND o_w_id = in_w_id
			 AND o_d_id = tmp_d_id;
        """,
        """
            /* 4 */
		   UPDATE order_line
		   SET ol_delivery_d = current_timestamp
		   WHERE ol_o_id = tmp_o_id
			 AND ol_w_id = in_w_id
			 AND ol_d_id = tmp_d_id;
        """,
        """
            /* 5 */
		   SELECT SUM(ol_amount * ol_quantity)
		   INTO out_ol_amount
		   FROM order_line
		   WHERE ol_o_id = tmp_o_id
			 AND ol_w_id = in_w_id
			 AND ol_d_id = tmp_d_id;
        """,
        """
            /* 6 */
		   UPDATE customer
		   SET c_delivery_cnt = c_delivery_cnt + 1,
			   c_balance = c_balance + out_ol_amount
		   WHERE c_id = out_c_id
			 AND c_w_id = in_w_id
			 AND c_d_id = tmp_d_id;
        """
    ],
    "PAYMENT": [
        """
          	/* 0 */
            SELECT w_name, w_street_1, w_street_2, w_city, w_state, w_zip
            INTO out_w_name, out_w_street_1, out_w_street_2, out_w_city,
                 out_w_state, out_w_zip
            FROM warehouse
            WHERE w_id = in_w_id;  
        """,
        """
            /* 1 */
            UPDATE warehouse
            SET w_ytd = w_ytd + in_h_amount
            WHERE w_id = in_w_id;
        """,
        """
        	/* 2 */
            SELECT d_name, d_street_1, d_street_2, d_city, d_state, d_zip
            INTO out_d_name, out_d_street_1, out_d_street_2, out_d_city,
                 out_d_state, out_d_zip
            FROM district
            WHERE d_id = in_d_id
              AND d_w_id = in_w_id;
        """,
        """
            /* 3 */
            UPDATE district
            SET d_ytd = d_ytd + in_h_amount
            WHERE d_id = in_d_id
              AND d_w_id = in_w_id;
        """,
        """
            /* 4 */
            IF in_c_id = 0 THEN
                    SELECT c_id, c_first, c_middle, c_last, c_street_1, c_street_2, c_city,
                       c_state, c_zip, c_phone, c_since, c_credit,
                       c_credit_lim, c_discount, c_balance, c_data,
                       c_ytd_payment
                    INTO out_c_id, out_c_first, out_c_middle, out_c_last, out_c_street_1,
                        out_c_street_2, out_c_city, out_c_state, out_c_zip, out_c_phone,
                        out_c_since, out_c_credit, out_c_credit_lim, out_c_discount,
                        out_c_balance, out_c_data, out_c_ytd_payment
                    FROM customer
                    WHERE c_w_id = in_c_w_id
                      AND c_d_id = in_c_d_id
                      AND c_last = in_c_last
                    ORDER BY c_first ASC limit 1;
            ELSE
                    SET out_c_id = in_c_id;
                    SELECT c_first, c_middle, c_last, c_street_1, c_street_2, c_city,
                       c_state, c_zip, c_phone, c_since, c_credit,
                       c_credit_lim, c_discount, c_balance, c_data,
                       c_ytd_payment
                    INTO out_c_first, out_c_middle, out_c_last, out_c_street_1,
                        out_c_street_2, out_c_city, out_c_state, out_c_zip, out_c_phone,
                        out_c_since, out_c_credit, out_c_credit_lim, out_c_discount,
                        out_c_balance, out_c_data, out_c_ytd_payment
                    FROM customer
                    WHERE c_w_id = in_c_w_id
                        AND c_d_id = in_c_d_id
                        AND c_id = out_c_id;
            END IF;
        """,
        """
            /* 5 */
            IF out_c_credit = 'BC' THEN
                    SELECT out_c_id
                    INTO tmp_c_id;
                    SELECT in_c_d_id 
                    INTO tmp_c_d_id;
                    SELECT in_c_w_id
                    INTO tmp_c_w_id;
                    SELECT in_d_id
                    INTO tmp_d_id;
                    SELECT in_w_id
                    INTO tmp_w_id;
    
                    SET out_c_data = concat(tmp_c_id,' ',tmp_c_d_id,' ',tmp_c_w_id,' ',tmp_d_id,' ',tmp_w_id);
    
                    UPDATE customer
                    SET c_balance = out_c_balance - in_h_amount,
                        c_ytd_payment = out_c_ytd_payment + 1,
                        c_data = out_c_data
                    WHERE c_id = out_c_id
                      AND c_w_id = in_c_w_id
                      AND c_d_id = in_c_d_id;
            ELSE
                    UPDATE customer
                    SET c_balance = out_c_balance - in_h_amount,
                        c_ytd_payment = out_c_ytd_payment + 1
                    WHERE c_id = out_c_id
                      AND c_w_id = in_c_w_id
                      AND c_d_id = in_c_d_id;
            END IF;
        """,
        """
            /* 6 */
            SET tmp_h_data = concat(out_w_name,' ', out_d_name);
            INSERT INTO history (h_c_id, h_c_d_id, h_c_w_id, h_d_id, h_w_id,
                                 h_date, h_amount, h_data)
            VALUES (out_c_id, in_c_d_id, in_c_w_id, in_d_id, in_w_id,
                    current_timestamp, in_h_amount, tmp_h_data);
        """

    ],
    "NEWORDER": ["""
          /* 0 */
          SELECT c_discount , c_last, c_credit
          INTO out_c_discount, out_c_last, out_c_credit
          FROM customer
          WHERE c_w_id = tmp_w_id
            AND c_d_id = tmp_d_id
            AND c_id = tmp_c_id;
        """,
        """
        /* 1 */
        SELECT w_tax
        INTO out_w_tax
        FROM warehouse
        WHERE w_id = tmp_w_id;
        """,
        """
        /* 2 */
        SELECT d_tax, d_next_o_id
        INTO out_d_tax, out_d_next_o_id
        FROM district
        WHERE d_w_id = tmp_w_id
         AND d_id = tmp_d_id FOR UPDATE;
        
        SET o_id=out_d_next_o_id;
        
        UPDATE district
        SET d_next_o_id = d_next_o_id + 1
        WHERE d_w_id = tmp_w_id
         AND d_id = tmp_d_id;
        """,
        """
        /* 3 */
        INSERT INTO orders (o_id, o_d_id, o_w_id, o_c_id, o_entry_d,
                             o_carrier_id, o_ol_cnt, o_all_local)
        VALUES (out_d_next_o_id, tmp_d_id, tmp_w_id, tmp_c_id,
                 current_timestamp, NULL, tmp_o_ol_cnt, tmp_o_all_local);
        """,
        """
        /* 4 */
        INSERT INTO new_order (no_o_id, no_d_id, no_w_id)
        VALUES (out_d_next_o_id, tmp_d_id, tmp_w_id);
        """
    ]
}

delivery_format = '''
    CREATE PROCEDURE `delivery_%d`(in_w_id INT, in_o_carrier_id INT, d_total INT)
    BEGIN

       DECLARE      out_c_id INT;
       DECLARE      out_ol_amount INT;
       DECLARE 	tmp_d_id INT;
       DECLARE 	tmp_o_id INT default 0;
    
        SET tmp_d_id = 1;
        while tmp_d_id <= d_total DO
        BEGIN
        
            SET tmp_o_id= 0;
            
            %s
            
       IF tmp_o_id > 0 
         THEN
           
           %s
     
           %s
     
           %s
     
           %s
     
           %s
           
           %s
    
         END IF;
    
         SET tmp_d_id = tmp_d_id + 1;
    
       END;
       END WHILE;
    END        
'''

payment_format = '''
CREATE PROCEDURE `payment_%d`(in_w_id INT, in_d_id INT, in_c_id INT, in_c_w_id INT, in_c_d_id INT,
                         in_c_last VARCHAR(16), in_h_amount INT)
BEGIN

DECLARE  out_w_name VARCHAR(10);
DECLARE  out_w_street_1 VARCHAR(20);
DECLARE  out_w_street_2 VARCHAR(20);
DECLARE  out_w_city VARCHAR(20);
DECLARE  out_w_state VARCHAR(2);
DECLARE  out_w_zip VARCHAR(9);

DECLARE  out_d_name VARCHAR(10);
DECLARE  out_d_street_1 VARCHAR(20);
DECLARE  out_d_street_2 VARCHAR(20);
DECLARE  out_d_city VARCHAR(20);
DECLARE  out_d_state VARCHAR(2);
DECLARE  out_d_zip VARCHAR(9);

DECLARE  out_c_id INTEGER;
DECLARE  out_c_first VARCHAR(16);
DECLARE  out_c_middle VARCHAR(2);
DECLARE  out_c_last VARCHAR(20);
DECLARE  out_c_street_1 VARCHAR(20);
DECLARE  out_c_street_2 VARCHAR(20);
DECLARE  out_c_city VARCHAR(20);
DECLARE  out_c_state VARCHAR(2);
DECLARE  out_c_zip VARCHAR(9);
DECLARE  out_c_phone VARCHAR(16);
DECLARE  out_c_since VARCHAR(28);
DECLARE  out_c_credit VARCHAR(2);
DECLARE  out_c_credit_lim FIXED(24, 12);
DECLARE  out_c_discount REAL;
DECLARE  out_c_balance NUMERIC;
DECLARE  out_c_data VARCHAR(500);
DECLARE  out_c_ytd_payment INTEGER;


#        /* Goofy temporaty variables. */
DECLARE  tmp_c_id VARCHAR(30);
DECLARE  tmp_c_d_id VARCHAR(30);
DECLARE  tmp_c_w_id VARCHAR(30);
DECLARE  tmp_d_id VARCHAR(30);
DECLARE  tmp_w_id VARCHAR(30);
DECLARE  tmp_h_amount VARCHAR(30);

#        /* This one is not goofy. */
DECLARE  tmp_h_data VARCHAR(30);

        %s

        %s

        %s

        %s

        %s
        
        %s
        
        %s
                
END
'''

new_order_format = '''
CREATE DEFINER=`jw2544`@`localhost` PROCEDURE `new_order_%d`(tmp_w_id INT,           
                           tmp_d_id INT,           
                           tmp_c_id INT,           
                           tmp_o_all_local INT,
                           tmp_o_ol_cnt INT,           
                           ol_i_id1 INT,           
                           ol_supply_w_id1 INT,           
                           ol_quantity1 INT,           
                           ol_i_id2 INT,           
                           ol_supply_w_id2 INT,           
                           ol_quantity2 INT,           
                           ol_i_id3 INT,           
                           ol_supply_w_id3 INT,           
                           ol_quantity3 INT,           
                           ol_i_id4 INT,           
                           ol_supply_w_id4 INT,           
                           ol_quantity4 INT,           
                           ol_i_id5 INT,           
                           ol_supply_w_id5 INT,           
                           ol_quantity5 INT,           
                           ol_i_id6 INT,           
                           ol_supply_w_id6 INT,           
                           ol_quantity6 INT,           
                           ol_i_id7 INT,           
                           ol_supply_w_id7 INT,           
                           ol_quantity7 INT,           
                           ol_i_id8 INT,           
                           ol_supply_w_id8 INT,           
                           ol_quantity8 INT,           
                           ol_i_id9 INT,           
                           ol_supply_w_id9 INT,           
                           ol_quantity9 INT,           
                           ol_i_id10 INT,           
                           ol_supply_w_id10 INT,           
                           ol_quantity10 INT,           
                           ol_i_id11 INT,           
                           ol_supply_w_id11 INT,           
                           ol_quantity11 INT,           
                           ol_i_id12 INT,           
                           ol_supply_w_id12 INT,           
                           ol_quantity12 INT,           
                           ol_i_id13 INT,           
                           ol_supply_w_id13 INT,           
                           ol_quantity13 INT,           
                           ol_i_id14 INT,           
                           ol_supply_w_id14 INT,           
                           ol_quantity14 INT,           
                           ol_i_id15 INT,           
                           ol_supply_w_id15 INT,           
                           ol_quantity15 INT,
                           out rc int)
BEGIN

  DECLARE out_c_credit VARCHAR(255);
  DECLARE tmp_i_name VARCHAR(255);
  DECLARE tmp_i_data VARCHAR(255);
  DECLARE out_c_last VARCHAR(255);

  DECLARE tmp_ol_supply_w_id INT;
  DECLARE tmp_ol_quantity INT;
  DECLARE out_d_next_o_id INT;
  DECLARE tmp_i_id INT;

  DECLARE tmp_s_quantity INT;

  DECLARE out_w_tax REAL;
  DECLARE out_d_tax REAL;
  DECLARE out_c_discount REAL;
  DECLARE tmp_i_price REAL;
  DECLARE tmp_ol_amount REAL;
  DECLARE tmp_total_amount REAL;

  DECLARE o_id INT;

  declare exit handler for sqlstate '02000' set rc = 1;

  SET rc=0;

  SET o_id = 0;

  /* getWarehouseTaxRate */
  
  %s
  
  %s
  
  %s
  
  %s
  
  %s
  
  SET tmp_total_amount = 0;

    IF tmp_o_ol_cnt > 0 
    THEN

      SET tmp_i_id = ol_i_id1;
      SET tmp_ol_supply_w_id = ol_supply_w_id1;
      SET tmp_ol_quantity = ol_quantity1;

	  /* 5 */
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 
      THEN
		SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

		call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
							 tmp_ol_quantity, tmp_i_price,
				 tmp_i_name, tmp_i_data,
				 out_d_next_o_id, tmp_ol_amount,
							 tmp_ol_supply_w_id, 1, tmp_s_quantity);

		SET tmp_total_amount = tmp_ol_amount;
		  END IF;
	END IF;
    
    IF tmp_o_ol_cnt > 1 
    THEN
      SET tmp_i_id = ol_i_id2;
      SET tmp_ol_supply_w_id = ol_supply_w_id2;
      SET tmp_ol_quantity = ol_quantity2;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 
      THEN
	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                    	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 2, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 2 THEN

      SET tmp_i_id = ol_i_id3;
      SET tmp_ol_supply_w_id = ol_supply_w_id3;
      SET tmp_ol_quantity = ol_quantity3;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 3, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 3 THEN

      SET tmp_i_id = ol_i_id4;
      SET tmp_ol_supply_w_id = ol_supply_w_id4;
      SET tmp_ol_quantity = ol_quantity4;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                    	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 4, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 4 THEN

      SET tmp_i_id = ol_i_id5;
      SET tmp_ol_supply_w_id = ol_supply_w_id5;
      SET tmp_ol_quantity = ol_quantity5;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 5, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 5 THEN
      SET tmp_i_id = ol_i_id6;
      SET tmp_ol_supply_w_id = ol_supply_w_id6;
      SET tmp_ol_quantity = ol_quantity6;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                     	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 6, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 6 THEN
      SET tmp_i_id = ol_i_id7;
      SET tmp_ol_supply_w_id = ol_supply_w_id7;
      SET tmp_ol_quantity = ol_quantity7;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;

	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                   	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 7, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 7 THEN
      SET tmp_i_id = ol_i_id8;
      SET tmp_ol_supply_w_id = ol_supply_w_id8;
      SET tmp_ol_quantity = ol_quantity8;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
        call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
		         tmp_i_name, tmp_i_data,
		         out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 8, tmp_s_quantity);

        SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 8 THEN
      SET tmp_i_id = ol_i_id9;
      SET tmp_ol_supply_w_id = ol_supply_w_id9;
      SET tmp_ol_quantity = ol_quantity9;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
        call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
                         tmp_i_name, tmp_i_data,
		         out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 9, tmp_s_quantity);

        SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 9 THEN
      SET tmp_i_id = ol_i_id10;
      SET tmp_ol_supply_w_id = ol_supply_w_id10;
      SET tmp_ol_quantity = ol_quantity10;

      SELECT i_price, i_name, i_data 
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
	                 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 10, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 10 THEN
      SET tmp_i_id = ol_i_id11;
      SET tmp_ol_supply_w_id = ol_supply_w_id11;
      SET tmp_ol_quantity = ol_quantity11;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
	             	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 11, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 11 THEN
      SET tmp_i_id = ol_i_id12;
      SET tmp_ol_supply_w_id = ol_supply_w_id12;
      SET tmp_ol_quantity = ol_quantity12;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
 	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
 	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
           	         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 12, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 12 THEN
      SET tmp_i_id = ol_i_id13;
      SET tmp_ol_supply_w_id = ol_supply_w_id13;
      SET tmp_ol_quantity = ol_quantity13;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
 	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                   	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 13, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 13 THEN
      SET tmp_i_id = ol_i_id14;
      SET tmp_ol_supply_w_id = ol_supply_w_id14;
      SET tmp_ol_quantity = ol_quantity14;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 14, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 14 THEN

      SET tmp_i_id = ol_i_id15;
      SET tmp_ol_supply_w_id = ol_supply_w_id15;
      SET tmp_ol_quantity = ol_quantity15;

      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
 	SET tmp_ol_amount = tmp_i_price * tmp_ol_quantity;
	call new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                  	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 15, tmp_s_quantity);

	SET tmp_total_amount = tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

END
'''


def filterPermutationWithConstraint(all_permutations, constraints):
    permutation_with_constraint = []
    for p in all_permutations:
        # check whether this permutation is validate
        flag = True
        for constraint in constraints:
            if constraint[0] < len(p) and constraint[1] < len(p):
                firstElementPos = p.index(constraint[0])
                secondElementPos = p.index(constraint[1])
                if firstElementPos > secondElementPos:
                    flag = False
                    break
        if flag:
            permutation_with_constraint.append(list(p))
    # print "permutation_with_constraint"
    # print permutation_with_constraint
    return permutation_with_constraint


# create store procedure for delivery
payment_unit = 7
delivery_unit = 7
new_order_unit = 5

payment_unit_constraint = [(4, 5), (0, 6), (2, 6), (4, 6)]
delivery_unit_constraint = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (2, 6), (5, 6)]
new_order_unit_constraint = [(2, 3), (2, 4), (3, 4)]

payment_permutations = itertools.permutations(range(payment_unit))
validate_payment_permutations = filterPermutationWithConstraint(payment_permutations, payment_unit_constraint)

delivery_permutations = itertools.permutations(range(delivery_unit))
validate_delivery_permutations = filterPermutationWithConstraint(delivery_permutations, delivery_unit_constraint)

new_order_permutations = itertools.permutations(range(new_order_unit))
validate_new_order_permutation = filterPermutationWithConstraint(new_order_permutations, new_order_unit_constraint)

i = 0
for delivery_permutation in validate_delivery_permutations:
    delivery_sql_unit = TXN_UNIT["DELIVERY"]
    delivery_procedure_sql = delivery_format % (
    i, delivery_sql_unit[delivery_permutation[0]], delivery_sql_unit[delivery_permutation[1]],
    delivery_sql_unit[delivery_permutation[2]], delivery_sql_unit[delivery_permutation[3]],
    delivery_sql_unit[delivery_permutation[4]], delivery_sql_unit[delivery_permutation[5]],
    delivery_sql_unit[delivery_permutation[6]])
    # print delivery_procedure_sql
    cursor.execute("DROP procedure IF EXISTS delivery_%d" % i)
    cursor.execute(delivery_procedure_sql)
    i += 1
print i

i = 0
for payment_permutation in validate_payment_permutations:
    payment_sql_unit = TXN_UNIT["PAYMENT"]
    payment_procedure_sql = payment_format % (
    i, payment_sql_unit[payment_permutation[0]], payment_sql_unit[payment_permutation[1]],
    payment_sql_unit[payment_permutation[2]], payment_sql_unit[payment_permutation[3]],
    payment_sql_unit[payment_permutation[4]], payment_sql_unit[payment_permutation[5]],
    payment_sql_unit[payment_permutation[6]])
    # print delivery_procedure_sql
    cursor.execute("DROP procedure IF EXISTS payment_%d" % i)
    cursor.execute(payment_procedure_sql)
    i += 1
print i

i = 0
for new_order_permutation in validate_new_order_permutation:
    new_order_sql_unit = TXN_UNIT["NEWORDER"]
    new_order_procedure_sql = new_order_format % (
    i, new_order_sql_unit[new_order_permutation[0]], new_order_sql_unit[new_order_permutation[1]],
    new_order_sql_unit[new_order_permutation[2]], new_order_sql_unit[new_order_permutation[3]],
    new_order_sql_unit[new_order_permutation[4]])
    # print delivery_procedure_sql
    cursor.execute("DROP procedure IF EXISTS new_order_%d" % i)
    cursor.execute(new_order_procedure_sql)
    i += 1
print i

new_order_inner_procedure = '''
CREATE PROCEDURE `new_order_inner`(in_w_id INT,
	                      in_d_id INT,
	                      in_ol_i_id INT,
	                      in_ol_quantity INT,
	                      in_i_price NUMERIC,
	                      in_i_name TEXT,
	                      in_i_data TEXT,
	                      in_ol_o_id INT,
	                      in_ol_amount NUMERIC,
	                      in_ol_supply_w_id INT,
	                      in_ol_number INT,
                              out out_s_quantity INT)
BEGIN

DECLARE	tmp_s_dist VARCHAR(255);
DECLARE	tmp_s_data VARCHAR(255);

	/* 6 */
	IF in_d_id = 1 THEN
		SELECT s_quantity, s_dist_01, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 2 THEN
		SELECT s_quantity, s_dist_02, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 3 THEN
		SELECT s_quantity, s_dist_03, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 4 THEN
		SELECT s_quantity, s_dist_04, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 5 THEN
		SELECT s_quantity, s_dist_05, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 6 THEN
		SELECT s_quantity, s_dist_06, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 7 THEN
		SELECT s_quantity, s_dist_07, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 8 THEN
		SELECT s_quantity, s_dist_08, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 9 THEN
		SELECT s_quantity, s_dist_09, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 10 THEN
		SELECT s_quantity, s_dist_10, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	END IF;

	/* 7 */
	IF out_s_quantity > in_ol_quantity + 10 THEN
		UPDATE stock
		SET s_quantity = s_quantity - in_ol_quantity
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSE
		UPDATE stock
		SET s_quantity = s_quantity - in_ol_quantity + 91
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	END IF;

	/* 8 */
	INSERT INTO order_line (ol_o_id, ol_d_id, ol_w_id, ol_number, ol_i_id,
	                        ol_supply_w_id, ol_delivery_d, ol_quantity,
                                ol_amount, ol_dist_info)
	VALUES (in_ol_o_id, in_d_id, in_w_id, in_ol_number, in_ol_i_id,
	        in_ol_supply_w_id, NULL, in_ol_quantity, in_ol_amount,
	        tmp_s_dist);
END
'''

stock_level_procedure = '''
CREATE PROCEDURE `stock_level`(in_w_id INT,
                             in_d_id INT,
                             in_threshold INT,
                             OUT low_stock INT)
BEGIN

  DECLARE tmp_d_next_o_id INT;

  SELECT d_next_o_id
  INTO tmp_d_next_o_id
  FROM district
  WHERE d_w_id = in_w_id
    AND d_id = in_d_id;

  SELECT count(*)
  INTO low_stock
  FROM order_line, stock, district
  WHERE d_id = in_d_id
        AND d_w_id = in_w_id
        AND d_id = ol_d_id
        AND d_w_id = ol_w_id
        AND ol_i_id = s_i_id
        AND ol_w_id = s_w_id
        AND s_quantity < in_threshold
        AND ol_o_id BETWEEN (tmp_d_next_o_id - 20)
                        AND (tmp_d_next_o_id - 1);

END
'''

order_status_procedure = '''
CREATE PROCEDURE `order_status`(in_c_id INT,
         	               in_c_w_id INT,
	                       in_c_d_id INT,
	                       in_c_last TEXT)
BEGIN
DECLARE out_c_first TEXT;
DECLARE out_c_middle char(2);
DECLARE out_c_balance NUMERIC;
DECLARE out_o_id INT;
DECLARE out_o_carrier_id INT;
DECLARE out_o_entry_d VARCHAR(28);
DECLARE out_o_ol_cnt INT;
DECLARE out_ol_supply_w_id1 INT; 
DECLARE out_ol_i_id1 INT;
DECLARE out_ol_quantity1 INT; 
DECLARE out_ol_amount1 NUMERIC;
DECLARE out_ol_delivery_d1 VARCHAR(28);
DECLARE out_ol_supply_w_id2 INT;
DECLARE out_ol_i_id2 INT;
DECLARE out_ol_quantity2 INT;
DECLARE out_ol_amount2 NUMERIC;
DECLARE out_ol_delivery_d2 VARCHAR(28);
DECLARE out_ol_supply_w_id3 INT;
DECLARE out_ol_i_id3 INT;
DECLARE out_ol_quantity3 INT;
DECLARE out_ol_amount3 NUMERIC;
DECLARE out_ol_delivery_d3 VARCHAR(28);
DECLARE out_ol_supply_w_id4 INT;
DECLARE out_ol_i_id4 INT;
DECLARE out_ol_quantity4 INT; 
DECLARE out_ol_amount4 NUMERIC;
DECLARE out_ol_delivery_d4 VARCHAR(28);
DECLARE out_ol_supply_w_id5 INT; 
DECLARE out_ol_i_id5 INT;
DECLARE out_ol_quantity5 INT; 
DECLARE out_ol_amount5 NUMERIC;
DECLARE out_ol_delivery_d5 VARCHAR(28);
DECLARE out_ol_supply_w_id6 INT; 
DECLARE out_ol_i_id6 INT;
DECLARE out_ol_quantity6 INT; 
DECLARE out_ol_amount6 NUMERIC;
DECLARE out_ol_delivery_d6 VARCHAR(28);
DECLARE out_ol_supply_w_id7 INT; 
DECLARE out_ol_i_id7 INT;
DECLARE out_ol_quantity7 INT; 
DECLARE out_ol_amount7 NUMERIC;
DECLARE out_ol_delivery_d7 VARCHAR(28);
DECLARE out_ol_supply_w_id8 INT; 
DECLARE out_ol_i_id8 INT;
DECLARE out_ol_quantity8 INT; 
DECLARE out_ol_amount8 NUMERIC;
DECLARE out_ol_delivery_d8 VARCHAR(28);
DECLARE out_ol_supply_w_id9 INT; 
DECLARE out_ol_i_id9 INT;
DECLARE out_ol_quantity9 INT; 
DECLARE out_ol_amount9 NUMERIC;
DECLARE out_ol_delivery_d9 VARCHAR(28);
DECLARE out_ol_supply_w_id10 INT; 
DECLARE out_ol_i_id10 INT;
DECLARE out_ol_quantity10 INT; 
DECLARE out_ol_amount10 NUMERIC;
DECLARE out_ol_delivery_d10 VARCHAR(28);
DECLARE out_ol_supply_w_id11 INT; 
DECLARE out_ol_i_id11 INT;
DECLARE out_ol_quantity11 INT; 
DECLARE out_ol_amount11 NUMERIC;
DECLARE out_ol_delivery_d11 VARCHAR(28);
DECLARE out_ol_supply_w_id12 INT; 
DECLARE out_ol_i_id12 INT;
DECLARE out_ol_quantity12 INT; 
DECLARE out_ol_amount12 NUMERIC;
DECLARE out_ol_delivery_d12 VARCHAR(28);
DECLARE out_ol_supply_w_id13 INT; 
DECLARE out_ol_i_id13 INT;
DECLARE out_ol_quantity13 INT; 
DECLARE out_ol_amount13 NUMERIC;
DECLARE out_ol_delivery_d13 VARCHAR(28);
DECLARE out_ol_supply_w_id14 INT; 
DECLARE out_ol_i_id14 INT;
DECLARE out_ol_quantity14 INT; 
DECLARE out_ol_amount14 NUMERIC;
DECLARE out_ol_delivery_d14 VARCHAR(28);
DECLARE out_ol_supply_w_id15 INT; 
DECLARE out_ol_i_id15 INT;
DECLARE out_ol_quantity15 INT; 
DECLARE out_ol_amount15 NUMERIC;
DECLARE out_ol_delivery_d15 VARCHAR(28);

	DECLARE out_c_id INT;
	DECLARE out_c_last VARCHAR(255);
        declare rc int default 0;

        declare c cursor for SELECT ol_i_id, ol_supply_w_id, ol_quantity, 
                                    ol_amount, ol_delivery_d
                             FROM order_line
                             WHERE ol_w_id = in_c_w_id
                               AND ol_d_id = in_c_d_id
                               AND ol_o_id = out_o_id;

        declare continue handler for sqlstate '02000' set rc = 1;









	
	IF in_c_id = 0 THEN
		SELECT c_id
		INTO out_c_id 
		FROM customer
		WHERE c_w_id = in_c_w_id
		  AND c_d_id = in_c_d_id
		  AND c_last = in_c_last
		ORDER BY c_first ASC limit 1;
	ELSE
		set out_c_id = in_c_id;
	END IF;

	SELECT c_first, c_middle, c_last, c_balance
	INTO out_c_first, out_c_middle, out_c_last, out_c_balance
	FROM customer
	WHERE c_w_id = in_c_w_id   
	  AND c_d_id = in_c_d_id
	  AND c_id = out_c_id;

	SELECT o_id, o_carrier_id, o_entry_d, o_ol_cnt
	INTO out_o_id, out_o_carrier_id, out_o_entry_d, out_o_ol_cnt
	FROM orders
	WHERE o_w_id = in_c_w_id
  	AND o_d_id = in_c_d_id
  	AND o_c_id = out_c_id
	ORDER BY o_id DESC limit 1;

        open c;

        fetch_block:
        BEGIN
         fetch c into out_ol_i_id1, out_ol_supply_w_id1, out_ol_quantity1, 
                      out_ol_amount1, out_ol_delivery_d1;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id2, out_ol_supply_w_id2, out_ol_quantity2, 
                      out_ol_amount2, out_ol_delivery_d2;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id3, out_ol_supply_w_id3, out_ol_quantity3, 
                      out_ol_amount3, out_ol_delivery_d3;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id4, out_ol_supply_w_id4, out_ol_quantity4, 
                      out_ol_amount4, out_ol_delivery_d4;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id5, out_ol_supply_w_id5, out_ol_quantity5, 
                      out_ol_amount5, out_ol_delivery_d5;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id6, out_ol_supply_w_id6, out_ol_quantity6, 
                      out_ol_amount6, out_ol_delivery_d6;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id7, out_ol_supply_w_id7, out_ol_quantity7, 
                      out_ol_amount7, out_ol_delivery_d7;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id8, out_ol_supply_w_id8, out_ol_quantity8, 
                      out_ol_amount8, out_ol_delivery_d8;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id9, out_ol_supply_w_id9, out_ol_quantity9, 
                      out_ol_amount9, out_ol_delivery_d9;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id10, out_ol_supply_w_id10, out_ol_quantity10, 
                      out_ol_amount10, out_ol_delivery_d10;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id11, out_ol_supply_w_id11, out_ol_quantity11, 
                      out_ol_amount11, out_ol_delivery_d11;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id12, out_ol_supply_w_id12, out_ol_quantity12, 
                      out_ol_amount12, out_ol_delivery_d12;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id13, out_ol_supply_w_id13, out_ol_quantity13, 
                      out_ol_amount13, out_ol_delivery_d13;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id14, out_ol_supply_w_id14, out_ol_quantity14, 
                      out_ol_amount14, out_ol_delivery_d14;
         if rc then
            leave fetch_block;
         end if;
         fetch c into out_ol_i_id15, out_ol_supply_w_id15, out_ol_quantity15, 
                      out_ol_amount15, out_ol_delivery_d15;
       end fetch_block;

       close c;

END
'''

cursor.execute("DROP procedure IF EXISTS new_order_inner")
cursor.execute(new_order_inner_procedure)
cursor.execute("DROP procedure IF EXISTS stock_level")
cursor.execute(stock_level_procedure)
cursor.execute("DROP procedure IF EXISTS order_status")
cursor.execute(order_status_procedure)