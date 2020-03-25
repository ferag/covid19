from sqlalchemy import create_engine
import sqlite3
engine = create_engine('sqlite://', echo=False)


import pandas as pd

df=pd.read_excel('images.xlsx')
df=df.dropna()
print(df)

coviddb=df.to_sql('images', con=engine)

x=engine.execute("SELECT edad, id FROM images ORDER BY random() LIMIT 10;").fetchall()
print(x)

