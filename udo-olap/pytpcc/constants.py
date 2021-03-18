# PG version of TPCH
# QUERIES = {
#     "q1": '''
#         select
#             l_returnflag,
#             l_linestatus,
#             sum(l_quantity) as sum_qty,
#             sum(l_extendedprice) as sum_base_price,
#             sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
#             sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
#             avg(l_quantity) as avg_qty,
#             avg(l_extendedprice) as avg_price,
#             avg(l_discount) as avg_disc,
#             count(l_quantity) as count_order
#         from
#             lineitem
#         where
#             l_shipdate <= date '1998-12-01' - interval '117' day
#         group by
#             l_returnflag,
#             l_linestatus
#         order by
#             l_returnflag,
#             l_linestatus
#         limit 1;''',
#     "q2": '''
#         select
#             s_acctbal,
#             s_name,
#             n_name,
#             p_partkey,
#             p_mfgr,
#             s_address,
#             s_phone,
#             s_comment
#         from
#             part,
#             supplier,
#             partsupp,
#             nation,
#             region
#         where
#             p_partkey = ps_partkey
#             and s_suppkey = ps_suppkey
#             and p_size = 25
#             and p_type like '%STEEL'
#             and s_nationkey = n_nationkey
#             and n_regionkey = r_regionkey
#             and r_name = 'EUROPE'
#             and ps_supplycost = (
#                 select
#                     min(ps_supplycost)
#                 from
#                     partsupp,
#                     supplier,
#                     nation,
#                     region
#                 where
#                     p_partkey = ps_partkey
#                     and s_suppkey = ps_suppkey
#                     and s_nationkey = n_nationkey
#                     and n_regionkey = r_regionkey
#                     and r_name = 'EUROPE'
#             )
#         order by
#             s_acctbal desc,
#             n_name,
#             s_name,
#             p_partkey
#         LIMIT 1;
#     ''',
#     "q3": '''
#         select
#             l_orderkey,
#             sum(l_extendedprice * (1 - l_discount)) as revenue,
#             o_orderdate,
#             o_shippriority
#         from
#             customer,
#             orders,
#             lineitem
#         where
#             c_mktsegment = 'HOUSEHOLD'
#             and c_custkey = o_custkey
#             and l_orderkey = o_orderkey
#             and o_orderdate < date '1995-03-21'
#             and l_shipdate > date '1995-03-21'
#         group by
#             l_orderkey,
#             o_orderdate,
#             o_shippriority
#         order by
#             revenue desc,
#             o_orderdate
#         limit 10;
#     ''',
#     "q4": '''
#         select
#             o_orderpriority,
#             count(*) as order_count
#         from
#             orders
#         where
#             o_orderdate >= date '1996-03-01'
#             and o_orderdate < date '1996-03-01' + interval '3' month
#             and exists (
#                 select
#                     *
#                 from
#                     lineitem
#                 where
#                     l_orderkey = o_orderkey
#                     and l_commitdate < l_receiptdate
#             )
#         group by
#             o_orderpriority
#         order by
#             o_orderpriority
#         limit 1;
#     ''',
#     "q5": '''
#         select
#             n_name,
#             sum(l_extendedprice * (1 - l_discount)) as revenue
#         from
#             customer,
#             orders,
#             lineitem,
#             supplier,
#             nation,
#             region
#         where
#             c_custkey = o_custkey
#             and l_orderkey = o_orderkey
#             and l_suppkey = s_suppkey
#             and c_nationkey = s_nationkey
#             and s_nationkey = n_nationkey
#             and n_regionkey = r_regionkey
#             and r_name = 'AMERICA'
#             and o_orderdate >= date '1995-01-01'
#             and o_orderdate < date '1995-01-01' + interval '1' year
#         group by
#             n_name
#         order by
#             revenue desc
#         limit 1;
#     ''',
#     "q6": '''
#         select
#             sum(l_extendedprice * l_discount) as revenue
#         from
#             lineitem
#         where
#             l_shipdate >= date '1995-01-01'
#             and l_shipdate < date '1995-01-01' + interval '1' year
#             and l_discount between 0.09 - 0.01 and 0.09 + 0.01
#             and l_quantity < 24
#         limit 1;
# 	''',
#     "q7": '''
#         select
#             supp_nation,
#             cust_nation,
#             l_year,
#             sum(volume) as revenue
#         from
#             (
#                 select
#                     n1.n_name as supp_nation,
#                     n2.n_name as cust_nation,
#                     extract(year from l_shipdate) as l_year,
#                     l_extendedprice * (1 - l_discount) as volume
#                 from
#                     supplier,
#                     lineitem,
#                     orders,
#                     customer,
#                     nation n1,
#                     nation n2
#                 where
#                     s_suppkey = l_suppkey
#                     and o_orderkey = l_orderkey
#                     and c_custkey = o_custkey
#                     and s_nationkey = n1.n_nationkey
#                     and c_nationkey = n2.n_nationkey
#                     and (
#                         (n1.n_name = 'RUSSIA' and n2.n_name = 'INDIA')
#                         or (n1.n_name = 'INDIA' and n2.n_name = 'RUSSIA')
#                     )
#                     and l_shipdate between date '1995-01-01' and date '1996-12-31'
#             ) as shipping
#         group by
#             supp_nation,
#             cust_nation,
#             l_year
#         order by
#             supp_nation,
#             cust_nation,
#             l_year
#         limit 1;
#     ''',
#     "q8": '''
#         select
#             o_year,
#             sum(case
#                 when nation = 'UNITED KINGDOM' then volume
#                 else 0
#             end) / sum(volume) as mkt_share
#         from
#             (
#                 select
#                     extract(year from o_orderdate) as o_year,
#                     l_extendedprice * (1 - l_discount) as volume,
#                     n2.n_name as nation
#                 from
#                     part,
#                     supplier,
#                     lineitem,
#                     orders,
#                     customer,
#                     nation n1,
#                     nation n2,
#                     region
#                 where
#                     p_partkey = l_partkey
#                     and s_suppkey = l_suppkey
#                     and l_orderkey = o_orderkey
#                     and o_custkey = c_custkey
#                     and c_nationkey = n1.n_nationkey
#                     and n1.n_regionkey = r_regionkey
#                     and r_name = 'EUROPE'
#                     and s_nationkey = n2.n_nationkey
#                     and o_orderdate between date '1995-01-01' and date '1996-12-31'
#                     and p_type = 'PROMO PLATED COPPER'
#             ) as all_nations
#         group by
#             o_year
#         order by
#             o_year
#         limit 1;
#     ''',
#     "q9": '''
#         select
#             nation,
#             o_year,
#             sum(amount) as sum_profit
#         from
#             (
#                 select
#                     n_name as nation,
#                     extract(year from o_orderdate) as o_year,
#                     l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount
#                 from
#                     part,
#                     supplier,
#                     lineitem,
#                     partsupp,
#                     orders,
#                     nation
#                 where
#                     s_suppkey = l_suppkey
#                     and ps_suppkey = l_suppkey
#                     and ps_partkey = l_partkey
#                     and p_partkey = l_partkey
#                     and o_orderkey = l_orderkey
#                     and s_nationkey = n_nationkey
#                     and p_name like '%orchid%'
#             ) as profit
#         group by
#             nation,
#             o_year
#         order by
#             nation,
#             o_year desc
#         limit 1;
#     ''',
#     "q10": '''
#         select
#             c_custkey,
#             c_name,
#             sum(l_extendedprice * (1 - l_discount)) as revenue,
#             c_acctbal,
#             n_name,
#             c_address,
#             c_phone,
#             c_comment
#         from
#             customer,
#             orders,
#             lineitem,
#             nation
#         where
#             c_custkey = o_custkey
#             and l_orderkey = o_orderkey
#             and o_orderdate >= date '1995-01-01'
#             and o_orderdate < date '1995-01-01' + interval '3' month
#             and l_returnflag = 'R'
#             and c_nationkey = n_nationkey
#         group by
#             c_custkey,
#             c_name,
#             c_acctbal,
#             c_phone,
#             n_name,
#             c_address,
#             c_comment
#         order by
#             revenue desc
#         limit 1;
#     ''',
#     "q11": '''
#         select
#             ps_partkey,
#             sum(ps_supplycost * ps_availqty) as value
#         from
#             partsupp,
#             supplier,
#             nation
#         where
#             ps_suppkey = s_suppkey
#             and s_nationkey = n_nationkey
#             and n_name = 'ETHIOPIA'
#         group by
#             ps_partkey having
#                 sum(ps_supplycost * ps_availqty) > (
#                     select
#                         sum(ps_supplycost * ps_availqty) * 0.0001000000
#                     from
#                         partsupp,
#                         supplier,
#                         nation
#                     where
#                         ps_suppkey = s_suppkey
#                         and s_nationkey = n_nationkey
#                         and n_name = 'ETHIOPIA'
#                 )
#         order by
#             value desc
#         limit 1;
#     ''',
#     "q12": '''
#         select
#             l_shipmode,
#             sum(case
#                 when o_orderpriority = '1-URGENT'
#                     or o_orderpriority = '2-HIGH'
#                     then 1
#                 else 0
#             end) as high_line_count,
#             sum(case
#                 when o_orderpriority <> '1-URGENT'
#                     and o_orderpriority <> '2-HIGH'
#                     then 1
#                 else 0
#             end) as low_line_count
#         from
#             orders,
#             lineitem
#         where
#             o_orderkey = l_orderkey
#             and l_shipmode in ('TRUCK', 'AIR')
#             and l_commitdate < l_receiptdate
#             and l_shipdate < l_commitdate
#             and l_receiptdate >= date '1997-01-01'
#             and l_receiptdate < date '1997-01-01' + interval '1' year
#         group by
#             l_shipmode
#         order by
#             l_shipmode
#         limit 1;
#     ''',
#     "q13": '''
#         select
#             c_count,
#             count(*) as custdist
#         from
#             (
#                 select
#                     c_custkey,
#                     count(o_orderkey)
#                 from
#                     customer left outer join orders on
#                         c_custkey = o_custkey
#                         and o_comment not like '%pending%packages%'
#                 group by
#                     c_custkey
#             ) as c_orders (c_custkey, c_count)
#         group by
#             c_count
#         order by
#             custdist desc,
#             c_count desc
#         limit 1;
#     ''',
#     "q14": '''
#         select
#             100.00 * sum(case
#                 when p_type like 'PROMO%'
#                     then l_extendedprice * (1 - l_discount)
#                 else 0
#             end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue
#         from
#             lineitem,
#             part
#         where
#             l_partkey = p_partkey
#             and l_shipdate >= date '1993-11-01'
#             and l_shipdate < date '1993-11-01' + interval '1' month
#         limit 1;
#     ''',
#     "q15": '''
#         create view REVENUE0 (supplier_no, total_revenue) as select l_suppkey, sum(l_extendedprice * (1 - l_discount)) from LINEITEM where l_shipdate >= date '1997-07-01' and l_shipdate < date '1997-07-01' + interval '3' month group by l_suppkey;
#         select s_suppkey, s_name, s_address, s_phone, total_revenue from SUPPLIER, REVENUE0 where s_suppkey = supplier_no and total_revenue = ( select max(total_revenue) from REVENUE0) order by s_suppkey;
#         drop view REVENUE0;
#     ''',
#     "q16": '''
#         select
#             p_brand,
#             p_type,
#             p_size,
#             count(distinct ps_suppkey) as supplier_cnt
#         from
#             partsupp,
#             part
#         where
#             p_partkey = ps_partkey
#             and p_brand <> 'Brand#23'
#             and p_type not like 'MEDIUM BRUSHED%'
#             and p_size in (45, 35, 7, 23, 24, 18, 14, 15)
#             and ps_suppkey not in (
#                 select
#                     s_suppkey
#                 from
#                     supplier
#                 where
#                     s_comment like '%Customer%Complaints%'
#             )
#         group by
#             p_brand,
#             p_type,
#             p_size
#         order by
#             supplier_cnt desc,
#             p_brand,
#             p_type,
#             p_size
#         limit 1;
#     ''',
#     "q17": '''
#         select
#             sum(l_extendedprice) / 7.0 as avg_yearly
#         from
#             lineitem,
#             part,
#                 (select l_partkey as agg_partkey, 0.2 * avg(l_quantity) as avg_quantity from lineitem group by l_partkey) part_agg
#         where
#             p_partkey = l_partkey
#                 and agg_partkey = l_partkey
#             and p_brand = 'Brand#33'
#             and p_container = 'WRAP JAR'
#             and l_quantity < avg_quantity
#         limit 1;
#     ''',
#     "q18": '''
#         select
#             c_name,
#             c_custkey,
#             o_orderkey,
#             o_orderdate,
#             o_totalprice,
#             sum(l_quantity)
#         from
#             customer,
#             orders,
#             lineitem
#         where
#             o_orderkey in (
#                 select
#                     l_orderkey
#                 from
#                     lineitem
#                 group by
#                     l_orderkey having
#                         sum(l_quantity) > 314
#             )
#             and c_custkey = o_custkey
#             and o_orderkey = l_orderkey
#         group by
#             c_name,
#             c_custkey,
#             o_orderkey,
#             o_orderdate,
#             o_totalprice
#         order by
#             o_totalprice desc,
#             o_orderdate
#         limit 1;
#     ''',
#     "q19": '''
#         select
#             sum(l_extendedprice* (1 - l_discount)) as revenue
#         from
#             lineitem,
#             part
#         where
#             (
#                 p_partkey = l_partkey
#                 and p_brand = 'Brand#54'
#                 and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
#                 and l_quantity >= 4 and l_quantity <= 4 + 10
#                 and p_size between 1 and 5
#                 and l_shipmode in ('AIR', 'AIR REG')
#                 and l_shipinstruct = 'DELIVER IN PERSON'
#             )
#             or
#             (
#                 p_partkey = l_partkey
#                 and p_brand = 'Brand#51'
#                 and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
#                 and l_quantity >= 11 and l_quantity <= 11 + 10
#                 and p_size between 1 and 10
#                 and l_shipmode in ('AIR', 'AIR REG')
#                 and l_shipinstruct = 'DELIVER IN PERSON'
#             )
#             or
#             (
#                 p_partkey = l_partkey
#                 and p_brand = 'Brand#21'
#                 and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
#                 and l_quantity >= 28 and l_quantity <= 28 + 10
#                 and p_size between 1 and 15
#                 and l_shipmode in ('AIR', 'AIR REG')
#                 and l_shipinstruct = 'DELIVER IN PERSON'
#             )
#         limit 1;
#     ''',
#     "q20": '''select
#                 s_name,
#                 s_address
#             from
#                 supplier,
#                 nation
#             where
#                 s_suppkey in (
#                     select
#                         ps_suppkey
#                     from
#                         partsupp,
#                         (
#                             select
#                                 l_partkey agg_partkey,
#                                 l_suppkey agg_suppkey,
#                                 0.5 * sum(l_quantity) AS agg_quantity
#                             from
#                                 lineitem
#                             where
#                                 l_shipdate >= date '1997-01-01'
#                                 and l_shipdate < date '1997-01-01' + interval '1' year
#                             group by
#                                 l_partkey,
#                                 l_suppkey
#                         ) agg_lineitem
#                     where
#                         agg_partkey = ps_partkey
#                         and agg_suppkey = ps_suppkey
#                         and ps_partkey in (
#                             select
#                                 p_partkey
#                             from
#                                 part
#                             where
#                                 p_name like 'powder%'
#                         )
#                         and ps_availqty > agg_quantity
#                 )
#                 and s_nationkey = n_nationkey
#                 and n_name = 'ARGENTINA'
#             order by
#                 s_name
#             limit 1;''',
#     "q21": '''
#         select
#             s_name,
#             count(*) as numwait
#         from
#             supplier,
#             lineitem l1,
#             orders,
#             nation
#         where
#             s_suppkey = l1.l_suppkey
#             and o_orderkey = l1.l_orderkey
#             and o_orderstatus = 'F'
#             and l1.l_receiptdate > l1.l_commitdate
#             and exists (
#                 select
#                     *
#                 from
#                     lineitem l2
#                 where
#                     l2.l_orderkey = l1.l_orderkey
#                     and l2.l_suppkey <> l1.l_suppkey
#             )
#             and not exists (
#                 select
#                     *
#                 from
#                     lineitem l3
#                 where
#                     l3.l_orderkey = l1.l_orderkey
#                     and l3.l_suppkey <> l1.l_suppkey
#                     and l3.l_receiptdate > l3.l_commitdate
#             )
#             and s_nationkey = n_nationkey
#             and n_name = 'BRAZIL'
#         group by
#             s_name
#         order by
#             numwait desc,
#             s_name
#         limit 1;
#     ''',
#     "q22": '''
#         select
#             cntrycode,
#             count(*) as numcust,
#             sum(c_acctbal) as totacctbal
#         from
#             (
#                 select
#                     substring(c_phone from 1 for 2) as cntrycode,
#                     c_acctbal
#                 from
#                     customer
#                 where
#                     substring(c_phone from 1 for 2) in
#                         ('20', '10', '18', '16', '17', '29', '21')
#                     and c_acctbal > (
#                         select
#                             avg(c_acctbal)
#                         from
#                             customer
#                         where
#                             c_acctbal > 0.00
#                             and substring(c_phone from 1 for 2) in
#                                 ('20', '10', '18', '16', '17', '29', '21')
#                     )
#                     and not exists (
#                         select
#                             *
#                         from
#                             orders
#                         where
#                             o_custkey = c_custkey
#                     )
#             ) as custsale
#         group by
#             cntrycode
#         order by
#             cntrycode;
#     '''
# }


