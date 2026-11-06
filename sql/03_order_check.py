import duckdb


con= duckdb.connect('data/paysim.duckdb' , read_only= True)


# Peek: see LAG working on the first 5 rows
print(con.sql("""
    SELECT
	rowid,
	step,
	LAG(step) OVER  (ORDER BY rowid) as prev_step
    FROM paysim
    ORDER BY rowid
    LIMIT 155
"""))


# The real test: count rows where time goes backwards

print(con.sql("""
    SELECT COUNT(*) as backwards_rows
    FROM (
	SELECT
	    step,
	    LAG(step) OVER (ORDER BY rowid) as prev_step
	FROM paysim
    )
    WHERE step< prev_step
"""))



# Where does each new hour begin?
print(con.sql("""
    SELECT rowid, step, prev_step
    FROM (
        SELECT
            rowid,
            step,
            LAG(step) OVER (ORDER BY rowid) AS prev_step
        FROM paysim
    )
    WHERE step > prev_step
    ORDER BY rowid
    LIMIT 5
"""))

con.close()
