"""
raw SQL로 관리되는 employee 테이블을 생성한다.

주의: Django가 관리하는 테이블(auth_*, django_*, core_notification 등)은
web/manage.py migrate 가 책임진다. 이 스크립트는 AI 에이전트/services 계층이
직접 sqlite3로 접근하는 employee 테이블만 다룬다.

hospital.db가 유실되거나, 새 환경에 처음 배포할 때 다음처럼 실행하면 된다:

    python -m database.init_db
"""

try:
    from database.db import get_connection
except ModuleNotFoundError:
    # python database/init_db.py 형태의 직접 실행을 지원한다.
    from db import get_connection


CREATE_EMPLOYEE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS employee (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_no   TEXT UNIQUE,
    name          TEXT NOT NULL,
    department    TEXT,
    leave_days    INTEGER DEFAULT 15
);
"""


def init_db():

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(CREATE_EMPLOYEE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()

    print("employee 테이블 준비 완료 (이미 있으면 그대로 유지됨)")


if __name__ == "__main__":
    init_db()
