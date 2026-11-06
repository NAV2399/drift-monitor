import duckdb

con = duckdb.connect()

result = con.sql("""
    SELECT 
        COUNT(*)                AS total_rows,
        COUNT(DISTINCT step)    AS distinct_steps,
        MIN(step)               AS min_step,
        MAX(step)               AS max_step
    FROM read_csv('data/paysim.csv')

""")

print(result)