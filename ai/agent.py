import json
import ollama

from ai.planner import plan
from ai.workflow import execute_workflow
from ai.response_builder import build_response
from ai.formatter import format_result
from ai.validator import validate
from ai.memory import memory_store, set_active_memory, reset_active_memory


def ask_ai(message, session_id):
    """
    session_id: 요청을 보낸 사용자를 구분하는 키.
    Django 뷰에서는 request.session.session_key를 넘겨주면 된다.
    (session_key가 없으면 request.session.save()로 먼저 생성해야 함)
    """

    memory = memory_store.get(session_id)
    token = set_active_memory(memory)

    try:
        memory.add_message("user", message)

        action = plan(message, memory)

        if not validate(action):
            return "Planner 결과가 올바르지 않습니다."

        steps = action.get("steps", [])

        if len(steps) == 0:

            response = ollama.chat(

                model="qwen3:4b",

                messages=[

                    {
                        "role":"user",
                        "content":message
                    }

                ]

            )

            answer = response["message"]["content"]
            memory.add_message("assistant", answer)
            return answer

        results = execute_workflow(
            steps
        )

        if results:
            memory.set_last_tool(results[-1]["tool"])

        formatted = format_result(results)

        if formatted is not None:
            memory.add_message("assistant", formatted)
            return formatted

        answer = build_response(results)
        memory.add_message("assistant", answer)
        return answer
    finally:
        reset_active_memory(token)
