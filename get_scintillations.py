import csv

csv.register_dialect('myDialect',
                      delimiter = '|',
                      skipinitialspace = True,
                      quoting = csv.QUOTE_ALL)

with open('example.csv') as f:
    data = csv.reader(f, dialect = 'myDialect')
    i = 0
    for row in data:
        i += 1
        if i == 2: a = row

    print(a)
    print(type(a))
