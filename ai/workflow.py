from tools.registry import TOOLS


def execute_workflow(steps):

    results = []

    for step in steps:

        tool_name = step.get("tool")
        arguments = step.get("arguments", {})

        tool = TOOLS.get(tool_name)

        if tool is None:
            results.append({
                "tool": tool_name,
                "result": {
                    "success": False,
                    "message": f"알 수 없는 Tool : {tool_name}"
                }
            })
            continue

        try:

            result = tool["function"](
                **arguments
            )

        except Exception as e:

            result = {
                "success": False,
                "message": str(e)
            }

        results.append({

            "tool": tool_name,
            "result": result

        })

    return results