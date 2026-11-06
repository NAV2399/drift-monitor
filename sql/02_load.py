import duckdb

con= duckdb.connect('data/paysim.duckdb')

con.sql("""
     CREATE OR REPLACE TABLE paysim AS
     SELECT *FROM read_csv('data/paysim.csv')
""")

print(con.sql("SELECT COUNT(*) AS total_rows FROM paysim"))
print(con.sql("SELECT rowid, step , type, amount FROM paysim LIMIT 5 "))


con.close()	
