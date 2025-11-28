import os, psycopg
from psycopg.rows import tuple_row

DATABASE_URL = os.getenv("DATABASE_URL", "")

def test_pgvector_temp_table_kNN():
    if not DATABASE_URL:
        return
    with psycopg.connect(DATABASE_URL, row_factory=tuple_row) as c:
        # create a small temp table with vector dim 3
        c.execute("CREATE TEMP TABLE IF NOT EXISTS emb3 (id uuid DEFAULT gen_random_uuid(), v vector(3), content text)")
        c.execute("INSERT INTO emb3 (v, content) VALUES ('[0.1,0.2,0.3]', 'a'), ('[0.2,0.1,0.0]', 'b')")
        # query by nearest to [0.1,0.2,0.3]
        cur = c.execute("""SELECT content FROM emb3 ORDER BY v <-> '[0.1,0.2,0.3]' LIMIT 1""")
        row = cur.fetchone()
        assert row is not None
