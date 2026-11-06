import duckdb


con = duckdb.connect('data/paysim.duckdb', read_only= True)

# Fraud rate for each transaction type

print(con.sql("""
    SELECT
	type,
	COUNT(*)					AS total_txns,
	SUM(isFraud)					AS fraud_txns,
	ROUND(100.0 * SUM(isFraud) / COUNT(*),3)  	AS fraud_rate_pct
    FROM paysim
    GROUP BY type
    ORDER BY fraud_rate_pct DESC
"""))

# Fraud rate across the whole dataset
print(con.sql("""
    SELECT
        COUNT(*)                                   AS total_txns,
        SUM(isFraud)                               AS fraud_txns,
        ROUND(100.0 * SUM(isFraud) / COUNT(*), 4)  AS fraud_rate_pct
    FROM paysim
"""))


con.close()

