from tools.registry import TOOLS


def validate(action):

    if "steps" not in action:

        return False

    for step in action["steps"]:

        tool = step.get("tool")

        if tool not in TOOLS:

            return False

    return True