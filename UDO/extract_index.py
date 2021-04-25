# -----------------------------------------------------------------------
# Copyright (c) 2021    Cornell Database Group
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import argparse
import json
import os
import re
import itertools

udo_parser = argparse.ArgumentParser(description='UDO index candidate generator.')

udo_parser.add_argument('-db_schema', help='the database schmea to optimizes')
udo_parser.add_argument('-queries', help='queries')

args = udo_parser.parse_args()
# change
args = vars(args)

with open(args['db_schema']) as f:
    db_schema = json.load(f)

if args['queries']:
    queries = dict()
    for file_name in os.listdir(args['queries']):
        if file_name.endswith(".sql"):
            with open(os.path.join(args['queries'], file_name)) as f:
                content = f.read()
                queries[file_name] = content

table_pattern = re.compile("FROM(.*)WHERE")
where_pattern = re.compile("WHERE(.*)")
collect_indices = dict()
for query_id, query in queries.items():
    matches = table_pattern.findall(query)
    join_elements = matches[0].split(',')
    rename_table_dict = {}
    for join_element in join_elements:
        rename_pos = join_element.index("AS")
        if join_element[:rename_pos].strip() not in rename_table_dict:
            rename_table_dict[join_element[:rename_pos].strip()] = [join_element[rename_pos + 2:].strip()]
        else:
            rename_table_dict[join_element[:rename_pos].strip()].append(join_element[rename_pos + 2:].strip())
    print(rename_table_dict)
    where_clause = where_pattern.findall(query)[0]
    for table, columns in db_schema.items():
        if table in rename_table_dict:
            for rename_table in rename_table_dict[table]:
                for column in columns:
                    if rename_table + '.' + column in where_clause:
                        if table not in collect_indices:
                            collect_indices[table] = [column]
                        elif column not in collect_indices[table]:
                            collect_indices[table].append(column)
print(collect_indices)

for k in collect_indices.keys():
    all_candidate = collect_indices[k]
    v = []
    for i in range(1, len(all_candidate) + 1):
        v += [','.join(comb) for comb in (itertools.combinations(all_candidate, i))]
    for i in range(len(v)):
        print("('IDX_%s_%d','%s','%s')," % (k, i, k, v[i]))