# mysql version of TPCH
QUERIES = {
    "q1": '''
        select l_returnflag, l_linestatus, sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from LINEITEM where l_shipdate <= date '1998-12-01' - interval '108' day group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus;
        ''',
    "q2": '''
        select s_acctbal, s_name, n_name, p_partkey, p_mfgr, s_address, s_phone, s_comment from PART, SUPPLIER, PARTSUPP, NATION, REGION where p_partkey = ps_partkey and s_suppkey = ps_suppkey and p_size = 30 and p_type like '%STEEL' and s_nationkey = n_nationkey and n_regionkey = r_regionkey and r_name = 'ASIA' and ps_supplycost = (select min(ps_supplycost) from PARTSUPP, SUPPLIER, NATION, REGION where p_partkey = ps_partkey and s_suppkey = ps_suppkey and s_nationkey = n_nationkey and n_regionkey = r_regionkey and r_name = 'ASIA') order by s_acctbal desc, n_name, s_name, p_partkey limit 100;
    ''',
    "q3": '''
        select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from CUSTOMER, ORDERS, LINEITEM where c_mktsegment = 'AUTOMOBILE' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < date '1995-03-13' and l_shipdate > date '1995-03-13' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10;
    ''',
    "q4": '''
        select o_orderpriority, count(*) as order_count from ORDERS where o_orderdate >= date '1995-01-01' and o_orderdate < date '1995-01-01' + interval '3' month and exists (select * from LINEITEM where l_orderkey = o_orderkey and l_commitdate < l_receiptdate) group by o_orderpriority order by o_orderpriority;
    ''',
    "q5": '''
        select n_name, sum(l_extendedprice * (1 - l_discount)) as revenue from CUSTOMER, ORDERS, LINEITEM, SUPPLIER, NATION, REGION where c_custkey = o_custkey and l_orderkey = o_orderkey and l_suppkey = s_suppkey and c_nationkey = s_nationkey and s_nationkey = n_nationkey and n_regionkey = r_regionkey and r_name = 'MIDDLE EAST' and o_orderdate >= date '1994-01-01' and o_orderdate < date '1994-01-01' + interval '1' year group by n_name order by revenue desc;
    ''',
    "q6": '''
        select
            sum(l_extendedprice * l_discount) as revenue
        from
            LINEITEM
        where
            l_shipdate >= date '1994-01-01'
            and l_shipdate < date '1994-01-01' + interval '1' year
            and l_discount between 0.06 - 0.01 and 0.06 + 0.01
            and l_quantity < 24;
	''',
    "q7": '''
        select supp_nation, cust_nation, l_year, sum(volume) as revenue from ( select n1.n_name as supp_nation, n2.n_name as cust_nation, extract(year from l_shipdate) as l_year, l_extendedprice * (1 - l_discount) as volume from SUPPLIER, LINEITEM, ORDERS, CUSTOMER, NATION n1, NATION n2 where s_suppkey = l_suppkey and o_orderkey = l_orderkey and c_custkey = o_custkey and s_nationkey = n1.n_nationkey and c_nationkey = n2.n_nationkey and ((n1.n_name = 'JAPAN' and n2.n_name = 'INDIA') or (n1.n_name = 'INDIA' and n2.n_name = 'JAPAN')) and l_shipdate between date '1995-01-01' and date '1996-12-31') as shipping group by supp_nation, cust_nation, l_year order by supp_nation, cust_nation, l_year;
    ''',
    "q8": '''
        select o_year, sum(case when nation = 'INDIA' then volume else 0 end) / sum(volume) as mkt_share from (select extract(year from o_orderdate) as o_year,	l_extendedprice * (1 - l_discount) as volume, n2.n_name as nation from PART, SUPPLIER, LINEITEM, ORDERS, CUSTOMER, NATION n1, NATION n2, REGION where p_partkey = l_partkey and s_suppkey = l_suppkey and l_orderkey = o_orderkey and o_custkey = c_custkey and c_nationkey = n1.n_nationkey and n1.n_regionkey = r_regionkey and r_name = 'ASIA'	and s_nationkey = n2.n_nationkey and o_orderdate between date '1995-01-01' and date '1996-12-31'and p_type = 'SMALL PLATED COPPER') as all_nations group by o_year order by o_year;
    ''',
    "q9": '''
       select nation, o_year, sum(amount) as sum_profit from (select n_name as nation, extract(year from o_orderdate) as o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount from PART, SUPPLIER, LINEITEM, PARTSUPP, ORDERS, NATION where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey and p_partkey = l_partkey and o_orderkey = l_orderkey and s_nationkey = n_nationkey and p_name like '%dim%') as profit group by nation, o_year order by nation, o_year desc;
    ''',
    "q10": '''
        select c_custkey,
            c_name,
            sum(l_extendedprice * (1 - l_discount)) as revenue,
            c_acctbal,
            n_name,
            c_address,
            c_phone,
            c_comment
        from
            CUSTOMER,
            ORDERS,
            LINEITEM,
            NATION
        where
            c_custkey = o_custkey
            and l_orderkey = o_orderkey
            and o_orderdate >= date '1993-08-01'
            and o_orderdate < date '1993-08-01' + interval '3' month
            and l_returnflag = 'R'
            and c_nationkey = n_nationkey
        group by
            c_custkey,
            c_name,
            c_acctbal,
            c_phone,
            n_name,
            c_address,
            c_comment
        order by
            revenue desc
        limit 20;
    ''',
    "q11": '''
        select ps_partkey, sum(ps_supplycost * ps_availqty) as value from PARTSUPP, SUPPLIER, NATION where ps_suppkey = s_suppkey and s_nationkey = n_nationkey and n_name = 'MOZAMBIQUE' group by ps_partkey having sum(ps_supplycost * ps_availqty) > (select sum(ps_supplycost * ps_availqty) * 0.0001000000 from PARTSUPP, SUPPLIER, NATION where ps_suppkey = s_suppkey and s_nationkey = n_nationkey and n_name = 'MOZAMBIQUE') order by value desc;
    ''',
    "q12": '''
        select l_shipmode, sum(case when o_orderpriority = '1-URGENT' or o_orderpriority = '2-HIGH' then 1 else 0 end) as high_line_count, sum(case when o_orderpriority <> '1-URGENT' and o_orderpriority <> '2-HIGH' then 1 else 0 end) as low_line_count from ORDERS, LINEITEM where o_orderkey = l_orderkey and l_shipmode in ('RAIL', 'FOB') and l_commitdate < l_receiptdate and l_shipdate < l_commitdate and l_receiptdate >= date '1997-01-01' and l_receiptdate < date '1997-01-01' + interval '1' year group by l_shipmode order by l_shipmode;
    ''',
    "q13": '''
        select c_count, count(*) as custdist from (select c_custkey, count(o_orderkey) as c_count from CUSTOMER left outer join ORDERS on c_custkey = o_custkey and o_comment not like '%pending%deposits%' group by c_custkey) c_orders group by c_count order by custdist desc, c_count desc;
    ''',
    "q14": '''
        select 100.00 * sum(case when p_type like 'PROMO%' then l_extendedprice * (1 - l_discount) else 0 end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue from LINEITEM, PART where l_partkey = p_partkey and l_shipdate >= date '1996-12-01' and l_shipdate < date '1996-12-01' + interval '1' month;
    ''',
    "q15": '''
        create view REVENUE0 (supplier_no, total_revenue) as select l_suppkey, sum(l_extendedprice * (1 - l_discount)) from LINEITEM where l_shipdate >= date '1997-07-01' and l_shipdate < date '1997-07-01' + interval '3' month group by l_suppkey; select s_suppkey, s_name, s_address, s_phone, total_revenue from SUPPLIER, REVENUE0 where s_suppkey = supplier_no and total_revenue = ( select max(total_revenue) from REVENUE0) order by s_suppkey; drop view REVENUE0;
    ''',
    "q16": '''
        select p_brand, p_type, p_size, count(distinct ps_suppkey) as supplier_cnt from PARTSUPP, PART where p_partkey = ps_partkey and p_brand <> 'Brand#34' and p_type not like 'LARGE BRUSHED%' and p_size in (48, 19, 12, 4, 41, 7, 21, 39) and ps_suppkey not in (select s_suppkey from SUPPLIER where s_comment like '%Customer%Complaints%') group by p_brand, p_type, p_size order by supplier_cnt desc, p_brand, p_type, p_size;
    ''',
    "q17": '''
        select sum(l_extendedprice) / 7.0 as avg_yearly from LINEITEM, PART where p_partkey = l_partkey and p_brand = 'Brand#44' and p_container = 'WRAP PKG' and l_quantity < (select 0.2 * avg(l_quantity) from LINEITEM where l_partkey = p_partkey);
    ''',
    "q18": '''
        select c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice, sum(l_quantity) from CUSTOMER, ORDERS, LINEITEM where o_orderkey in (select l_orderkey from LINEITEM group by l_orderkey having sum(l_quantity) > 314) and c_custkey = o_custkey and o_orderkey = l_orderkey group by c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice order by o_totalprice desc, o_orderdate limit 100;
    ''',
    "q19": '''
        select sum(l_extendedprice* (1 - l_discount)) as revenue from LINEITEM, PART where (p_partkey = l_partkey and p_brand = 'Brand#52' and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG') and l_quantity >= 4 and l_quantity <= 4 + 10 and p_size between 1 and 5 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON') or (p_partkey = l_partkey and p_brand = 'Brand#11' and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK') and l_quantity >= 18 and l_quantity <= 18 + 10 and p_size between 1 and 10 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' ) or (p_partkey = l_partkey and p_brand = 'Brand#51' and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG') and l_quantity >= 29 and l_quantity <= 29 + 10 and p_size between 1 and 15 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON');
    ''',
    "q20": '''
        select s_name, s_address from SUPPLIER, NATION where s_suppkey in ( select ps_suppkey from PARTSUPP where ps_partkey in (select p_partkey from PART where p_name like 'green%') and ps_availqty > (select 0.5 * sum(l_quantity) from LINEITEM where l_partkey = ps_partkey and l_suppkey = ps_suppkey and l_shipdate >= date '1993-01-01' and l_shipdate < date '1993-01-01' + interval '1' year)) and s_nationkey = n_nationkey and n_name = 'ALGERIA' order by s_name;
    ''',
    "q21": '''
        select s_name, count(*) as numwait from SUPPLIER, LINEITEM l1, ORDERS, NATION where s_suppkey = l1.l_suppkey and o_orderkey = l1.l_orderkey and o_orderstatus = 'F' and l1.l_receiptdate > l1.l_commitdate and exists ( select * from LINEITEM l2 where l2.l_orderkey = l1.l_orderkey and l2.l_suppkey <> l1.l_suppkey) and not exists (select * from LINEITEM l3 where l3.l_orderkey = l1.l_orderkey and l3.l_suppkey <> l1.l_suppkey and l3.l_receiptdate > l3.l_commitdate) and s_nationkey = n_nationkey and n_name = 'EGYPT' group by s_name order by numwait desc, s_name limit 100;
    ''',
    "q22": '''
        select cntrycode, count(*) as numcust, sum(c_acctbal) as totacctbal from (select substring(c_phone from 1 for 2) as cntrycode, c_acctbal from CUSTOMER where substring(c_phone from 1 for 2) in ('20', '40', '22', '30', '39', '42', '21') and c_acctbal > ( select avg(c_acctbal) from CUSTOMER where c_acctbal > 0.00 and substring(c_phone from 1 for 2) in ('20', '40', '22', '30', '39', '42', '21')) and not exists ( select * from ORDERS where o_custkey = c_custkey)) as custsale group by cntrycode order by cntrycode;
    '''
}

