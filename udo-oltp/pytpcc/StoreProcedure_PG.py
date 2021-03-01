
import psycopg2
import itertools

config = {
    "host": "127.0.0.1",
    "db": "tpcc",
    "user": "postgres",
    "passwd": "jw2544"
}

conn = psycopg2.connect("dbname='%s' user='%s'" % (config["db"], config["user"]))
conn.autocommit = True
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
                    out_c_id := in_c_id;
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

                    out_c_data := concat(tmp_c_id,' ',tmp_c_d_id,' ',tmp_c_w_id,' ',tmp_d_id,' ',tmp_w_id);

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
            tmp_h_data := concat(out_w_name,' ', out_d_name);
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
         
                o_id := out_d_next_o_id;
         
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
CREATE OR REPLACE FUNCTION delivery_%d(in_w_id INT, in_o_carrier_id INT, d_total INT) RETURNS VOID
    AS $$
   

       DECLARE      out_c_id INT;
            out_ol_amount INT;
       	tmp_d_id INT;
       	tmp_o_id INT default 0;
    BEGIN
    
        tmp_d_id := 1;
        while tmp_d_id <= d_total LOOP
        BEGIN
        
            tmp_o_id:= 0;
            
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
    
         tmp_d_id := tmp_d_id + 1;
    
       END;
       END LOOP;
       
       EXCEPTION
        WHEN serialization_failure OR deadlock_detected OR no_data_found
            THEN ROLLBACK;
            
    END;
 $$ LANGUAGE plpgsql;
'''

payment_format = '''
CREATE OR REPLACE FUNCTION payment_%d(in_w_id INT, in_d_id INT, in_c_id INT, in_c_w_id INT, in_c_d_id INT,
                         in_c_last VARCHAR(16), in_h_amount REAL) RETURNS VOID
AS $$


DECLARE  out_w_name VARCHAR(10);
  out_w_street_1 VARCHAR(20);
  out_w_street_2 VARCHAR(20);
  out_w_city VARCHAR(20);
  out_w_state VARCHAR(2);
  out_w_zip VARCHAR(9);

  out_d_name VARCHAR(10);
  out_d_street_1 VARCHAR(20);
  out_d_street_2 VARCHAR(20);
  out_d_city VARCHAR(20);
  out_d_state VARCHAR(2);
  out_d_zip VARCHAR(9);

  out_c_id INTEGER;
  out_c_first VARCHAR(16);
  out_c_middle VARCHAR(2);
  out_c_last VARCHAR(20);
  out_c_street_1 VARCHAR(20);
  out_c_street_2 VARCHAR(20);
  out_c_city VARCHAR(20);
  out_c_state VARCHAR(2);
  out_c_zip VARCHAR(9);
  out_c_phone VARCHAR(16);
  out_c_since VARCHAR(28);
  out_c_credit VARCHAR(2);
  out_c_credit_lim decimal(24, 12);
  out_c_discount REAL;
  out_c_balance NUMERIC(10,0);
  out_c_data VARCHAR(500);
  out_c_ytd_payment INTEGER;


--        /* Goofy temporaty variables. */
  tmp_c_id VARCHAR(30);
  tmp_c_d_id VARCHAR(30);
  tmp_c_w_id VARCHAR(30);
  tmp_d_id VARCHAR(30);
  tmp_w_id VARCHAR(30);
  tmp_h_amount VARCHAR(30);

--        /* This one is not goofy. */
  tmp_h_data VARCHAR(30);
BEGIN

        %s

        %s

        %s

        %s

        %s
        
        %s
        
        %s
    
    EXCEPTION
        WHEN serialization_failure OR deadlock_detected OR no_data_found
            THEN ROLLBACK;
                        
END;
$$ LANGUAGE plpgsql;
'''

new_order_format = '''
CREATE OR REPLACE FUNCTION new_order_%d(tmp_w_id INT,           
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
                           ol_quantity15 INT) RETURNS VOID
