import csv
import os
import smtplib
import threading
import time
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

from ai.memory import memory
from services.employee_service import EmployeeService
from tools.registry import register_tool

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception:
    A4 = None
    canvas = None

try:
    from PIL import Image
    import pytesseract
except Exception:
    Image = None
    pytesseract = None

_scheduler_state = {
    "running": False,
    "thread": None,
    "hour": 9,
    "minute": 0,
    "last_run_date": None,
}


def _normalize_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _generate_leave_status_report_file():
    employees = EmployeeService.list_employees()

    report_dir = _PROJECT_ROOT / "data" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    date_key = datetime.now().strftime("%Y%m%d")
    file_path = report_dir / f"leave_status_{date_key}.txt"

    lines = [
        f"휴가 현황 리포트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "사번\t이름\t부서\t연차",
    ]

    for employee in employees:
        lines.append(
            f"{employee['employee_no']}\t{employee['name']}\t"
            f"{employee['department']}\t{employee['leave_days']}"
        )

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return str(file_path), len(employees)


def _scheduler_loop():
    while _scheduler_state["running"]:
        now = datetime.now()
        target_hour = _scheduler_state["hour"]
        target_minute = _scheduler_state["minute"]

        if now.hour == target_hour and now.minute == target_minute:
            today_key = now.strftime("%Y%m%d")
            if _scheduler_state["last_run_date"] != today_key:
                _generate_leave_status_report_file()
                _scheduler_state["last_run_date"] = today_key

        time.sleep(30)


@register_tool(
    name="create_leave_request_pdf",
    description="휴가 신청서 PDF 생성",
    parameters={
        "name": "직원 이름",
        "start_date": "휴가 시작일(YYYY-MM-DD)",
        "end_date": "휴가 종료일(YYYY-MM-DD)",
        "reason": "사유",
        "filename": "파일명(선택)"
    }
)
def create_leave_request_pdf(name=None, start_date=None, end_date=None, reason=None, filename=None):
    if name is None:
        name = memory.resolve_employee_reference("휴가 신청서")

    if not name:
        return {"success": False, "message": "직원 이름이 필요합니다."}

    employee = EmployeeService.find_by_name(name)
    if employee is None:
        return {"success": False, "message": "직원을 찾을 수 없습니다."}

    if canvas is None or A4 is None:
        return {
            "success": False,
            "message": "reportlab이 설치되어 있지 않습니다. requirements 설치 후 다시 시도하세요."
        }

    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")
    if end_date is None:
        end_date = start_date
    if reason is None:
        reason = "개인 사유"

    export_dir = _PROJECT_ROOT / "data" / "pdf"
    export_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leave_request_{name}_{timestamp}.pdf"

    if not str(filename).lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    output_path = export_dir / filename

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    text = pdf.beginText(50, height - 50)
    text.setFont("Helvetica", 12)
    text.textLine("Hospital AI - Leave Request Form")
    text.textLine("")
    text.textLine(f"Name: {employee['name']}")
    text.textLine(f"Department: {employee['department']}")
    text.textLine(f"Employee No: {employee['employee_no']}")
    text.textLine(f"Start Date: {start_date}")
    text.textLine(f"End Date: {end_date}")
    text.textLine(f"Reason: {reason}")
    text.textLine("")
    text.textLine(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    pdf.drawText(text)
    pdf.showPage()
    pdf.save()

    return {
        "success": True,
        "file_path": str(output_path),
        "name": employee["name"],
    }


@register_tool(
    name="import_employees_csv",
    description="CSV 파일의 직원 데이터를 DB로 가져오기",
    parameters={
        "csv_path": "CSV 파일 경로"
    }
)
def import_employees_csv(csv_path):
    if not csv_path:
        return {"success": False, "message": "csv_path가 필요합니다."}

    source_path = Path(csv_path)
    if not source_path.exists():
        return {"success": False, "message": "CSV 파일을 찾을 수 없습니다."}

    imported = 0
    updated = 0

    with source_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required_columns = {"name", "department", "leave_days"}

        if not reader.fieldnames:
            return {"success": False, "message": "CSV 헤더가 비어 있습니다."}

        lower_fieldnames = {column.strip().lower() for column in reader.fieldnames}
        if not required_columns.issubset(lower_fieldnames):
            return {
                "success": False,
                "message": "CSV 헤더는 name, department, leave_days를 포함해야 합니다."
            }

        for row in reader:
            normalized_row = {k.strip().lower(): v for k, v in row.items()}
            name = (normalized_row.get("name") or "").strip()
            department = (normalized_row.get("department") or "").strip()
            leave_days = _normalize_int(normalized_row.get("leave_days"), 15)

            if not name:
                continue

            existing = EmployeeService.find_by_name(name)
            if existing is None:
                EmployeeService.create_employee(name=name, department=department, leave_days=leave_days)
                imported += 1
                continue

            EmployeeService.update_department(name=name, department=department or existing["department"])
            leave_delta = leave_days - int(existing["leave_days"])
            if leave_delta != 0:
                EmployeeService.update_leave(name=name, amount=leave_delta)
            updated += 1

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
    }


