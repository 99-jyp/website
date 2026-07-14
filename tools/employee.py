from ai.memory import memory
from tools.registry import register_tool
from services.employee_service import EmployeeService
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook


@register_tool(
    name="search_employee",
    description="직원 검색",
    parameters={
        "name": "직원 이름"
    }
)
def search_employee(name: str):

    employee = EmployeeService.find_by_name(name)

    if employee is None:
        return {
            "success": False,
            "message": "직원을 찾을 수 없습니다."
        }

    memory.set_employee(name)
    memory.set_department(employee["department"])

    return {
        "success": True,
        "employee": {
            "employee_no": employee["employee_no"],
            "name": employee["name"],
            "department": employee["department"],
            "leave": employee["leave_days"]
        }
    }


@register_tool(
    name="get_leave",
    description="남은 연차 조회",
    parameters={
        "name": "직원 이름"
    }
)
def get_leave(name=None):

    if name is None:
        name = memory.get_employee()

    if name is None:
        return {
            "success": False,
            "message": "최근 조회한 직원이 없습니다."
        }

    employee = EmployeeService.find_by_name(name)

    if employee is None:
        return {
            "success": False,
            "message": "직원을 찾을 수 없습니다."
        }

    return {
        "success": True,
        "leave": employee["leave_days"]
    }

@register_tool(
    name="update_leave",
    description="직원 연차 변경",
    parameters={
        "name": "직원 이름",
        "amount": "변경할 연차"
    }
)
def update_leave(name=None, amount=0):

    if name is None:
        # 되돌릴 수 있는 액션이므로 get_leave와 동일하게
        # "최근 조회/작업한 직원"을 지시어 여부와 무관하게 기본 대상으로 삼는다.
        name = memory.get_employee()

    if name is None:
        return {
            "success": False,
            "message": "최근 조회한 직원이 없습니다."
        }

    employee = EmployeeService.update_leave(
        name,
        amount
    )

    if employee is None:
        return {
            "success": False,
            "message": "직원을 찾을 수 없습니다."
        }

    return {
        "success": True,
        "employee": {
            "name": employee["name"],
            "leave": employee["leave_days"]
        }
    }


@register_tool(
    name="create_employee",
    description="직원 등록",
    parameters={
        "name": "직원 이름",
        "department": "부서명",
        "leave_days": "초기 연차(선택)"
    }
)
def create_employee(name, department, leave_days=15):

    try:
        employee = EmployeeService.create_employee(
            name=name,
            department=department,
            leave_days=leave_days
        )
    except RuntimeError as exc:
        # 사번 생성 재시도가 모두 실패한 경우 (employee_service.py 참고)
        return {
            "success": False,
            "message": f"직원 등록에 실패했습니다: {exc}"
        }

    memory.set_employee(name)
    memory.set_department(department)

    return {
        "success": True,
        "employee": {
            "employee_no": employee["employee_no"],
            "name": employee["name"],
            "department": employee["department"],
            "leave": employee["leave_days"]
        }
    }


@register_tool(
    name="update_employee_department",
    description="직원 부서 변경",
    parameters={
        "name": "직원 이름",
        "department": "변경할 부서"
    }
)
def update_employee_department(name, department):

    if name is None:
        # 되돌릴 수 있는 액션이므로 get_leave와 동일하게
        # "최근 조회/작업한 직원"을 지시어 여부와 무관하게 기본 대상으로 삼는다.
        name = memory.get_employee()

    if name is None:
        return {
            "success": False,
            "message": "최근 조회한 직원이 없습니다."
        }

    employee = EmployeeService.update_department(name, department)

    if employee is None:
        return {
            "success": False,
            "message": "직원을 찾을 수 없습니다."
        }

    memory.set_employee(name)
    memory.set_department(department)

    return {
        "success": True,
        "employee": {
            "name": employee["name"],
            "department": employee["department"]
        }
    }


@register_tool(
    name="delete_employee",
    description="직원 삭제",
    parameters={
        "name": "직원 이름"
    }
)
def delete_employee(name=None):

    if name is None:
        # 파괴적/비가역적 액션이므로 자동 fallback을 하지 않는다.
        # planner 단계에서 "그 사람 삭제해줘"처럼 지시어가 있어야만
        # 이름이 채워지고, 애매한 경우엔 명시적으로 되묻는다.
        return {
            "success": False,
            "message": "삭제할 직원을 지정해주세요. (예: \"홍길동 삭제\", \"그 사람 삭제\")"
        }

    employee = EmployeeService.delete_employee(name)

    if employee is None:
        return {
            "success": False,
            "message": "직원을 찾을 수 없습니다."
        }

    if memory.get_employee() == name:
        memory.set_employee(None)
        memory.set_department(None)

    return {
        "success": True,
        "employee": {
            "name": employee["name"],
            "department": employee["department"]
        }
    }


@register_tool(
    name="export_employee_excel",
    description="직원 명단 엑셀 파일 생성",
    parameters={
        "filename": "생성 파일명(선택)"
    }
)
def export_employee_excel(filename=None):

    employees = EmployeeService.list_employees()

    if not employees:
        return {
            "success": False,
            "message": "내보낼 직원 데이터가 없습니다."
        }

    workbook = Workbook()
    worksheet = workbook.active
    if worksheet is None:
        worksheet = workbook.create_sheet("직원명단")
    worksheet.title = "직원명단"

    worksheet.append(["사번", "이름", "부서", "연차"])

    for employee in employees:
        worksheet.append([
            employee["employee_no"],
            employee["name"],
            employee["department"],
            employee["leave_days"]
        ])

    export_dir = Path(__file__).resolve().parent.parent / "data" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    if filename is None or not str(filename).strip():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employee_list_{timestamp}.xlsx"

    if not str(filename).lower().endswith(".xlsx"):
        filename = f"{filename}.xlsx"

    output_path = export_dir / filename
    workbook.save(output_path)

    return {
        "success": True,
        "file_path": str(output_path),
        "count": len(employees)
    }