AS $$


  DECLARE out_c_credit VARCHAR(255);
  tmp_i_name VARCHAR(255);
  tmp_i_data VARCHAR(255);
  out_c_last VARCHAR(255);

  tmp_ol_supply_w_id INT;
  tmp_ol_quantity INT;
  out_d_next_o_id INT;
  tmp_i_id INT;

  tmp_s_quantity INT;

  out_w_tax REAL;
  out_d_tax REAL;
  out_c_discount REAL;
  tmp_i_price REAL;
  tmp_ol_amount REAL;
  tmp_total_amount REAL;

  o_id INT;
BEGIN

  o_id := 0;

  /* SQLINES DEMO *** te */
  
  %s
  
  %s
  
  %s
  
  %s
  
  %s
  
  tmp_total_amount := 0;

    IF tmp_o_ol_cnt > 0 
    THEN

      tmp_i_id := ol_i_id1;
      tmp_ol_supply_w_id := ol_supply_w_id1;
      tmp_ol_quantity := ol_quantity1;

	  /* 5 */
      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 
      THEN
		tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

		SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
							 tmp_ol_quantity, tmp_i_price,
				 tmp_i_name, tmp_i_data,
				 out_d_next_o_id, tmp_ol_amount,
							 tmp_ol_supply_w_id, 1) into tmp_s_quantity;

		tmp_total_amount := tmp_ol_amount;
		  END IF;
	END IF;
    
    IF tmp_o_ol_cnt > 1 
    THEN
      tmp_i_id := ol_i_id2;
      tmp_ol_supply_w_id := ol_supply_w_id2;
      tmp_ol_quantity := ol_quantity2;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 
      THEN
	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                    	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 2) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 2 THEN

      tmp_i_id := ol_i_id3;
      tmp_ol_supply_w_id := ol_supply_w_id3;
      tmp_ol_quantity := ol_quantity3;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 3) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 3 THEN

      tmp_i_id := ol_i_id4;
      tmp_ol_supply_w_id := ol_supply_w_id4;
      tmp_ol_quantity := ol_quantity4;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                    	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 4) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 4 THEN

      tmp_i_id := ol_i_id5;
      tmp_ol_supply_w_id := ol_supply_w_id5;
      tmp_ol_quantity := ol_quantity5;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 5) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 5 THEN
      tmp_i_id := ol_i_id6;
      tmp_ol_supply_w_id := ol_supply_w_id6;
      tmp_ol_quantity := ol_quantity6;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                     	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 6) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 6 THEN
      tmp_i_id := ol_i_id7;
      tmp_ol_supply_w_id := ol_supply_w_id7;
      tmp_ol_quantity := ol_quantity7;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;

	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                   	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 7) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 7 THEN
      tmp_i_id := ol_i_id8;
      tmp_ol_supply_w_id := ol_supply_w_id8;
      tmp_ol_quantity := ol_quantity8;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
        SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
		         tmp_i_name, tmp_i_data,
		         out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 8) into tmp_s_quantity;

        tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    IF tmp_o_ol_cnt > 8 THEN
      tmp_i_id := ol_i_id9;
      tmp_ol_supply_w_id := ol_supply_w_id9;
      tmp_ol_quantity := ol_quantity9;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
        SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
                         tmp_i_name, tmp_i_data,
		         out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 9) into tmp_s_quantity;

        tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 9 THEN
      tmp_i_id := ol_i_id10;
      tmp_ol_supply_w_id := ol_supply_w_id10;
      tmp_ol_quantity := ol_quantity10;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data 
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
	                 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 10) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 10 THEN
      tmp_i_id := ol_i_id11;
      tmp_ol_supply_w_id := ol_supply_w_id11;
      tmp_ol_quantity := ol_quantity11;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
        tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
	             	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 11) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 11 THEN
      tmp_i_id := ol_i_id12;
      tmp_ol_supply_w_id := ol_supply_w_id12;
      tmp_ol_quantity := ol_quantity12;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
 	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
 	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
           	         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 12) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 12 THEN
      tmp_i_id := ol_i_id13;
      tmp_ol_supply_w_id := ol_supply_w_id13;
      tmp_ol_quantity := ol_quantity13;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
 	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                   	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 13) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 13 THEN
      tmp_i_id := ol_i_id14;
      tmp_ol_supply_w_id := ol_supply_w_id14;
      tmp_ol_quantity := ol_quantity14;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                         tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 14) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;

    IF tmp_o_ol_cnt > 14 THEN

      tmp_i_id := ol_i_id15;
      tmp_ol_supply_w_id := ol_supply_w_id15;
      tmp_ol_quantity := ol_quantity15;

      -- SQLINES LICENSE FOR EVALUATION USE ONLY
      SELECT i_price, i_name, i_data
      INTO tmp_i_price, tmp_i_name, tmp_i_data
      FROM item
      WHERE i_id = tmp_i_id;

      IF tmp_i_price > 0 THEN
 	tmp_ol_amount := tmp_i_price * tmp_ol_quantity;
	SELECT * FROM new_order_inner(tmp_w_id, tmp_d_id, tmp_i_id,
                  	 tmp_ol_quantity, tmp_i_price,
			 tmp_i_name, tmp_i_data,
			 out_d_next_o_id, tmp_ol_amount,
                         tmp_ol_supply_w_id, 15) into tmp_s_quantity;

	tmp_total_amount := tmp_total_amount + tmp_ol_amount;
      END IF;
    END IF;
    
    EXCEPTION
        WHEN serialization_failure OR deadlock_detected OR no_data_found
            THEN ROLLBACK;

