import duckdb

con= duckdb.connect('data/paysim.duckdb', read_only=True)

# Summary: smallest, largest, and average transactions per hour
print(con.sql("""
    WITH per_step AS (
	SELECT  step, COUNT(*) as txns
	FROM paysim
	GROUP BY step
    )
    SELECT 
	MIN(txns)		AS min_txns,
	MAX(txns) 		AS max_txns,
	ROUND(AVG(txns),1) 	AS avg_txns
    FROM per_step
"""))

#the 5 busiest hours

print(con.sql("""
    WITH per_step AS (
	SELECT step, COUNT(*) as txns
	FROM  paysim
	GROUP BY step
    )
    SELECT step, txns
    FROM per_step
    ORDER BY txns DESC
    LIMIT 5
"""))

con.close()