cardinality_info = {
    "CUSTOMER": 150000,
    "ORDERS": 1500000,
    "LINEITEM": 6001215,
    "NATION": 25,
    "PARTSUPP": 800000,
    "PART": 200000,
    "REGION": 5,
    "SUPPLIER": 10000
}

# for imdb benchmark
#
# QUERIES = {
#     '01a': '''SELECT MIN(mc.note) AS production_note, MIN(t.title) AS movie_title, MIN(t.production_year) AS movie_year FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info_idx AS mi_idx, title AS t WHERE ct.kind = 'production companies' AND it.info = 'top 250 rank' AND mc.note  not like '%(as Metro-Goldwyn-Mayer Pictures)%' and (mc.note like '%(co-production)%' or mc.note like '%(presents)%') AND ct.id = mc.company_type_id AND t.id = mc.movie_id AND t.id = mi_idx.movie_id AND mc.movie_id = mi_idx.movie_id AND it.id = mi_idx.info_type_id;''',
#     '01b': '''SELECT MIN(mc.note) AS production_note, MIN(t.title) AS movie_title, MIN(t.production_year) AS movie_year FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info_idx AS mi_idx, title AS t WHERE ct.kind = 'production companies' AND it.info = 'bottom 10 rank' AND mc.note  not like '%(as Metro-Goldwyn-Mayer Pictures)%' AND t.production_year between 2005 and 2010 AND ct.id = mc.company_type_id AND t.id = mc.movie_id AND t.id = mi_idx.movie_id AND mc.movie_id = mi_idx.movie_id AND it.id = mi_idx.info_type_id;''',
#     '01c': '''SELECT MIN(mc.note) AS production_note, MIN(t.title) AS movie_title, MIN(t.production_year) AS movie_year FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info_idx AS mi_idx, title AS t WHERE ct.kind = 'production companies' AND it.info = 'top 250 rank' AND mc.note  not like '%(as Metro-Goldwyn-Mayer Pictures)%' and (mc.note like '%(co-production)%') AND t.production_year >2010 AND ct.id = mc.company_type_id AND t.id = mc.movie_id AND t.id = mi_idx.movie_id AND mc.movie_id = mi_idx.movie_id AND it.id = mi_idx.info_type_id;''',
#     '01d': '''SELECT MIN(mc.note) AS production_note, MIN(t.title) AS movie_title, MIN(t.production_year) AS movie_year FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info_idx AS mi_idx, title AS t WHERE ct.kind = 'production companies' AND it.info = 'bottom 10 rank' AND mc.note  not like '%(as Metro-Goldwyn-Mayer Pictures)%' AND t.production_year >2000 AND ct.id = mc.company_type_id AND t.id = mc.movie_id AND t.id = mi_idx.movie_id AND mc.movie_id = mi_idx.movie_id AND it.id = mi_idx.info_type_id;''',
#     '02a': '''SELECT MIN(t.title) AS movie_title FROM company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, title AS t WHERE cn.country_code ='[de]' AND k.keyword ='character-name-in-title' AND cn.id = mc.company_id AND mc.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND mc.movie_id = mk.movie_id;''',
#     '02b': '''SELECT MIN(t.title) AS movie_title FROM company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, title AS t WHERE cn.country_code ='[nl]' AND k.keyword ='character-name-in-title' AND cn.id = mc.company_id AND mc.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND mc.movie_id = mk.movie_id;''',
#     '02c': '''SELECT MIN(t.title) AS movie_title FROM company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, title AS t WHERE cn.country_code ='[sm]' AND k.keyword ='character-name-in-title' AND cn.id = mc.company_id AND mc.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND mc.movie_id = mk.movie_id;''',
#     '02d': '''SELECT MIN(t.title) AS movie_title FROM company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND cn.id = mc.company_id AND mc.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND mc.movie_id = mk.movie_id;''',
#     '03a': '''SELECT MIN(t.title) AS movie_title FROM keyword AS k, movie_info AS mi, movie_keyword AS mk, title AS t WHERE k.keyword  like '%sequel%' AND mi.info  IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German') AND t.production_year > 2005 AND t.id = mi.movie_id AND t.id = mk.movie_id AND mk.movie_id = mi.movie_id AND k.id = mk.keyword_id;''',
#     '03b': '''SELECT MIN(t.title) AS movie_title FROM keyword AS k, movie_info AS mi, movie_keyword AS mk, title AS t WHERE k.keyword  like '%sequel%' AND mi.info  IN ('Bulgaria') AND t.production_year > 2010 AND t.id = mi.movie_id AND t.id = mk.movie_id AND mk.movie_id = mi.movie_id AND k.id = mk.keyword_id;''',
#     '03c': '''SELECT MIN(t.title) AS movie_title FROM keyword AS k, movie_info AS mi, movie_keyword AS mk, title AS t WHERE k.keyword  like '%sequel%' AND mi.info  IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German', 'USA', 'American') AND t.production_year > 1990 AND t.id = mi.movie_id AND t.id = mk.movie_id AND mk.movie_id = mi.movie_id AND k.id = mk.keyword_id;''',
#     '04a': '''SELECT MIN(mi_idx.info) AS rating, MIN(t.title) AS movie_title FROM info_type AS it, keyword AS k, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE it.info ='rating' AND k.keyword  like '%sequel%' AND mi_idx.info  > '5.0' AND t.production_year > 2005 AND t.id = mi_idx.movie_id AND t.id = mk.movie_id AND mk.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it.id = mi_idx.info_type_id;''',
#     '04b': '''SELECT MIN(mi_idx.info) AS rating, MIN(t.title) AS movie_title FROM info_type AS it, keyword AS k, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE it.info ='rating' AND k.keyword  like '%sequel%' AND mi_idx.info  > '9.0' AND t.production_year > 2010 AND t.id = mi_idx.movie_id AND t.id = mk.movie_id AND mk.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it.id = mi_idx.info_type_id;''',
#     '04c': '''SELECT MIN(mi_idx.info) AS rating, MIN(t.title) AS movie_title FROM info_type AS it, keyword AS k, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE it.info ='rating' AND k.keyword  like '%sequel%' AND mi_idx.info  > '2.0' AND t.production_year > 1990 AND t.id = mi_idx.movie_id AND t.id = mk.movie_id AND mk.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it.id = mi_idx.info_type_id;''',
#     '05a': '''SELECT MIN(t.title) AS typical_european_movie FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info AS mi, title AS t WHERE ct.kind  = 'production companies' AND mc.note  like '%(theatrical)%' and mc.note like '%(France)%' AND mi.info  IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German') AND t.production_year > 2005 AND t.id = mi.movie_id AND t.id = mc.movie_id AND mc.movie_id = mi.movie_id AND ct.id = mc.company_type_id AND it.id = mi.info_type_id;''',
#     '05b': '''SELECT MIN(t.title) AS american_vhs_movie FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info AS mi, title AS t WHERE ct.kind  = 'production companies' AND mc.note  like '%(VHS)%' and mc.note like '%(USA)%' and mc.note like '%(1994)%' AND mi.info  IN ('USA', 'America') AND t.production_year > 2010 AND t.id = mi.movie_id AND t.id = mc.movie_id AND mc.movie_id = mi.movie_id AND ct.id = mc.company_type_id AND it.id = mi.info_type_id;''',
#     '05c': '''SELECT MIN(t.title) AS american_movie FROM company_type AS ct, info_type AS it, movie_companies AS mc, movie_info AS mi, title AS t WHERE ct.kind  = 'production companies' AND mc.note  not like '%(TV)%' and mc.note like '%(USA)%' AND mi.info  IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German', 'USA', 'American') AND t.production_year > 1990 AND t.id = mi.movie_id AND t.id = mc.movie_id AND mc.movie_id = mi.movie_id AND ct.id = mc.company_type_id AND it.id = mi.info_type_id;''',
#     '06a': '''SELECT MIN(k.keyword) AS movie_keyword, MIN(n.name) AS actor_name, MIN(t.title) AS marvel_movie FROM cast_info AS ci, keyword AS k, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword = 'marvel-cinematic-universe' AND n.name LIKE '%Downey%Robert%' AND t.production_year > 2010 AND k.id = mk.keyword_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND ci.movie_id = mk.movie_id AND n.id = ci.person_id;''',
#     '06b': '''SELECT MIN(k.keyword) AS movie_keyword, MIN(n.name) AS actor_name, MIN(t.title) AS hero_movie FROM cast_info AS ci, keyword AS k, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword in ('superhero', 'sequel', 'second-part', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence') AND n.name LIKE '%Downey%Robert%' AND t.production_year > 2014 AND k.id = mk.keyword_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND ci.movie_id = mk.movie_id AND n.id = ci.person_id;''',
#     '06c': '''SELECT MIN(k.keyword) AS movie_keyword, MIN(n.name) AS actor_name, MIN(t.title) AS marvel_movie FROM cast_info AS ci, keyword AS k, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword = 'marvel-cinematic-universe' AND n.name LIKE '%Downey%Robert%' AND t.production_year > 2014 AND k.id = mk.keyword_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND ci.movie_id = mk.movie_id AND n.id = ci.person_id;''',
#     '06d': '''SELECT MIN(k.keyword) AS movie_keyword, MIN(n.name) AS actor_name, MIN(t.title) AS hero_movie FROM cast_info AS ci, keyword AS k, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword in ('superhero', 'sequel', 'second-part', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence') AND n.name LIKE '%Downey%Robert%' AND t.production_year > 2000 AND k.id = mk.keyword_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND ci.movie_id = mk.movie_id AND n.id = ci.person_id;''',
#     '06e': '''SELECT MIN(k.keyword) AS movie_keyword, MIN(n.name) AS actor_name, MIN(t.title) AS marvel_movie FROM cast_info AS ci, keyword AS k, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword = 'marvel-cinematic-universe' AND n.name LIKE '%Downey%Robert%' AND t.production_year > 2000 AND k.id = mk.keyword_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND ci.movie_id = mk.movie_id AND n.id = ci.person_id;''',
#     '06f': '''SELECT MIN(k.keyword) AS movie_keyword, MIN(n.name) AS actor_name, MIN(t.title) AS hero_movie FROM cast_info AS ci, keyword AS k, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword in ('superhero', 'sequel', 'second-part', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence') AND t.production_year > 2000 AND k.id = mk.keyword_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND ci.movie_id = mk.movie_id AND n.id = ci.person_id;''',
#     '07a': '''SELECT MIN(n.name) AS of_person, MIN(t.title) AS biography_movie FROM aka_name AS an, cast_info AS ci, info_type AS it, link_type AS lt, movie_link AS ml, name AS n, person_info AS pi, title AS t WHERE an.name LIKE '%a%' AND it.info ='mini biography' AND lt.link ='features' AND n.name_pcode_cf BETWEEN 'A' AND 'F' AND (n.gender='m' OR (n.gender = 'f' AND n.name LIKE 'B%')) AND pi.note ='Volker Boehm' AND t.production_year BETWEEN 1980 AND 1995 AND n.id = an.person_id AND n.id = pi.person_id AND ci.person_id = n.id AND t.id = ci.movie_id AND ml.linked_movie_id = t.id AND lt.id = ml.link_type_id AND it.id = pi.info_type_id AND pi.person_id = an.person_id AND pi.person_id = ci.person_id AND an.person_id = ci.person_id AND ci.movie_id = ml.linked_movie_id;''',
#     '07b': '''SELECT MIN(n.name) AS of_person, MIN(t.title) AS biography_movie FROM aka_name AS an, cast_info AS ci, info_type AS it, link_type AS lt, movie_link AS ml, name AS n, person_info AS pi, title AS t WHERE an.name LIKE '%a%' AND it.info ='mini biography' AND lt.link ='features' AND n.name_pcode_cf LIKE 'D%' AND n.gender='m' AND pi.note ='Volker Boehm' AND t.production_year BETWEEN 1980 AND 1984 AND n.id = an.person_id AND n.id = pi.person_id AND ci.person_id = n.id AND t.id = ci.movie_id AND ml.linked_movie_id = t.id AND lt.id = ml.link_type_id AND it.id = pi.info_type_id AND pi.person_id = an.person_id AND pi.person_id = ci.person_id AND an.person_id = ci.person_id AND ci.movie_id = ml.linked_movie_id;''',
#     '07c': '''SELECT MIN(n.name) AS cast_member_name, MIN(pi.info) AS cast_member_info FROM aka_name AS an, cast_info AS ci, info_type AS it, link_type AS lt, movie_link AS ml, name AS n, person_info AS pi, title AS t WHERE an.name  is not NULL and (an.name LIKE '%a%' or an.name LIKE 'A%') AND it.info ='mini biography' AND lt.link  in ('references', 'referenced in', 'features', 'featured in') AND n.name_pcode_cf BETWEEN 'A' AND 'F' AND (n.gender='m' OR (n.gender = 'f' AND n.name LIKE 'A%')) AND pi.note  is not NULL AND t.production_year BETWEEN 1980 AND 2010 AND n.id = an.person_id AND n.id = pi.person_id AND ci.person_id = n.id AND t.id = ci.movie_id AND ml.linked_movie_id = t.id AND lt.id = ml.link_type_id AND it.id = pi.info_type_id AND pi.person_id = an.person_id AND pi.person_id = ci.person_id AND an.person_id = ci.person_id AND ci.movie_id = ml.linked_movie_id;''',
#     '08a': '''SELECT MIN(an1.name) AS actress_pseudonym, MIN(t.title) AS japanese_movie_dubbed FROM aka_name AS an1, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n1, role_type AS rt, title AS t WHERE ci.note ='(voice: English version)' AND cn.country_code ='[jp]' AND mc.note like '%(Japan)%' and mc.note not like '%(USA)%' AND n1.name like '%Yo%' and n1.name not like '%Yu%' AND rt.role ='actress' AND an1.person_id = n1.id AND n1.id = ci.person_id AND ci.movie_id = t.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND an1.person_id = ci.person_id AND ci.movie_id = mc.movie_id;''',
#     '08b': '''SELECT MIN(an.name) AS acress_pseudonym, MIN(t.title) AS japanese_anime_movie FROM aka_name AS an, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n, role_type AS rt, title AS t WHERE ci.note ='(voice: English version)' AND cn.country_code ='[jp]' AND mc.note like '%(Japan)%' and mc.note not like '%(USA)%' and (mc.note like '%(2006)%' or mc.note like '%(2007)%') AND n.name like '%Yo%' and n.name not like '%Yu%' AND rt.role ='actress' AND t.production_year between 2006 and 2007 and (t.title like 'One Piece%' or t.title like 'Dragon Ball Z%') AND an.person_id = n.id AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND an.person_id = ci.person_id AND ci.movie_id = mc.movie_id;''',
#     '08c': '''SELECT MIN(a1.name) AS writer_pseudo_name, MIN(t.title) AS movie_title FROM aka_name AS a1, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n1, role_type AS rt, title AS t WHERE cn.country_code ='[us]' AND rt.role ='writer' AND a1.person_id = n1.id AND n1.id = ci.person_id AND ci.movie_id = t.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND a1.person_id = ci.person_id AND ci.movie_id = mc.movie_id;''',
#     '08d': '''SELECT MIN(an1.name) AS costume_designer_pseudo, MIN(t.title) AS movie_with_costumes FROM aka_name AS an1, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n1, role_type AS rt, title AS t WHERE cn.country_code ='[us]' AND rt.role ='costume designer' AND an1.person_id = n1.id AND n1.id = ci.person_id AND ci.movie_id = t.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND an1.person_id = ci.person_id AND ci.movie_id = mc.movie_id;''',
#     '09a': '''SELECT MIN(an.name) AS alternative_name, MIN(chn.name) AS character_name, MIN(t.title) AS movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND mc.note  is not NULL and (mc.note like '%(USA)%' or mc.note like '%(worldwide)%') AND n.gender ='f' and n.name like '%Ang%' AND rt.role ='actress' AND t.production_year  between 2005 and 2015 AND ci.movie_id = t.id AND t.id = mc.movie_id AND ci.movie_id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND n.id = ci.person_id AND chn.id = ci.person_role_id AND an.person_id = n.id AND an.person_id = ci.person_id;''',
#     '09b': '''SELECT MIN(an.name) AS alternative_name, MIN(chn.name) AS voiced_character, MIN(n.name) AS voicing_actress, MIN(t.title) AS american_movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n, role_type AS rt, title AS t WHERE ci.note  = '(voice)' AND cn.country_code ='[us]' AND mc.note  like '%(200%)%' and (mc.note like '%(USA)%' or mc.note like '%(worldwide)%') AND n.gender ='f' and n.name like '%Angel%' AND rt.role ='actress' AND t.production_year  between 2007 and 2010 AND ci.movie_id = t.id AND t.id = mc.movie_id AND ci.movie_id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND n.id = ci.person_id AND chn.id = ci.person_role_id AND an.person_id = n.id AND an.person_id = ci.person_id;''',
#     '09c': '''SELECT MIN(an.name) AS alternative_name, MIN(chn.name) AS voiced_character_name, MIN(n.name) AS voicing_actress, MIN(t.title) AS american_movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND ci.movie_id = t.id AND t.id = mc.movie_id AND ci.movie_id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND n.id = ci.person_id AND chn.id = ci.person_role_id AND an.person_id = n.id AND an.person_id = ci.person_id;''',
#     '09d': '''SELECT MIN(an.name) AS alternative_name, MIN(chn.name) AS voiced_char_name, MIN(n.name) AS voicing_actress, MIN(t.title) AS american_movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, movie_companies AS mc, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND n.gender ='f' AND rt.role ='actress' AND ci.movie_id = t.id AND t.id = mc.movie_id AND ci.movie_id = mc.movie_id AND mc.company_id = cn.id AND ci.role_id = rt.id AND n.id = ci.person_id AND chn.id = ci.person_role_id AND an.person_id = n.id AND an.person_id = ci.person_id;''',
#     '10a': '''SELECT MIN(chn.name) AS uncredited_voiced_character, MIN(t.title) AS russian_movie FROM char_name AS chn, cast_info AS ci, company_name AS cn, company_type AS ct, movie_companies AS mc, role_type AS rt, title AS t WHERE ci.note  like '%(voice)%' and ci.note like '%(uncredited)%' AND cn.country_code  = '[ru]' AND rt.role  = 'actor' AND t.production_year > 2005 AND t.id = mc.movie_id AND t.id = ci.movie_id AND ci.movie_id = mc.movie_id AND chn.id = ci.person_role_id AND rt.id = ci.role_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '10b': '''SELECT MIN(chn.name) AS chr, MIN(t.title) AS russian_mov_with_actor_producer FROM char_name AS chn, cast_info AS ci, company_name AS cn, company_type AS ct, movie_companies AS mc, role_type AS rt, title AS t WHERE ci.note  like '%(producer)%' AND cn.country_code  = '[ru]' AND rt.role  = 'actor' AND t.production_year > 2010 AND t.id = mc.movie_id AND t.id = ci.movie_id AND ci.movie_id = mc.movie_id AND chn.id = ci.person_role_id AND rt.id = ci.role_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '10c': '''SELECT MIN(chn.name) AS chr, MIN(t.title) AS movie_with_american_producer FROM char_name AS chn, cast_info AS ci, company_name AS cn, company_type AS ct, movie_companies AS mc, role_type AS rt, title AS t WHERE ci.note  like '%(producer)%' AND cn.country_code  = '[us]' AND t.production_year > 1990 AND t.id = mc.movie_id AND t.id = ci.movie_id AND ci.movie_id = mc.movie_id AND chn.id = ci.person_role_id AND rt.id = ci.role_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '11a': '''SELECT MIN(cn.name) AS from_company, MIN(lt.link) AS movie_link_type, MIN(t.title) AS non_polish_sequel_movie FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND t.production_year BETWEEN 1950 AND 2000 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id;''',
#     '11b': '''SELECT MIN(cn.name) AS from_company, MIN(lt.link) AS movie_link_type, MIN(t.title) AS sequel_movie FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follows%' AND mc.note IS NULL AND t.production_year  = 1998 and t.title like '%Money%' AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id;''',
#     '11c': '''SELECT MIN(cn.name) AS from_company, MIN(mc.note) AS production_note, MIN(t.title) AS movie_based_on_book FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code  !='[pl]' and (cn.name like '20th Century Fox%' or cn.name like 'Twentieth Century Fox%') AND ct.kind  != 'production companies' and ct.kind is not NULL AND k.keyword  in ('sequel', 'revenge', 'based-on-novel') AND mc.note  is not NULL AND t.production_year  > 1950 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id;''',
#     '11d': '''SELECT MIN(cn.name) AS from_company, MIN(mc.note) AS production_note, MIN(t.title) AS movie_based_on_book FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code  !='[pl]' AND ct.kind  != 'production companies' and ct.kind is not NULL AND k.keyword  in ('sequel', 'revenge', 'based-on-novel') AND mc.note  is not NULL AND t.production_year  > 1950 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id;''',
#     '12a': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS drama_horror_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, title AS t WHERE cn.country_code  = '[us]' AND ct.kind  = 'production companies' AND it1.info = 'genres' AND it2.info = 'rating' AND mi.info  in ('Drama', 'Horror') AND mi_idx.info  > '8.0' AND t.production_year  between 2005 and 2008 AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND mi.info_type_id = it1.id AND mi_idx.info_type_id = it2.id AND t.id = mc.movie_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id;''',
#     '12b': '''SELECT MIN(mi.info) AS budget, MIN(t.title) AS unsuccsessful_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, title AS t WHERE cn.country_code ='[us]' AND ct.kind  is not NULL and (ct.kind ='production companies' or ct.kind = 'distributors') AND it1.info ='budget' AND it2.info ='bottom 10 rank' AND t.production_year >2000 AND (t.title LIKE 'Birdemic%' OR t.title LIKE '%Movie%') AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND mi.info_type_id = it1.id AND mi_idx.info_type_id = it2.id AND t.id = mc.movie_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id;''',
#     '12c': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS mainstream_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, title AS t WHERE cn.country_code  = '[us]' AND ct.kind  = 'production companies' AND it1.info = 'genres' AND it2.info = 'rating' AND mi.info  in ('Drama', 'Horror', 'Western', 'Family') AND mi_idx.info  > '7.0' AND t.production_year  between 2000 and 2010 AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND mi.info_type_id = it1.id AND mi_idx.info_type_id = it2.id AND t.id = mc.movie_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id;''',
#     '13a': '''SELECT MIN(mi.info) AS release_date, MIN(miidx.info) AS rating, MIN(t.title) AS german_movie FROM company_name AS cn, company_type AS ct, info_type AS it, info_type AS it2, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS miidx, title AS t WHERE cn.country_code ='[de]' AND ct.kind ='production companies' AND it.info ='rating' AND it2.info ='release dates' AND kt.kind ='movie' AND mi.movie_id = t.id AND it2.id = mi.info_type_id AND kt.id = t.kind_id AND mc.movie_id = t.id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND miidx.movie_id = t.id AND it.id = miidx.info_type_id AND mi.movie_id = miidx.movie_id AND mi.movie_id = mc.movie_id AND miidx.movie_id = mc.movie_id;''',
#     '13b': '''SELECT MIN(cn.name) AS producing_company, MIN(miidx.info) AS rating, MIN(t.title) AS movie_about_winning FROM company_name AS cn, company_type AS ct, info_type AS it, info_type AS it2, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS miidx, title AS t WHERE cn.country_code ='[us]' AND ct.kind ='production companies' AND it.info ='rating' AND it2.info ='release dates' AND kt.kind ='movie' AND t.title  != '' AND (t.title LIKE '%Champion%' OR t.title LIKE '%Loser%') AND mi.movie_id = t.id AND it2.id = mi.info_type_id AND kt.id = t.kind_id AND mc.movie_id = t.id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND miidx.movie_id = t.id AND it.id = miidx.info_type_id AND mi.movie_id = miidx.movie_id AND mi.movie_id = mc.movie_id AND miidx.movie_id = mc.movie_id;''',
#     '13c': '''SELECT MIN(cn.name) AS producing_company, MIN(miidx.info) AS rating, MIN(t.title) AS movie_about_winning FROM company_name AS cn, company_type AS ct, info_type AS it, info_type AS it2, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS miidx, title AS t WHERE cn.country_code ='[us]' AND ct.kind ='production companies' AND it.info ='rating' AND it2.info ='release dates' AND kt.kind ='movie' AND t.title  != '' AND (t.title LIKE 'Champion%' OR t.title LIKE 'Loser%') AND mi.movie_id = t.id AND it2.id = mi.info_type_id AND kt.id = t.kind_id AND mc.movie_id = t.id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND miidx.movie_id = t.id AND it.id = miidx.info_type_id AND mi.movie_id = miidx.movie_id AND mi.movie_id = mc.movie_id AND miidx.movie_id = mc.movie_id;''',
#     '13d': '''SELECT MIN(cn.name) AS producing_company, MIN(miidx.info) AS rating, MIN(t.title) AS movie FROM company_name AS cn, company_type AS ct, info_type AS it, info_type AS it2, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS miidx, title AS t WHERE cn.country_code ='[us]' AND ct.kind ='production companies' AND it.info ='rating' AND it2.info ='release dates' AND kt.kind ='movie' AND mi.movie_id = t.id AND it2.id = mi.info_type_id AND kt.id = t.kind_id AND mc.movie_id = t.id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND miidx.movie_id = t.id AND it.id = miidx.info_type_id AND mi.movie_id = miidx.movie_id AND mi.movie_id = mc.movie_id AND miidx.movie_id = mc.movie_id;''',
#     '14a': '''SELECT MIN(mi_idx.info) AS rating, MIN(t.title) AS northern_dark_movie FROM info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  = 'movie' AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  < '8.5' AND t.production_year  > 2010 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id;''',
#     '14b': '''SELECT MIN(mi_idx.info) AS rating, MIN(t.title) AS western_dark_production FROM info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title') AND kt.kind  = 'movie' AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  > '6.0' AND t.production_year  > 2010 and (t.title like '%murder%' or t.title like '%Murder%' or t.title like '%Mord%') AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id;''',
#     '14c': '''SELECT MIN(mi_idx.info) AS rating, MIN(t.title) AS north_european_dark_production FROM info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  is not null and k.keyword in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Danish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  < '8.5' AND t.production_year  > 2005 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id;''',
#     '15a': '''SELECT MIN(mi.info) AS release_date, MIN(t.title) AS internet_movie FROM aka_title AS at, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cn.country_code  = '[us]' AND it1.info  = 'release dates' AND mc.note  like '%(200%)%' and mc.note like '%(worldwide)%' AND mi.note  like '%internet%' AND mi.info  like 'USA:% 200%' AND t.production_year  > 2000 AND t.id = at.movie_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = at.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = at.movie_id AND mc.movie_id = at.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '15b': '''SELECT MIN(mi.info) AS release_date, MIN(t.title) AS youtube_movie FROM aka_title AS at, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cn.country_code  = '[us]' and cn.name = 'YouTube' AND it1.info  = 'release dates' AND mc.note  like '%(200%)%' and mc.note like '%(worldwide)%' AND mi.note  like '%internet%' AND mi.info  like 'USA:% 200%' AND t.production_year  between 2005 and 2010 AND t.id = at.movie_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = at.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = at.movie_id AND mc.movie_id = at.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '15c': '''SELECT MIN(mi.info) AS release_date, MIN(t.title) AS modern_american_internet_movie FROM aka_title AS at, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cn.country_code  = '[us]' AND it1.info  = 'release dates' AND mi.note  like '%internet%' AND mi.info  is not NULL and (mi.info like 'USA:% 199%' or mi.info like 'USA:% 200%') AND t.production_year  > 1990 AND t.id = at.movie_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = at.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = at.movie_id AND mc.movie_id = at.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '15d': '''SELECT MIN(at.title) AS aka_title, MIN(t.title) AS internet_movie_title FROM aka_title AS at, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cn.country_code  = '[us]' AND it1.info  = 'release dates' AND mi.note  like '%internet%' AND t.production_year  > 1990 AND t.id = at.movie_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = at.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = at.movie_id AND mc.movie_id = at.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id;''',
#     '16a': '''SELECT MIN(an.name) AS cool_actor_pseudonym, MIN(t.title) AS series_named_after_char FROM aka_name AS an, cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND t.episode_nr >= 50 AND t.episode_nr < 100 AND an.person_id = n.id AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND an.person_id = ci.person_id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '16b': '''SELECT MIN(an.name) AS cool_actor_pseudonym, MIN(t.title) AS series_named_after_char FROM aka_name AS an, cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND an.person_id = n.id AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND an.person_id = ci.person_id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '16c': '''SELECT MIN(an.name) AS cool_actor_pseudonym, MIN(t.title) AS series_named_after_char FROM aka_name AS an, cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND t.episode_nr < 100 AND an.person_id = n.id AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND an.person_id = ci.person_id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '16d': '''SELECT MIN(an.name) AS cool_actor_pseudonym, MIN(t.title) AS series_named_after_char FROM aka_name AS an, cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND t.episode_nr >= 5 AND t.episode_nr < 100 AND an.person_id = n.id AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND an.person_id = ci.person_id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '17a': '''SELECT MIN(n.name) AS member_in_charnamed_american_movie, MIN(n.name) AS a1 FROM cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND n.name  LIKE 'B%' AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '17b': '''SELECT MIN(n.name) AS member_in_charnamed_movie, MIN(n.name) AS a1 FROM cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword ='character-name-in-title' AND n.name  LIKE 'Z%' AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '17c': '''SELECT MIN(n.name) AS member_in_charnamed_movie, MIN(n.name) AS a1 FROM cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword ='character-name-in-title' AND n.name  LIKE 'X%' AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '17d': '''SELECT MIN(n.name) AS member_in_charnamed_movie FROM cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword ='character-name-in-title' AND n.name  LIKE '%Bert%' AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '17e': '''SELECT MIN(n.name) AS member_in_charnamed_movie FROM cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE cn.country_code ='[us]' AND k.keyword ='character-name-in-title' AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '17f': '''SELECT MIN(n.name) AS member_in_charnamed_movie FROM cast_info AS ci, company_name AS cn, keyword AS k, movie_companies AS mc, movie_keyword AS mk, name AS n, title AS t WHERE k.keyword ='character-name-in-title' AND n.name  LIKE '%B%' AND n.id = ci.person_id AND ci.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_id = cn.id AND ci.movie_id = mc.movie_id AND ci.movie_id = mk.movie_id AND mc.movie_id = mk.movie_id;''',
#     '18a': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(t.title) AS movie_title FROM cast_info AS ci, info_type AS it1, info_type AS it2, movie_info AS mi, movie_info_idx AS mi_idx, name AS n, title AS t WHERE ci.note  in ('(producer)', '(executive producer)') AND it1.info  = 'budget' AND it2.info  = 'votes' AND n.gender  = 'm' and n.name like '%Tim%' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id;''',
#     '18b': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(t.title) AS movie_title FROM cast_info AS ci, info_type AS it1, info_type AS it2, movie_info AS mi, movie_info_idx AS mi_idx, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'rating' AND mi.info  in ('Horror', 'Thriller') and mi.note is NULL AND mi_idx.info  > '8.0' AND n.gender  is not null and n.gender = 'f' AND t.production_year  between 2008 and 2014 AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id;''',
#     '18c': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(t.title) AS movie_title FROM cast_info AS ci, info_type AS it1, info_type AS it2, movie_info AS mi, movie_info_idx AS mi_idx, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND mi.info  in ('Horror', 'Action', 'Sci-Fi', 'Thriller', 'Crime', 'War') AND n.gender  = 'm' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND mi.movie_id = mi_idx.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id;''',
#     '19a': '''SELECT MIN(n.name) AS voicing_actress, MIN(t.title) AS voiced_movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, movie_companies AS mc, movie_info AS mi, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND mc.note  is not NULL and (mc.note like '%(USA)%' or mc.note like '%(worldwide)%') AND mi.info  is not null and (mi.info like 'Japan:%200%' or mi.info like 'USA:%200%') AND n.gender ='f' and n.name like '%Ang%' AND rt.role ='actress' AND t.production_year  between 2005 and 2009 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mi.movie_id = ci.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id;''',
#     '19b': '''SELECT MIN(n.name) AS voicing_actress, MIN(t.title) AS kung_fu_panda FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, movie_companies AS mc, movie_info AS mi, name AS n, role_type AS rt, title AS t WHERE ci.note  = '(voice)' AND cn.country_code ='[us]' AND it.info  = 'release dates' AND mc.note  like '%(200%)%' and (mc.note like '%(USA)%' or mc.note like '%(worldwide)%') AND mi.info  is not null and (mi.info like 'Japan:%2007%' or mi.info like 'USA:%2008%') AND n.gender ='f' and n.name like '%Angel%' AND rt.role ='actress' AND t.production_year  between 2007 and 2008 and t.title like '%Kung%Fu%Panda%' AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mi.movie_id = ci.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id;''',
#     '19c': '''SELECT MIN(n.name) AS voicing_actress, MIN(t.title) AS jap_engl_voiced_movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, movie_companies AS mc, movie_info AS mi, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND mi.info  is not null and (mi.info like 'Japan:%200%' or mi.info like 'USA:%200%') AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND t.production_year  > 2000 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mi.movie_id = ci.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id;''',
#     '19d': '''SELECT MIN(n.name) AS voicing_actress, MIN(t.title) AS jap_engl_voiced_movie FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, movie_companies AS mc, movie_info AS mi, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND n.gender ='f' AND rt.role ='actress' AND t.production_year  > 2000 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mi.movie_id = ci.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id;''',
#     '20a': '''SELECT MIN(t.title) AS complete_downey_ironman_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, keyword AS k, kind_type AS kt, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like '%complete%' AND chn.name  not like '%Sherlock%' and (chn.name like '%Tony%Stark%' or chn.name like '%Iron%Man%') AND k.keyword  in ('superhero', 'sequel', 'second-part', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence') AND kt.kind  = 'movie' AND t.production_year  > 1950 AND kt.id = t.kind_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND t.id = cc.movie_id AND mk.movie_id = ci.movie_id AND mk.movie_id = cc.movie_id AND ci.movie_id = cc.movie_id AND chn.id = ci.person_role_id AND n.id = ci.person_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '20b': '''SELECT MIN(t.title) AS complete_downey_ironman_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, keyword AS k, kind_type AS kt, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like '%complete%' AND chn.name  not like '%Sherlock%' and (chn.name like '%Tony%Stark%' or chn.name like '%Iron%Man%') AND k.keyword  in ('superhero', 'sequel', 'second-part', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence') AND kt.kind  = 'movie' AND n.name  LIKE '%Downey%Robert%' AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND t.id = cc.movie_id AND mk.movie_id = ci.movie_id AND mk.movie_id = cc.movie_id AND ci.movie_id = cc.movie_id AND chn.id = ci.person_role_id AND n.id = ci.person_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '20c': '''SELECT MIN(n.name) AS cast_member, MIN(t.title) AS complete_dynamic_hero_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, keyword AS k, kind_type AS kt, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like '%complete%' AND chn.name  is not NULL and (chn.name like '%man%' or chn.name like '%Man%') AND k.keyword  in ('superhero', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence', 'magnet', 'web', 'claw', 'laser') AND kt.kind  = 'movie' AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND t.id = cc.movie_id AND mk.movie_id = ci.movie_id AND mk.movie_id = cc.movie_id AND ci.movie_id = cc.movie_id AND chn.id = ci.person_role_id AND n.id = ci.person_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '21a': '''SELECT MIN(cn.name) AS company_name, MIN(lt.link) AS link_type, MIN(t.title) AS western_follow_up FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German') AND t.production_year BETWEEN 1950 AND 2000 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND mi.movie_id = t.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND ml.movie_id = mi.movie_id AND mk.movie_id = mi.movie_id AND mc.movie_id = mi.movie_id;''',
#     '21b': '''SELECT MIN(cn.name) AS company_name, MIN(lt.link) AS link_type, MIN(t.title) AS german_follow_up FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND mi.info IN ('Germany', 'German') AND t.production_year BETWEEN 2000 AND 2010 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND mi.movie_id = t.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND ml.movie_id = mi.movie_id AND mk.movie_id = mi.movie_id AND mc.movie_id = mi.movie_id;''',
#     '21c': '''SELECT MIN(cn.name) AS company_name, MIN(lt.link) AS link_type, MIN(t.title) AS western_follow_up FROM company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German', 'English') AND t.production_year BETWEEN 1950 AND 2010 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND mi.movie_id = t.id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND ml.movie_id = mi.movie_id AND mk.movie_id = mi.movie_id AND mc.movie_id = mi.movie_id;''',
#     '22a': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS western_violent_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mc.note  not like '%(USA)%' and mc.note like '%(200%)%' AND mi.info IN ('Germany', 'German', 'USA', 'American') AND mi_idx.info  < '7.0' AND t.production_year  > 2008 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mc.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id;''',
#     '22b': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS western_violent_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mc.note  not like '%(USA)%' and mc.note like '%(200%)%' AND mi.info IN ('Germany', 'German', 'USA', 'American') AND mi_idx.info  < '7.0' AND t.production_year  > 2009 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mc.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id;''',
#     '22c': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS western_violent_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mc.note  not like '%(USA)%' and mc.note like '%(200%)%' AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Danish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  < '8.5' AND t.production_year  > 2005 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mc.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id;''',
#     '22d': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS western_violent_movie FROM company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Danish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  < '8.5' AND t.production_year  > 2005 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mc.movie_id = mi_idx.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id;''',
#     '23a': '''SELECT MIN(kt.kind) AS movie_kind, MIN(t.title) AS complete_us_internet_movie FROM complete_cast AS cc, comp_cast_type AS cct1, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cct1.kind  = 'complete+verified' AND cn.country_code  = '[us]' AND it1.info  = 'release dates' AND kt.kind  in ('movie') AND mi.note  like '%internet%' AND mi.info  is not NULL and (mi.info like 'USA:% 199%' or mi.info like 'USA:% 200%') AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND t.id = cc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = cc.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = cc.movie_id AND mc.movie_id = cc.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND cct1.id = cc.status_id;''',
#     '23b': '''SELECT MIN(kt.kind) AS movie_kind, MIN(t.title) AS complete_nerdy_internet_movie FROM complete_cast AS cc, comp_cast_type AS cct1, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cct1.kind  = 'complete+verified' AND cn.country_code  = '[us]' AND it1.info  = 'release dates' AND k.keyword  in ('nerd', 'loner', 'alienation', 'dignity') AND kt.kind  in ('movie') AND mi.note  like '%internet%' AND mi.info  like 'USA:% 200%' AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND t.id = cc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = cc.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = cc.movie_id AND mc.movie_id = cc.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND cct1.id = cc.status_id;''',
#     '23c': '''SELECT MIN(kt.kind) AS movie_kind, MIN(t.title) AS complete_us_internet_movie FROM complete_cast AS cc, comp_cast_type AS cct1, company_name AS cn, company_type AS ct, info_type AS it1, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, title AS t WHERE cct1.kind  = 'complete+verified' AND cn.country_code  = '[us]' AND it1.info  = 'release dates' AND kt.kind  in ('movie', 'tv movie', 'video movie', 'video game') AND mi.note  like '%internet%' AND mi.info  is not NULL and (mi.info like 'USA:% 199%' or mi.info like 'USA:% 200%') AND t.production_year  > 1990 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND t.id = cc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = cc.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = cc.movie_id AND mc.movie_id = cc.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND cn.id = mc.company_id AND ct.id = mc.company_type_id AND cct1.id = cc.status_id;''',
#     '24a': '''SELECT MIN(chn.name) AS voiced_char_name, MIN(n.name) AS voicing_actress_name, MIN(t.title) AS voiced_action_movie_jap_eng FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND k.keyword  in ('hero', 'martial-arts', 'hand-to-hand-combat') AND mi.info  is not null and (mi.info like 'Japan:%201%' or mi.info like 'USA:%201%') AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND t.production_year  > 2010 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mk.movie_id AND mi.movie_id = ci.movie_id AND mi.movie_id = mk.movie_id AND ci.movie_id = mk.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id AND k.id = mk.keyword_id;''',
#     '24b': '''SELECT MIN(chn.name) AS voiced_char_name, MIN(n.name) AS voicing_actress_name, MIN(t.title) AS kung_fu_panda FROM aka_name AS an, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, name AS n, role_type AS rt, title AS t WHERE ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND cn.name  = 'DreamWorks Animation' AND it.info  = 'release dates' AND k.keyword  in ('hero', 'martial-arts', 'hand-to-hand-combat', 'computer-animated-movie') AND mi.info  is not null and (mi.info like 'Japan:%201%' or mi.info like 'USA:%201%') AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND t.production_year  > 2010 AND t.title like 'Kung Fu Panda%' AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mk.movie_id AND mi.movie_id = ci.movie_id AND mi.movie_id = mk.movie_id AND ci.movie_id = mk.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id AND k.id = mk.keyword_id;''',
#     '25a': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS male_writer, MIN(t.title) AS violent_movie_title FROM cast_info AS ci, info_type AS it1, info_type AS it2, keyword AS k, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'blood', 'gore', 'death', 'female-nudity') AND mi.info  = 'Horror' AND n.gender  = 'm' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi_idx.movie_id = mk.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id;''',
#     '25b': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS male_writer, MIN(t.title) AS violent_movie_title FROM cast_info AS ci, info_type AS it1, info_type AS it2, keyword AS k, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'blood', 'gore', 'death', 'female-nudity') AND mi.info  = 'Horror' AND n.gender   = 'm' AND t.production_year  > 2010 AND t.title  like 'Vampire%' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi_idx.movie_id = mk.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id;''',
#     '25c': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS male_writer, MIN(t.title) AS violent_movie_title FROM cast_info AS ci, info_type AS it1, info_type AS it2, keyword AS k, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mi.info  in ('Horror', 'Action', 'Sci-Fi', 'Thriller', 'Crime', 'War') AND n.gender   = 'm' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi_idx.movie_id = mk.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id;''',
#     '26a': '''SELECT MIN(chn.name) AS character_name, MIN(mi_idx.info) AS rating, MIN(n.name) AS playing_actor, MIN(t.title) AS complete_hero_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, info_type AS it2, keyword AS k, kind_type AS kt, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like '%complete%' AND chn.name  is not NULL and (chn.name like '%man%' or chn.name like '%Man%') AND it2.info  = 'rating' AND k.keyword  in ('superhero', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence', 'magnet', 'web', 'claw', 'laser') AND kt.kind  = 'movie' AND mi_idx.info  > '7.0' AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND t.id = cc.movie_id AND t.id = mi_idx.movie_id AND mk.movie_id = ci.movie_id AND mk.movie_id = cc.movie_id AND mk.movie_id = mi_idx.movie_id AND ci.movie_id = cc.movie_id AND ci.movie_id = mi_idx.movie_id AND cc.movie_id = mi_idx.movie_id AND chn.id = ci.person_role_id AND n.id = ci.person_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id AND it2.id = mi_idx.info_type_id;''',
#     '26b': '''SELECT MIN(chn.name) AS character_name, MIN(mi_idx.info) AS rating, MIN(t.title) AS complete_hero_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, info_type AS it2, keyword AS k, kind_type AS kt, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like '%complete%' AND chn.name  is not NULL and (chn.name like '%man%' or chn.name like '%Man%') AND it2.info  = 'rating' AND k.keyword  in ('superhero', 'marvel-comics', 'based-on-comic', 'fight') AND kt.kind  = 'movie' AND mi_idx.info  > '8.0' AND t.production_year  > 2005 AND kt.id = t.kind_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND t.id = cc.movie_id AND t.id = mi_idx.movie_id AND mk.movie_id = ci.movie_id AND mk.movie_id = cc.movie_id AND mk.movie_id = mi_idx.movie_id AND ci.movie_id = cc.movie_id AND ci.movie_id = mi_idx.movie_id AND cc.movie_id = mi_idx.movie_id AND chn.id = ci.person_role_id AND n.id = ci.person_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id AND it2.id = mi_idx.info_type_id;''',
#     '26c': '''SELECT MIN(chn.name) AS character_name, MIN(mi_idx.info) AS rating, MIN(t.title) AS complete_hero_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, info_type AS it2, keyword AS k, kind_type AS kt, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like '%complete%' AND chn.name  is not NULL and (chn.name like '%man%' or chn.name like '%Man%') AND it2.info  = 'rating' AND k.keyword  in ('superhero', 'marvel-comics', 'based-on-comic', 'tv-special', 'fight', 'violence', 'magnet', 'web', 'claw', 'laser') AND kt.kind  = 'movie' AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mk.movie_id AND t.id = ci.movie_id AND t.id = cc.movie_id AND t.id = mi_idx.movie_id AND mk.movie_id = ci.movie_id AND mk.movie_id = cc.movie_id AND mk.movie_id = mi_idx.movie_id AND ci.movie_id = cc.movie_id AND ci.movie_id = mi_idx.movie_id AND cc.movie_id = mi_idx.movie_id AND chn.id = ci.person_role_id AND n.id = ci.person_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id AND it2.id = mi_idx.info_type_id;''',
#     '27a': '''SELECT MIN(cn.name) AS producing_company, MIN(lt.link) AS link_type, MIN(t.title) AS complete_western_sequel FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cct1.kind  in ('cast', 'crew') AND cct2.kind  = 'complete' AND cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND mi.info IN ('Sweden', 'Germany','Swedish', 'German') AND t.production_year BETWEEN 1950 AND 2000 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND mi.movie_id = t.id AND t.id = cc.movie_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND ml.movie_id = mi.movie_id AND mk.movie_id = mi.movie_id AND mc.movie_id = mi.movie_id AND ml.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND mc.movie_id = cc.movie_id AND mi.movie_id = cc.movie_id;''',
#     '27b': '''SELECT MIN(cn.name) AS producing_company, MIN(lt.link) AS link_type, MIN(t.title) AS complete_western_sequel FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cct1.kind  in ('cast', 'crew') AND cct2.kind  = 'complete' AND cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND mi.info IN ('Sweden', 'Germany','Swedish', 'German') AND t.production_year  = 1998 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND mi.movie_id = t.id AND t.id = cc.movie_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND ml.movie_id = mi.movie_id AND mk.movie_id = mi.movie_id AND mc.movie_id = mi.movie_id AND ml.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND mc.movie_id = cc.movie_id AND mi.movie_id = cc.movie_id;''',
#     '27c': '''SELECT MIN(cn.name) AS producing_company, MIN(lt.link) AS link_type, MIN(t.title) AS complete_western_sequel FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, company_name AS cn, company_type AS ct, keyword AS k, link_type AS lt, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, movie_link AS ml, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  like 'complete%' AND cn.country_code !='[pl]' AND (cn.name LIKE '%Film%' OR cn.name LIKE '%Warner%') AND ct.kind ='production companies' AND k.keyword ='sequel' AND lt.link LIKE '%follow%' AND mc.note IS NULL AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Denish', 'Norwegian', 'German', 'English') AND t.production_year BETWEEN 1950 AND 2010 AND lt.id = ml.link_type_id AND ml.movie_id = t.id AND t.id = mk.movie_id AND mk.keyword_id = k.id AND t.id = mc.movie_id AND mc.company_type_id = ct.id AND mc.company_id = cn.id AND mi.movie_id = t.id AND t.id = cc.movie_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id AND ml.movie_id = mk.movie_id AND ml.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND ml.movie_id = mi.movie_id AND mk.movie_id = mi.movie_id AND mc.movie_id = mi.movie_id AND ml.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND mc.movie_id = cc.movie_id AND mi.movie_id = cc.movie_id;''',
#     '28a': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS complete_euro_dark_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cct1.kind  = 'crew' AND cct2.kind  != 'complete+verified' AND cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mc.note  not like '%(USA)%' and mc.note like '%(200%)%' AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Danish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  < '8.5' AND t.production_year  > 2000 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND t.id = cc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = cc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = cc.movie_id AND mc.movie_id = mi_idx.movie_id AND mc.movie_id = cc.movie_id AND mi_idx.movie_id = cc.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '28b': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS complete_euro_dark_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cct1.kind  = 'crew' AND cct2.kind  != 'complete+verified' AND cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mc.note  not like '%(USA)%' and mc.note like '%(200%)%' AND mi.info  IN ('Sweden', 'Germany', 'Swedish', 'German') AND mi_idx.info  > '6.5' AND t.production_year  > 2005 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND t.id = cc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = cc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = cc.movie_id AND mc.movie_id = mi_idx.movie_id AND mc.movie_id = cc.movie_id AND mi_idx.movie_id = cc.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '28c': '''SELECT MIN(cn.name) AS movie_company, MIN(mi_idx.info) AS rating, MIN(t.title) AS complete_euro_dark_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, company_name AS cn, company_type AS ct, info_type AS it1, info_type AS it2, keyword AS k, kind_type AS kt, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  = 'complete' AND cn.country_code  != '[us]' AND it1.info  = 'countries' AND it2.info  = 'rating' AND k.keyword  in ('murder', 'murder-in-title', 'blood', 'violence') AND kt.kind  in ('movie', 'episode') AND mc.note  not like '%(USA)%' and mc.note like '%(200%)%' AND mi.info IN ('Sweden', 'Norway', 'Germany', 'Denmark', 'Swedish', 'Danish', 'Norwegian', 'German', 'USA', 'American') AND mi_idx.info  < '8.5' AND t.production_year  > 2005 AND kt.id = t.kind_id AND t.id = mi.movie_id AND t.id = mk.movie_id AND t.id = mi_idx.movie_id AND t.id = mc.movie_id AND t.id = cc.movie_id AND mk.movie_id = mi.movie_id AND mk.movie_id = mi_idx.movie_id AND mk.movie_id = mc.movie_id AND mk.movie_id = cc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mc.movie_id AND mi.movie_id = cc.movie_id AND mc.movie_id = mi_idx.movie_id AND mc.movie_id = cc.movie_id AND mi_idx.movie_id = cc.movie_id AND k.id = mk.keyword_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND ct.id = mc.company_type_id AND cn.id = mc.company_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '29a': '''SELECT MIN(chn.name) AS voiced_char, MIN(n.name) AS voicing_actress, MIN(t.title) AS voiced_animation FROM aka_name AS an, complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, info_type AS it3, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, name AS n, person_info AS pi, role_type AS rt, title AS t WHERE cct1.kind  ='cast' AND cct2.kind  ='complete+verified' AND chn.name  = 'Queen' AND ci.note  in ('(voice)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND it3.info  = 'trivia' AND k.keyword  = 'computer-animation' AND mi.info  is not null and (mi.info like 'Japan:%200%' or mi.info like 'USA:%200%') AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND t.title  = 'Shrek 2' AND t.production_year  between 2000 and 2010 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = cc.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mk.movie_id AND mc.movie_id = cc.movie_id AND mi.movie_id = ci.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = cc.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id AND n.id = pi.person_id AND ci.person_id = pi.person_id AND it3.id = pi.info_type_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '29b': '''SELECT MIN(chn.name) AS voiced_char, MIN(n.name) AS voicing_actress, MIN(t.title) AS voiced_animation FROM aka_name AS an, complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, info_type AS it3, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, name AS n, person_info AS pi, role_type AS rt, title AS t WHERE cct1.kind  ='cast' AND cct2.kind  ='complete+verified' AND chn.name  = 'Queen' AND ci.note  in ('(voice)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND it3.info  = 'height' AND k.keyword  = 'computer-animation' AND mi.info  like 'USA:%200%' AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND t.title  = 'Shrek 2' AND t.production_year  between 2000 and 2005 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = cc.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mk.movie_id AND mc.movie_id = cc.movie_id AND mi.movie_id = ci.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = cc.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id AND n.id = pi.person_id AND ci.person_id = pi.person_id AND it3.id = pi.info_type_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '29c': '''SELECT MIN(chn.name) AS voiced_char, MIN(n.name) AS voicing_actress, MIN(t.title) AS voiced_animation FROM aka_name AS an, complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, char_name AS chn, cast_info AS ci, company_name AS cn, info_type AS it, info_type AS it3, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_keyword AS mk, name AS n, person_info AS pi, role_type AS rt, title AS t WHERE cct1.kind  ='cast' AND cct2.kind  ='complete+verified' AND ci.note  in ('(voice)', '(voice: Japanese version)', '(voice) (uncredited)', '(voice: English version)') AND cn.country_code ='[us]' AND it.info  = 'release dates' AND it3.info  = 'trivia' AND k.keyword  = 'computer-animation' AND mi.info  is not null and (mi.info like 'Japan:%200%' or mi.info like 'USA:%200%') AND n.gender ='f' and n.name like '%An%' AND rt.role ='actress' AND t.production_year  between 2000 and 2010 AND t.id = mi.movie_id AND t.id = mc.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = cc.movie_id AND mc.movie_id = ci.movie_id AND mc.movie_id = mi.movie_id AND mc.movie_id = mk.movie_id AND mc.movie_id = cc.movie_id AND mi.movie_id = ci.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = cc.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND cn.id = mc.company_id AND it.id = mi.info_type_id AND n.id = ci.person_id AND rt.id = ci.role_id AND n.id = an.person_id AND ci.person_id = an.person_id AND chn.id = ci.person_role_id AND n.id = pi.person_id AND ci.person_id = pi.person_id AND it3.id = pi.info_type_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '30a': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS writer, MIN(t.title) AS complete_violent_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, cast_info AS ci, info_type AS it1, info_type AS it2, keyword AS k, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  in ('cast', 'crew') AND cct2.kind  ='complete+verified' AND ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mi.info  in ('Horror', 'Thriller') AND n.gender  = 'm' AND t.production_year  > 2000 AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = cc.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = cc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = cc.movie_id AND mi_idx.movie_id = mk.movie_id AND mi_idx.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '30b': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS writer, MIN(t.title) AS complete_gore_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, cast_info AS ci, info_type AS it1, info_type AS it2, keyword AS k, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  in ('cast', 'crew') AND cct2.kind  ='complete+verified' AND ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mi.info  in ('Horror', 'Thriller') AND n.gender  = 'm' AND t.production_year  > 2000 and (t.title like '%Freddy%' or t.title like '%Jason%' or t.title like 'Saw%') AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = cc.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = cc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = cc.movie_id AND mi_idx.movie_id = mk.movie_id AND mi_idx.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '30c': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS writer, MIN(t.title) AS complete_violent_movie FROM complete_cast AS cc, comp_cast_type AS cct1, comp_cast_type AS cct2, cast_info AS ci, info_type AS it1, info_type AS it2, keyword AS k, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE cct1.kind  = 'cast' AND cct2.kind  ='complete+verified' AND ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mi.info  in ('Horror', 'Action', 'Sci-Fi', 'Thriller', 'Crime', 'War') AND n.gender  = 'm' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = cc.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = cc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = cc.movie_id AND mi_idx.movie_id = mk.movie_id AND mi_idx.movie_id = cc.movie_id AND mk.movie_id = cc.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id AND cct1.id = cc.subject_id AND cct2.id = cc.status_id;''',
#     '31a': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS writer, MIN(t.title) AS violent_liongate_movie FROM cast_info AS ci, company_name AS cn, info_type AS it1, info_type AS it2, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND cn.name  like 'Lionsgate%' AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mi.info  in ('Horror', 'Thriller') AND n.gender   = 'm' AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = mc.movie_id AND mi_idx.movie_id = mk.movie_id AND mi_idx.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id AND cn.id = mc.company_id;''',
#     '31b': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS writer, MIN(t.title) AS violent_liongate_movie FROM cast_info AS ci, company_name AS cn, info_type AS it1, info_type AS it2, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND cn.name  like 'Lionsgate%' AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mc.note  like '%(Blu-ray)%' AND mi.info  in ('Horror', 'Thriller') AND n.gender  = 'm' AND t.production_year  > 2000 and (t.title like '%Freddy%' or t.title like '%Jason%' or t.title like 'Saw%') AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = mc.movie_id AND mi_idx.movie_id = mk.movie_id AND mi_idx.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id AND cn.id = mc.company_id;''',
#     '31c': '''SELECT MIN(mi.info) AS movie_budget, MIN(mi_idx.info) AS movie_votes, MIN(n.name) AS writer, MIN(t.title) AS violent_liongate_movie FROM cast_info AS ci, company_name AS cn, info_type AS it1, info_type AS it2, keyword AS k, movie_companies AS mc, movie_info AS mi, movie_info_idx AS mi_idx, movie_keyword AS mk, name AS n, title AS t WHERE ci.note  in ('(writer)', '(head writer)', '(written by)', '(story)', '(story editor)') AND cn.name  like 'Lionsgate%' AND it1.info  = 'genres' AND it2.info  = 'votes' AND k.keyword  in ('murder', 'violence', 'blood', 'gore', 'death', 'female-nudity', 'hospital') AND mi.info  in ('Horror', 'Action', 'Sci-Fi', 'Thriller', 'Crime', 'War') AND t.id = mi.movie_id AND t.id = mi_idx.movie_id AND t.id = ci.movie_id AND t.id = mk.movie_id AND t.id = mc.movie_id AND ci.movie_id = mi.movie_id AND ci.movie_id = mi_idx.movie_id AND ci.movie_id = mk.movie_id AND ci.movie_id = mc.movie_id AND mi.movie_id = mi_idx.movie_id AND mi.movie_id = mk.movie_id AND mi.movie_id = mc.movie_id AND mi_idx.movie_id = mk.movie_id AND mi_idx.movie_id = mc.movie_id AND mk.movie_id = mc.movie_id AND n.id = ci.person_id AND it1.id = mi.info_type_id AND it2.id = mi_idx.info_type_id AND k.id = mk.keyword_id AND cn.id = mc.company_id;''',
#     '32a': '''SELECT MIN(lt.link) AS link_type, MIN(t1.title) AS first_movie, MIN(t2.title) AS second_movie FROM keyword AS k, link_type AS lt, movie_keyword AS mk, movie_link AS ml, title AS t1, title AS t2 WHERE k.keyword ='10,000-mile-club' AND mk.keyword_id = k.id AND t1.id = mk.movie_id AND ml.movie_id = t1.id AND ml.linked_movie_id = t2.id AND lt.id = ml.link_type_id AND mk.movie_id = t1.id;''',
#     '32b': '''SELECT MIN(lt.link) AS link_type, MIN(t1.title) AS first_movie, MIN(t2.title) AS second_movie FROM keyword AS k, link_type AS lt, movie_keyword AS mk, movie_link AS ml, title AS t1, title AS t2 WHERE k.keyword ='character-name-in-title' AND mk.keyword_id = k.id AND t1.id = mk.movie_id AND ml.movie_id = t1.id AND ml.linked_movie_id = t2.id AND lt.id = ml.link_type_id AND mk.movie_id = t1.id;''',
#     '33a': '''SELECT MIN(cn1.name) AS first_company, MIN(cn2.name) AS second_company, MIN(mi_idx1.info) AS first_rating, MIN(mi_idx2.info) AS second_rating, MIN(t1.title) AS first_movie, MIN(t2.title) AS second_movie FROM company_name AS cn1, company_name AS cn2, info_type AS it1, info_type AS it2, kind_type AS kt1, kind_type AS kt2, link_type AS lt, movie_companies AS mc1, movie_companies AS mc2, movie_info_idx AS mi_idx1, movie_info_idx AS mi_idx2, movie_link AS ml, title AS t1, title AS t2 WHERE cn1.country_code  = '[us]' AND it1.info  = 'rating' AND it2.info  = 'rating' AND kt1.kind  in ('tv series') AND kt2.kind  in ('tv series') AND lt.link  in ('sequel', 'follows', 'followed by') AND mi_idx2.info  < '3.0' AND t2.production_year  between 2005 and 2008 AND lt.id = ml.link_type_id AND t1.id = ml.movie_id AND t2.id = ml.linked_movie_id AND it1.id = mi_idx1.info_type_id AND t1.id = mi_idx1.movie_id AND kt1.id = t1.kind_id AND cn1.id = mc1.company_id AND t1.id = mc1.movie_id AND ml.movie_id = mi_idx1.movie_id AND ml.movie_id = mc1.movie_id AND mi_idx1.movie_id = mc1.movie_id AND it2.id = mi_idx2.info_type_id AND t2.id = mi_idx2.movie_id AND kt2.id = t2.kind_id AND cn2.id = mc2.company_id AND t2.id = mc2.movie_id AND ml.linked_movie_id = mi_idx2.movie_id AND ml.linked_movie_id = mc2.movie_id AND mi_idx2.movie_id = mc2.movie_id;''',
#     '33b': '''SELECT MIN(cn1.name) AS first_company, MIN(cn2.name) AS second_company, MIN(mi_idx1.info) AS first_rating, MIN(mi_idx2.info) AS second_rating, MIN(t1.title) AS first_movie, MIN(t2.title) AS second_movie FROM company_name AS cn1, company_name AS cn2, info_type AS it1, info_type AS it2, kind_type AS kt1, kind_type AS kt2, link_type AS lt, movie_companies AS mc1, movie_companies AS mc2, movie_info_idx AS mi_idx1, movie_info_idx AS mi_idx2, movie_link AS ml, title AS t1, title AS t2 WHERE cn1.country_code  = '[nl]' AND it1.info  = 'rating' AND it2.info  = 'rating' AND kt1.kind  in ('tv series') AND kt2.kind  in ('tv series') AND lt.link  LIKE '%follow%' AND mi_idx2.info  < '3.0' AND t2.production_year  = 2007 AND lt.id = ml.link_type_id AND t1.id = ml.movie_id AND t2.id = ml.linked_movie_id AND it1.id = mi_idx1.info_type_id AND t1.id = mi_idx1.movie_id AND kt1.id = t1.kind_id AND cn1.id = mc1.company_id AND t1.id = mc1.movie_id AND ml.movie_id = mi_idx1.movie_id AND ml.movie_id = mc1.movie_id AND mi_idx1.movie_id = mc1.movie_id AND it2.id = mi_idx2.info_type_id AND t2.id = mi_idx2.movie_id AND kt2.id = t2.kind_id AND cn2.id = mc2.company_id AND t2.id = mc2.movie_id AND ml.linked_movie_id = mi_idx2.movie_id AND ml.linked_movie_id = mc2.movie_id AND mi_idx2.movie_id = mc2.movie_id;''',
#     '33c': '''SELECT MIN(cn1.name) AS first_company, MIN(cn2.name) AS second_company, MIN(mi_idx1.info) AS first_rating, MIN(mi_idx2.info) AS second_rating, MIN(t1.title) AS first_movie, MIN(t2.title) AS second_movie FROM company_name AS cn1, company_name AS cn2, info_type AS it1, info_type AS it2, kind_type AS kt1, kind_type AS kt2, link_type AS lt, movie_companies AS mc1, movie_companies AS mc2, movie_info_idx AS mi_idx1, movie_info_idx AS mi_idx2, movie_link AS ml, title AS t1, title AS t2 WHERE cn1.country_code  != '[us]' AND it1.info  = 'rating' AND it2.info  = 'rating' AND kt1.kind  in ('tv series', 'episode') AND kt2.kind  in ('tv series', 'episode') AND lt.link  in ('sequel', 'follows', 'followed by') AND mi_idx2.info  < '3.5' AND t2.production_year  between 2000 and 2010 AND lt.id = ml.link_type_id AND t1.id = ml.movie_id AND t2.id = ml.linked_movie_id AND it1.id = mi_idx1.info_type_id AND t1.id = mi_idx1.movie_id AND kt1.id = t1.kind_id AND cn1.id = mc1.company_id AND t1.id = mc1.movie_id AND ml.movie_id = mi_idx1.movie_id AND ml.movie_id = mc1.movie_id AND mi_idx1.movie_id = mc1.movie_id AND it2.id = mi_idx2.info_type_id AND t2.id = mi_idx2.movie_id AND kt2.id = t2.kind_id AND cn2.id = mc2.company_id AND t2.id = mc2.movie_id AND ml.linked_movie_id = mi_idx2.movie_id AND ml.linked_movie_id = mc2.movie_id AND mi_idx2.movie_id = mc2.movie_id;'''
# }

# cardinality_info = {
#     "aka_name": 901343,
#     "aka_title": 361472,
#     "cast_info": 36244344,
#     "char_name": 3140339,
#     "comp_cast_type": 4,
#     "company_name": 234997,
#     "company_type": 4,
#     "complete_cast": 135086,
#     "info_type": 113,
#     "keyword": 134170,
#     "kind_type": 7,
#     "link_type": 18,
#     "movie_companies": 2609129,
#     "movie_info": 14835720,
#     "movie_info_idx": 1380035,
#     "movie_keyword": 4523930,
#     "movie_link": 29997,
#     "name": 4167491,
#     "person_info": 2963664,
#     "role_type": 12,
#     "title": 2528312
# }

# sample rate of queries.
sample_rate = 1

# reward scale params
light_reward_scale = 10
heavy_reward_scale = 10

# default_runtime=[]