END;
$$ LANGUAGE plpgsql;
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
    cursor.execute("DROP FUNCTION IF EXISTS delivery_%d;" % i)
    cursor.execute(delivery_procedure_sql)
    i += 1
print(i)

i = 0
for payment_permutation in validate_payment_permutations:
    payment_sql_unit = TXN_UNIT["PAYMENT"]
    payment_procedure_sql = payment_format % (
        i, payment_sql_unit[payment_permutation[0]], payment_sql_unit[payment_permutation[1]],
        payment_sql_unit[payment_permutation[2]], payment_sql_unit[payment_permutation[3]],
        payment_sql_unit[payment_permutation[4]], payment_sql_unit[payment_permutation[5]],
        payment_sql_unit[payment_permutation[6]])
    # print delivery_procedure_sql
    cursor.execute("DROP FUNCTION IF EXISTS payment_%d;" % i)
    cursor.execute(payment_procedure_sql)
    i += 1
print(i)

i = 0
for new_order_permutation in validate_new_order_permutation:
    new_order_sql_unit = TXN_UNIT["NEWORDER"]
    new_order_procedure_sql = new_order_format % (
        i, new_order_sql_unit[new_order_permutation[0]], new_order_sql_unit[new_order_permutation[1]],
        new_order_sql_unit[new_order_permutation[2]], new_order_sql_unit[new_order_permutation[3]],
        new_order_sql_unit[new_order_permutation[4]])
    # print delivery_procedure_sql
    cursor.execute("DROP FUNCTION IF EXISTS new_order_%d;" % i)
    cursor.execute(new_order_procedure_sql)
    i += 1
print(i)

new_order_inner_procedure = '''
-- SQLINES LICENSE FOR EVALUATION USE ONLY
CREATE OR REPLACE FUNCTION new_order_inner(in_w_id INT,
	                      in_d_id INT,
	                      in_ol_i_id INT,
	                      in_ol_quantity INT,
	                      in_i_price real,
	                      in_i_name character varying,
	                      in_i_data character varying,
	                      in_ol_o_id INT,
	                      in_ol_amount real,
	                      in_ol_supply_w_id INT,
	                      in_ol_number INT,
                          out out_s_quantity INT)
AS $$


DECLARE	tmp_s_dist VARCHAR(255);
	tmp_s_data VARCHAR(255);
BEGIN

	/* 6 */
	IF in_d_id = 1 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_01, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 2 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_02, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 3 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_03, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 4 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_04, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 5 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_05, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 6 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_06, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 7 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_07, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 8 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_08, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 9 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT s_quantity, s_dist_09, s_data
		INTO out_s_quantity, tmp_s_dist, tmp_s_data
		FROM stock
		WHERE s_i_id = in_ol_i_id
		  AND s_w_id = in_w_id;
	ELSEIF in_d_id = 10 THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
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
	        
	EXCEPTION
        WHEN serialization_failure OR deadlock_detected OR no_data_found
            THEN ROLLBACK;
            
END;
$$ LANGUAGE plpgsql;
'''

