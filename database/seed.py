try:
    from database.db import get_connection
except ModuleNotFoundError:
    # python database/seed.py 형태의 직접 실행을 지원한다.
    from db import get_connection

conn = get_connection()

cursor = conn.cursor()

employees = [

    ("2026001", "홍길동", "행정팀", 15),
    ("2026002", "김철수", "원무과", 12),
    ("2026003", "이영희", "간호부", 18),

]

cursor.executemany("""

INSERT OR IGNORE INTO employee

(employee_no,name,department,leave_days)

VALUES(?,?,?,?)

""", employees)

conn.commit()

conn.close()

print("샘플 데이터 입력 완료")