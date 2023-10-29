import shutil

class InterpreterMapping:
    PY = "python"
    JS = "node"
    RB = "ruby"
    PHP = "php"
    PL = "perl"

class MapExt:
    @staticmethod
    def resolve(script_path: str) -> str:
        script_extension = script_path.lower().split(".")[-1]
        if script_extension == "py" and shutil.which("python3"):
            return "python3"
        return getattr(InterpreterMapping, script_extension.upper(), "")
