import json
import re
import ollama
from tools.registry import TOOLS


def build_system_prompt():

    return f"""
너는 병원 AI Planner이다.

사용 가능한 Tool

{build_tool_prompt()}

반드시 JSON 객체만 출력한다. 설명 문장, 코드블록, 주석은 금지한다.

출력 형식:
{{
    "steps": [
        {{
            "tool": "tool_name",
            "arguments": {{}}
        }}
    ]
}}

규칙:
1) 사용자 요청이 툴 실행 대상이면 반드시 steps를 채운다.
2) 직원 등록 요청("김민수를 원무과로 등록해")이면 create_employee 사용.
3) 직원 부서 변경("홍길동 부서를 총무과로 변경")이면 update_employee_department 사용.
4) 직원 삭제("홍길동 삭제")이면 delete_employee 사용.
5) 연차 차감("홍길동 연차 2일 차감")은 update_leave 에 amount=-2 사용.
6) 정보 조회("조회", "연차 알려줘")는 search_employee 또는 get_leave 사용.
7) 직원 명단 생성, 직원 엑셀 생성, 엑셀로 내보내기 요청은 export_employee_excel 사용.
8) 휴가 신청서 PDF 생성 요청은 create_leave_request_pdf 사용.
9) CSV 가져오기/CSV 입력 요청은 import_employees_csv 사용.
10) OCR/이미지 글자 인식 요청은 ocr_image_to_text 사용.
11) 공지 메일 발송 요청은 send_notice_email 사용.
12) 매일 오전 9시 휴가 현황 자동 생성 요청은 start_daily_leave_scheduler 사용.
13) 즉시 휴가 현황 리포트 생성 요청은 generate_leave_status_report 사용.
"""


def _parse_plan(content: str):

    content = (content or "").strip()

    candidates = [content]

    # 모델이 ```json ... ``` 형태로 감싸는 경우를 처리한다.
    fence_match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        content,
        re.DOTALL | re.IGNORECASE
    )
    if fence_match:
        candidates.append(fence_match.group(1).strip())

    object_match = re.search(r"\{[\s\S]*\}", content)
    if object_match:
        candidates.append(object_match.group(0).strip())

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if not isinstance(parsed, dict):
            continue

        raw_steps = parsed.get("steps", [])
        if not isinstance(raw_steps, list):
            return {"steps": []}

        normalized_steps = []
        for step in raw_steps:
            if not isinstance(step, dict):
                continue

            tool_name = step.get("tool")
            arguments = step.get("arguments", {})

            if not isinstance(tool_name, str) or not tool_name.strip():
                continue

            if not isinstance(arguments, dict):
                arguments = {}

            normalized_steps.append({
                "tool": tool_name,
                "arguments": arguments
            })

        return {"steps": normalized_steps}

    return {"steps": []}


def _tool_requires_name(tool_name):

    return tool_name in {
        "search_employee",
        "get_leave",
        "update_leave",
        "update_employee_department",
        "delete_employee",
        "create_leave_request_pdf"
    }


def _apply_memory_fallback(steps, message, memory):

    fallback_name = memory.resolve_employee_reference(message)

    for step in steps:
        tool_name = step.get("tool")

        if not _tool_requires_name(tool_name):
            continue

        arguments = step.setdefault("arguments", {})

        name = arguments.get("name")
        if isinstance(name, str) and name.strip():
            continue

        if fallback_name is not None:
            arguments["name"] = fallback_name

        if tool_name == "update_leave" and "amount" in arguments:
            amount = arguments["amount"]
            if isinstance(amount, (int, float)):
                if ("차감" in message or "감소" in message) and amount > 0:
                    arguments["amount"] = -amount

    return steps

def plan(message, memory):

    response = ollama.chat(

        model="qwen3:4b",

        messages=[

            {
                "role":"system",

                "content":build_system_prompt()
            },

            {
                "role":"user",
                "content":message
            }

        ]

    )

    action = _parse_plan(
        response["message"]["content"]
    )

    action["steps"] = _apply_memory_fallback(
        action.get("steps", []),
        message,
        memory
    )

    return action

def build_tool_prompt():

    prompt = ""

    for name, tool in TOOLS.items():

        prompt += f"""
Tool : {name}

설명 :
{tool['description']}

파라미터 :
{tool['parameters']}

"""

    return prompt
