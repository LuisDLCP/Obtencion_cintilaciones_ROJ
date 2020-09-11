import csv

"""
# Read a csv file(dictionaries)
csv.register_dialect('myDialect',
                      delimiter = '|',
                      skipinitialspace = True,
                      quoting = csv.QUOTE_ALL)

with open('example.csv') as f:
    data = csv.DictReader(f, dialect = 'myDialect') #delimiter='|', skipinitialspace=True)
    for row in data:
        print(dict(row))

print(data)


"""

# Write a csv file

field  = ['Carol', 'huachipa', 60]

with open('example.csv', 'a') as f:
    writer = csv.writer(f, delimiter='|')
    writer.writerow(field)