@register_tool(
    name="ocr_image_to_text",
    description="이미지에서 텍스트를 OCR로 추출",
    parameters={
        "image_path": "이미지 파일 경로",
        "save_to": "텍스트 저장 파일 경로(선택)"
    }
)
def ocr_image_to_text(image_path, save_to=None):
    if not image_path:
        return {"success": False, "message": "image_path가 필요합니다."}

    source = Path(image_path)
    if not source.exists():
        return {"success": False, "message": "이미지 파일을 찾을 수 없습니다."}

    if Image is None or pytesseract is None:
        return {
            "success": False,
            "message": "pytesseract/Pillow가 설치되어 있지 않습니다. requirements 설치 후 다시 시도하세요."
        }

    try:
        text = pytesseract.image_to_string(Image.open(source), lang="kor+eng")
    except Exception as exc:
        return {
            "success": False,
            "message": f"OCR 처리 중 오류: {exc}"
        }

    if save_to:
        target = Path(save_to)
    else:
        target_dir = _PROJECT_ROOT / "data" / "ocr"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{source.stem}_ocr.txt"

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")

    return {
        "success": True,
        "text": text.strip(),
        "text_path": str(target)
    }


@register_tool(
    name="send_notice_email",
    description="공지 메일 발송",
    parameters={
        "to_email": "수신자 이메일",
        "subject": "메일 제목",
        "body": "메일 본문",
        "smtp_host": "SMTP 호스트(선택)",
        "smtp_port": "SMTP 포트(선택)",
        "smtp_user": "SMTP 계정(선택)",
        "smtp_password": "SMTP 비밀번호(선택)",
        "from_email": "발신자 이메일(선택)",
        "use_tls": "TLS 사용 여부(선택)",
        "dry_run": "실제 발송 대신 검증만 수행(선택)"
    }
)
def send_notice_email(
    to_email,
    subject,
    body,
    smtp_host=None,
    smtp_port=None,
    smtp_user=None,
    smtp_password=None,
    from_email=None,
    use_tls=True,
    dry_run=True,
):
    if not to_email or not subject or not body:
        return {"success": False, "message": "to_email, subject, body는 필수입니다."}

    smtp_host = smtp_host or os.getenv("SMTP_HOST")
    smtp_port = _normalize_int(smtp_port or os.getenv("SMTP_PORT"), 587)
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
    from_email = from_email or os.getenv("SMTP_FROM") or smtp_user

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "메일 발송 검증 완료(실제 발송 안 함)",
            "to_email": to_email,
            "subject": subject,
        }

    if not smtp_host or not smtp_user or not smtp_password or not from_email:
        return {
            "success": False,
            "message": "SMTP 설정이 부족합니다. smtp_host/smtp_user/smtp_password/from_email을 확인하세요."
        }

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())
    except Exception as exc:
        return {
            "success": False,
            "message": f"메일 발송 실패: {exc}"
        }

    return {
        "success": True,
        "dry_run": False,
        "message": "메일을 발송했습니다.",
        "to_email": to_email,
        "subject": subject,
    }


@register_tool(
    name="generate_leave_status_report",
    description="현재 휴가 현황 리포트를 생성",
    parameters={}
)
def generate_leave_status_report():
    file_path, count = _generate_leave_status_report_file()
    return {
        "success": True,
        "file_path": file_path,
        "count": count,
    }


@register_tool(
    name="start_daily_leave_scheduler",
    description="매일 지정 시각에 휴가 현황 리포트를 자동 생성",
    parameters={
        "hour": "실행 시(기본 9)",
        "minute": "실행 분(기본 0)"
    }
)
def start_daily_leave_scheduler(hour=9, minute=0):
    hour = _normalize_int(hour, 9)
    minute = _normalize_int(minute, 0)

    if _scheduler_state["running"]:
        return {
            "success": True,
            "message": "스케줄러가 이미 실행 중입니다.",
            "hour": _scheduler_state["hour"],
            "minute": _scheduler_state["minute"],
        }

    _scheduler_state["running"] = True
    _scheduler_state["hour"] = max(0, min(23, hour))
    _scheduler_state["minute"] = max(0, min(59, minute))
    _scheduler_state["last_run_date"] = None

    thread = threading.Thread(target=_scheduler_loop, daemon=True)
    thread.start()
    _scheduler_state["thread"] = thread

    return {
        "success": True,
        "message": "스케줄러를 시작했습니다.",
        "hour": _scheduler_state["hour"],
        "minute": _scheduler_state["minute"],
    }


@register_tool(
    name="stop_daily_leave_scheduler",
    description="휴가 현황 자동 생성 스케줄러 중지",
    parameters={}
)
def stop_daily_leave_scheduler():
    if not _scheduler_state["running"]:
        return {
            "success": True,
            "message": "스케줄러가 실행 중이 아닙니다.",
        }

    _scheduler_state["running"] = False
    return {
        "success": True,
        "message": "스케줄러를 중지했습니다.",
    }
