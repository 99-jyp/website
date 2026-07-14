import json
import ollama


def build_response(results):

    response = ollama.chat(

        model="qwen3:4b",

        messages=[

            {
                "role": "system",

                "content": """
너는 병원 AI이다.

Tool 실행 결과를 이용하여
자연스럽게 설명해라.

Tool 이름은 말하지 않는다.
"""
            },

            {
                "role": "user",

                "content": json.dumps(
                    results,
                    ensure_ascii=False,
                    indent=2
                )
            }

        ]

    )

    return response["message"]["content"]