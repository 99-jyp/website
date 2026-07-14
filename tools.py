employees = {
    "홍길동": {
        "department": "행정팀",
        "leave": 15
    },
    "김철수": {
        "department": "원무과",
        "leave": 12
    }
}


def search_employee(name: str):

    employee = employees.get(name)

    if employee is None:
        return {
            "success": False,
            "message": "직원을 찾을 수 없습니다."
        }

    return {
        "success": True,
        "employee": {
            "name": name,
            "department": employee["department"],
            "leave": employee["leave"]
        }
    }