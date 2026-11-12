import duckdb

con = duckdb.connect('data/paysim.duckdb', read_only=True)

print(con.sql("""
    SELECT
        LEFT(nameDest, 1)                                     AS dest_kind,
        COUNT(*)                                              AS txns,
        SUM(CASE WHEN newbalanceDest <> 0 THEN 1 ELSE 0 END)  AS nonzero_after
    FROM paysim
    GROUP BY dest_kind
"""))

con.close()
