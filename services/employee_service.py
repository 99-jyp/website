import sqlite3

from database.db import get_connection
from datetime import datetime


# 동시 요청으로 같은 사번이 생성되려 할 때 재시도할 최대 횟수
_EMPLOYEE_NO_MAX_RETRIES = 5


class EmployeeService:

    @staticmethod
    def list_employees():

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT employee_no, name, department, leave_days
                FROM employee
                ORDER BY employee_no ASC
                """
            )

            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def _generate_employee_no(conn):

        year_prefix = str(datetime.now().year)

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT employee_no
            FROM employee
            WHERE employee_no LIKE ?
            ORDER BY employee_no DESC
            LIMIT 1
            """,
            (f"{year_prefix}%",)
        )

        row = cursor.fetchone()

        if row is None:
            return f"{year_prefix}001"

        last_no = row["employee_no"]
        suffix = int(last_no[len(year_prefix):])
        return f"{year_prefix}{suffix + 1:03d}"

    @staticmethod
    def find_by_name(name):

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM employee
                WHERE name=?
                """,
                (name,)
            )

            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def create_employee(name, department, leave_days=15):
        """
        사번은 '마지막 사번 + 1'로 계산하므로, 두 요청이 거의 동시에 들어오면
        같은 사번을 계산해버릴 수 있다 (레이스 컨디션).

        DB의 employee_no UNIQUE 제약(있다는 전제)에 기대어, INSERT가
        중복으로 실패하면 사번을 다시 계산해서 재시도한다.
        DB에 UNIQUE 제약이 아직 없다면 반드시 추가해야 이 방어가 의미가 있다.
        """

        conn = get_connection()
        try:
            cursor = conn.cursor()

            last_error = None

            for _ in range(_EMPLOYEE_NO_MAX_RETRIES):

                employee_no = EmployeeService._generate_employee_no(conn)

                try:
                    cursor.execute(
                        """
                        INSERT INTO employee (employee_no, name, department, leave_days)
                        VALUES (?, ?, ?, ?)
                        """,
                        (employee_no, name, department, leave_days)
                    )
                    conn.commit()
                    break

                except sqlite3.IntegrityError as exc:
                    # employee_no가 중복된 경우로 추정 -> 롤백하고 재시도
                    conn.rollback()
                    last_error = exc
                    continue
            else:
                # 재시도를 다 썼는데도 실패한 경우
                raise RuntimeError(
                    "사번 생성에 반복적으로 실패했습니다. "
                    "employee_no UNIQUE 제약 여부를 확인해주세요."
                ) from last_error

            cursor.execute(
                """
                SELECT *
                FROM employee
                WHERE employee_no = ?
                """,
                (employee_no,)
            )

            return cursor.fetchone()

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update_department(name, department):

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE employee
                SET department = ?
                WHERE name = ?
                """,
                (department, name)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                return None

            conn.commit()

            cursor.execute(
                """
                SELECT *
                FROM employee
                WHERE name = ?
                """,
                (name,)
            )

            return cursor.fetchone()

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update_leave(name, amount):

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE employee
                SET leave_days = leave_days + ?
                WHERE name = ?
                """,
                (amount, name)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                return None

            conn.commit()

            cursor.execute(
                """
                SELECT *
                FROM employee
                WHERE name = ?
                """,
                (name,)
            )

            return cursor.fetchone()

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def delete_employee(name):

        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM employee
                WHERE name = ?
                """,
                (name,)
            )
            employee = cursor.fetchone()

            if employee is None:
                conn.rollback()
                return None

            cursor.execute(
                """
                DELETE FROM employee
                WHERE name = ?
                """,
                (name,)
            )

            conn.commit()
            return employee

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
