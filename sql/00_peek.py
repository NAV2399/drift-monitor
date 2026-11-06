import duckdb

con = duckdb.connect('data/paysim.duckdb', read_only=True)

# What columns exist, and what type is each one?
print(con.sql("DESCRIBE paysim"))

# What do the first rows look like?
print(con.sql("SELECT * FROM paysim LIMIT 5"))

con.close()
