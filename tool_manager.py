from tool_registry import TOOLS


def execute_tool(result):

    if not result.startswith("TOOL:"):
        return result

    _, tool_name, argument = result.split(":", 2)

    tool = TOOLS.get(tool_name)

    if tool is None:
        return "알 수 없는 도구입니다."

    return tool["function"](argument)
