def _format_get_leave(result):
    if result["success"]:
        return f"남은 연차는 {result['leave']}일입니다."
    return result["message"]


def _format_update_leave(result):
    if not result["success"]:
        return result["message"]
    employee = result["employee"]
    return (
        f"{employee['name']}님의 연차가 변경되었습니다.\n"
        f"현재 남은 연차는 {employee['leave']}일입니다."
    )


def _format_create_employee(result):
    if not result["success"]:
        return result["message"]
    employee = result["employee"]
    return (
        f"{employee['name']}님을 {employee['department']}에 등록했습니다.\n"
        f"사번: {employee['employee_no']}, 연차: {employee['leave']}일"
    )


def _format_update_employee_department(result):
    if not result["success"]:
        return result["message"]
    employee = result["employee"]
    return f"{employee['name']}님의 부서를 {employee['department']}로 변경했습니다."


def _format_delete_employee(result):
    if not result["success"]:
        return result["message"]
    employee = result["employee"]
    return f"{employee['name']}님을 삭제했습니다."


def _format_export_employee_excel(result):
    if not result["success"]:
        return result["message"]
    return (
        f"직원 명단 엑셀 파일을 생성했습니다.\n"
        f"파일: {result['file_path']}\n"
        f"총 {result['count']}명"
    )


def _format_create_leave_request_pdf(result):
    if not result["success"]:
        return result["message"]
    return (
        f"휴가 신청서 PDF를 생성했습니다.\n"
        f"직원: {result['name']}\n"
        f"파일: {result['file_path']}"
    )


def _format_import_employees_csv(result):
    if not result["success"]:
        return result["message"]
    return (
        f"CSV 가져오기를 완료했습니다.\n"
        f"신규 등록: {result['imported']}명\n"
        f"기존 수정: {result['updated']}명"
    )


def _format_ocr_image_to_text(result):
    if not result["success"]:
        return result["message"]
    preview = result["text"][:120]
    return (
        f"OCR 추출을 완료했습니다.\n"
        f"저장 파일: {result['text_path']}\n"
        f"미리보기: {preview}"
    )


def _format_send_notice_email(result):
    if not result["success"]:
        return result["message"]
    if result.get("dry_run"):
        return (
            f"메일 발송 검증만 수행했습니다.\n"
            f"수신자: {result['to_email']}\n"
            f"제목: {result['subject']}"
        )
    return (
        f"메일 발송을 완료했습니다.\n"
        f"수신자: {result['to_email']}\n"
        f"제목: {result['subject']}"
    )


def _format_generate_leave_status_report(result):
    if not result["success"]:
        return result["message"]
    return (
        f"휴가 현황 리포트를 생성했습니다.\n"
        f"파일: {result['file_path']}\n"
        f"총 {result['count']}명"
    )


def _format_start_daily_leave_scheduler(result):
    if not result["success"]:
        return result["message"]
    return f"스케줄러를 시작했습니다.\n매일 {result['hour']:02d}:{result['minute']:02d} 실행"


def _format_stop_daily_leave_scheduler(result):
    return result["message"]


# tool 이름 -> 처리 함수. 새 tool 추가할 땐 여기에 한 줄만 추가하면 됨.
TOOL_FORMATTERS = {
    "get_leave": _format_get_leave,
    "update_leave": _format_update_leave,
    "create_employee": _format_create_employee,
    "update_employee_department": _format_update_employee_department,
    "delete_employee": _format_delete_employee,
    "export_employee_excel": _format_export_employee_excel,
    "create_leave_request_pdf": _format_create_leave_request_pdf,
    "import_employees_csv": _format_import_employees_csv,
    "ocr_image_to_text": _format_ocr_image_to_text,
    "send_notice_email": _format_send_notice_email,
    "generate_leave_status_report": _format_generate_leave_status_report,
    "start_daily_leave_scheduler": _format_start_daily_leave_scheduler,
    "stop_daily_leave_scheduler": _format_stop_daily_leave_scheduler,
}


def format_result(results):

    if not results:
        return None

    tool = results[-1]["tool"]
    result = results[-1]["result"]

    handler = TOOL_FORMATTERS.get(tool)

    if handler is None:
        return None

    return handler(result)
