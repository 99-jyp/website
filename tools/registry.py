TOOLS = {}


def register_tool(
    name,
    description,
    parameters=None
):

    def decorator(func):

        TOOLS[name] = {

            "description": description,

            "parameters": parameters or {},

            "function": func

        }

        return func

    return decorator

from tools import employee
from tools import automation