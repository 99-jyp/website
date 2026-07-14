try:
    from database.db import get_connection
except ModuleNotFoundError:
    # python database/init_db.py 형태의 직접 실행을 지원한다.
    from db import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employee(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    employee_no TEXT UNIQUE,

    name TEXT NOT NULL,

    department TEXT,

    leave_days INTEGER DEFAULT 15

)
""")

conn.commit()

conn.close()

print("DB 생성 완료")