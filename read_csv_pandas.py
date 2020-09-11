import pandas as pd

cols = ["ID","Grade","Age","Nº courses"]

df = pd.read_csv('example2.csv',usecols=["ID"], names = cols)

print(df)
#print(type(df))
