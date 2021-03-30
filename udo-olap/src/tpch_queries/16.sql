 select
     p_brand,
     p_type,
     p_size,
     count(distinct ps_suppkey) as supplier_cnt
 from
     partsupp,
     part
 where
     p_partkey = ps_partkey
     and p_brand <> 'Brand23'
     and p_type not like 'MEDIUM BRUSHED%'
     and p_size in (45, 35, 7, 23, 24, 18, 14, 15)
     and ps_suppkey not in (
         select
             s_suppkey
         from
             supplier
         where
             s_comment like '%Customer%Complaints%'
     )
 group by
     p_brand,
     p_type,
     p_size
 order by
     supplier_cnt desc,
     p_brand,
     p_type,
     p_size
 limit 1;