stock_level_procedure = '''
CREATE OR REPLACE FUNCTION stock_level(in_w_id INT,
                             in_d_id INT,
                             in_threshold INT,
                             OUT low_stock INT)
AS $$


  DECLARE tmp_d_next_o_id INT;
BEGIN

  -- SQLINES LICENSE FOR EVALUATION USE ONLY
  SELECT d_next_o_id
  INTO tmp_d_next_o_id
  FROM district
  WHERE d_w_id = in_w_id
    AND d_id = in_d_id;

  -- SQLINES LICENSE FOR EVALUATION USE ONLY
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
                        
  EXCEPTION
        WHEN serialization_failure OR deadlock_detected OR no_data_found
            THEN ROLLBACK;

END;
$$ LANGUAGE plpgsql;
'''

order_status_procedure = '''
CREATE OR REPLACE FUNCTION order_status(in_c_id INT,
         	               in_c_w_id INT,
	                       in_c_d_id INT,
	                       in_c_last TEXT,
	                       OUT os_c_line TEXT) 
AS $$

DECLARE out_c_first TEXT;
 out_c_middle char(2);
 out_c_balance NUMERIC(10,0);
 out_o_id INT;
 out_o_carrier_id INT;
 out_o_entry_d VARCHAR(28);
 out_o_ol_cnt INT;
 out_c_id INT;
 out_c_last VARCHAR(255);
 os_ol RECORD;

BEGIN
	
	IF in_c_id = 0 or in_c_id is NULL THEN
		-- SQLINES LICENSE FOR EVALUATION USE ONLY
		SELECT c_id
		INTO out_c_id 
		FROM customer
		WHERE c_w_id = in_c_w_id
		  AND c_d_id = in_c_d_id
		  AND c_last = in_c_last
		ORDER BY c_first ASC limit 1;
	ELSE
		out_c_id := in_c_id;
	END IF;

	-- SQLINES LICENSE FOR EVALUATION USE ONLY
	SELECT c_first, c_middle, c_last, c_balance
	INTO out_c_first, out_c_middle, out_c_last, out_c_balance
	FROM customer
	WHERE c_w_id = in_c_w_id   
	  AND c_d_id = in_c_d_id
	  AND c_id = out_c_id;

	-- SQLINES LICENSE FOR EVALUATION USE ONLY
	SELECT o_id, o_carrier_id, o_entry_d, o_ol_cnt
	INTO out_o_id, out_o_carrier_id, out_o_entry_d, out_o_ol_cnt
	FROM orders
	WHERE o_w_id = in_c_w_id
  	AND o_d_id = in_c_d_id
  	AND o_c_id = out_c_id
	ORDER BY o_id DESC limit 1;
    
    os_c_line := '';
                              
    FOR os_ol IN
    SELECT ol_i_id, ol_supply_w_id, ol_quantity, ol_amount, ol_delivery_d, out_o_id, out_o_entry_d, out_o_carrier_id
      FROM order_line
     WHERE ol_o_id = out_o_id AND ol_d_id = in_c_d_id AND ol_w_id = in_c_w_id
    LOOP
        os_c_line := os_c_line || ',' || os_ol.ol_i_id || ',' || os_ol.ol_supply_w_id || ',' || os_ol.ol_quantity || ',' || os_ol.ol_amount || ',' || os_ol.ol_delivery_d;
    END LOOP;
    
    EXCEPTION
    WHEN serialization_failure OR deadlock_detected OR no_data_found
        THEN ROLLBACK;  

END;
$$ LANGUAGE plpgsql;
'''

cursor.execute("DROP function IF EXISTS new_order_inner")
cursor.execute(new_order_inner_procedure)
cursor.execute("DROP function IF EXISTS stock_level")
cursor.execute(stock_level_procedure)
cursor.execute("DROP function IF EXISTS order_status")
cursor.execute(order_status_procedure)