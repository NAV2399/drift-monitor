import duckdb

con = duckdb.connect('data/paysim.duckdb', read_only=True)

WINDOW_SIZE = 50_000

BASE = f"""
    WITH windowed AS (
        SELECT
            rowid // {WINDOW_SIZE} AS window_id,
            step, type, amount, isFraud
        FROM paysim
    ),
    per_window AS (
        SELECT
            window_id,
            MIN(step)  AS first_step,
            MAX(step)  AS last_step,
            COUNT(*)   AS txns,
            ROUND(100.0 * AVG(CASE WHEN type = 'TRANSFER' THEN 1 ELSE 0 END), 2) AS transfer_pct,
            ROUND(100.0 * AVG(CASE WHEN type = 'PAYMENT'  THEN 1 ELSE 0 END), 2) AS payment_pct,
            ROUND(AVG(amount), 0)          AS avg_amount,
            ROUND(100.0 * AVG(isFraud), 3) AS fraud_pct
        FROM windowed
        GROUP BY window_id
    )
"""

# First 10 windows
print(con.sql(BASE + "SELECT * FROM per_window ORDER BY window_id LIMIT 10"))

# How much does each metric move across ALL windows?
print(con.sql(BASE + """
    SELECT
        COUNT(*)          AS windows,
        MIN(transfer_pct) AS min_transfer, MAX(transfer_pct) AS max_transfer,
        MIN(avg_amount)   AS min_amount,   MAX(avg_amount)   AS max_amount,
        MIN(fraud_pct)    AS min_fraud,    MAX(fraud_pct)    AS max_fraud
    FROM per_window
"""))
con.sql(BASE + """
    SELECT window_id, first_step, last_step, fraud_pct
    FROM per_window
    ORDER BY fraud_pct DESC
    LIMIT 5
""").show(max_width=250)

con.close()
