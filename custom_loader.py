import ast
import builtins
import linecache
import multiprocessing as mp
import os
import traceback
from types import GeneratorType

TIMEOUT_SECONDS = 5

ALLOWED_IMPORTS = {
    "math",
    "random",
}

FORBIDDEN_MODULE_PREFIXES = (
    "os",
    "sys",
    "subprocess",
    "shutil",
    "pathlib",
    "socket",
    "requests",
    "urllib",
    "ctypes",
    "pickle",
    "marshal",
)

FORBIDDEN_CALLS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "open",
    "input",
    "breakpoint",
}

SUPPORTED_ENTRYPOINTS = (
    "run",
    "get_states",
    "visualize",
    "algorithm",
)


def _basename(path: str) -> str:
    return os.path.basename(path)


def _get_source_line(file_path: str, lineno: int) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if 1 <= lineno <= len(lines):
            return lines[lineno - 1].rstrip("\n")
    except Exception:
        pass
    return ""


def _format_error_message(error_type: str, message: str, line: int = None, code: str = "") -> str:
    parts = [f"{error_type}: {message}"]
    if line:
        parts.append(f"Line {line}")
    if code:
        parts.append(f"Code: {code.strip()}")
    return " | ".join(parts)


def _safe_builtins():
    allowed_names = [
        "abs", "all", "any", "bool", "dict", "enumerate", "float", "int", "len",
        "list", "max", "min", "print", "range", "reversed", "round", "set",
        "sorted", "str", "sum", "tuple", "zip"
    ]
    return {name: getattr(builtins, name) for name in allowed_names}


def _import_allowed_module(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root in ALLOWED_IMPORTS:
        return builtins.__import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Import not allowed: {name}")


def _build_exec_globals():
    safe = _safe_builtins()
    safe["__import__"] = _import_allowed_module
    return {
        "__builtins__": safe,
        "__name__": "__custom_sandbox__",
    }


def _normalize_state(step, index, previous_data):
    if not isinstance(step, dict):
        return None, f"State #{index} is not a dict."

    if "data" not in step:
        if previous_data is None:
            return None, f"State #{index} missing 'data' key."
        step = dict(step)
        step["data"] = previous_data[:]

    data = step.get("data")
    if not isinstance(data, list):
        return None, f"State #{index} has invalid 'data'. Expected list."

    normalized = {
        "data": data[:],
        "active": list(step.get("active", [])),
        "swap": list(step.get("swap", [])),
        "sorted_indices": list(step.get("sorted_indices", [])),
        "found_indices": list(step.get("found_indices", [])),
        "message": str(step.get("message", f"Custom step {index}")),
        "variables": dict(step.get("variables", {})),
        "stats": dict(step.get("stats", {})),
    }

    stats = normalized["stats"]
    stats.setdefault("steps", index)
    stats.setdefault("comparisons", 0)
    stats.setdefault("swaps", 0)

    return normalized, None


def _validate_ast(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        return False, _format_error_message("FileError", str(e))

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        line = getattr(e, "lineno", None)
        code = _get_source_line(file_path, line) if line else ""
        return False, _format_error_message("SyntaxError", e.msg, line, code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_MODULE_PREFIXES:
                    code = _get_source_line(file_path, node.lineno)
                    return False, _format_error_message(
                        "SecurityError",
                        f"Forbidden import '{alias.name}'",
                        node.lineno,
                        code
                    )

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_MODULE_PREFIXES:
                    code = _get_source_line(file_path, node.lineno)
                    return False, _format_error_message(
                        "SecurityError",
                        f"Forbidden import '{node.module}'",
                        node.lineno,
                        code
                    )

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                code = _get_source_line(file_path, node.lineno)
                return False, _format_error_message(
                    "SecurityError",
                    f"Forbidden call '{node.func.id}()'",
                    node.lineno,
                    code
                )

    function_names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    if not any(name in function_names for name in SUPPORTED_ENTRYPOINTS):
        return False, (
            "ContractError: No supported entry function found. "
            "Use one of: run(data), get_states(data), visualize(data), algorithm(data)"
        )

    return True, "Python file looks valid."


def controlled_check(file_path: str):
    if not file_path:
        return False, "No file selected."

    if not os.path.exists(file_path):
        return False, "Selected file does not exist."

    if not file_path.lower().endswith(".py"):
        return False, "Selected file is not a Python file."

    return _validate_ast(file_path)


def _pick_entry_function(namespace):
    for name in SUPPORTED_ENTRYPOINTS:
        fn = namespace.get(name)
        if callable(fn):
            return name, fn
    return None, None


def _extract_meta(namespace):
    meta = {
        "overview": "Custom algorithm loaded.",
        "why": "Custom algorithm explanation not provided.",
        "best": "-",
        "average": "-",
        "worst": "-",
        "space": "-",
    }

    custom_meta = namespace.get("CUSTOM_META")
    if isinstance(custom_meta, dict):
        for key in meta:
            if key in custom_meta:
                meta[key] = str(custom_meta[key])

    get_meta = namespace.get("get_meta")
    if callable(get_meta):
        try:
            dynamic_meta = get_meta()
            if isinstance(dynamic_meta, dict):
                for key in meta:
                    if key in dynamic_meta:
                        meta[key] = str(dynamic_meta[key])
        except Exception:
            pass

    return meta


def _coerce_result_to_states(result, original_data):
    if isinstance(result, GeneratorType):
        result = list(result)

    if not isinstance(result, list):
        return False, {
            "message": (
                "Custom function must return a list (or generator) of state dicts. "
                "Example: [{'data': [...], 'message': 'step'}]"
            )
        }

    states = []
    prev = original_data[:]

    for idx, raw_step in enumerate(result, start=1):
        normalized, err = _normalize_state(raw_step, idx, prev)
        if err:
            return False, {"message": err}
        states.append(normalized)
        prev = normalized["data"][:]

    if not states:
        return False, {"message": "Custom function returned an empty state list."}

    return True, {"states": states}


def _sandbox_worker(file_path, data, queue):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        exec_globals = _build_exec_globals()
        exec(compile(source, file_path, "exec"), exec_globals)

        entry_name, entry_fn = _pick_entry_function(exec_globals)
        if entry_fn is None:
            queue.put((
                False,
                {
                    "message": (
                        "No supported entry function found after execution. "
                        "Use one of: run(data), get_states(data), visualize(data), algorithm(data)"
                    )
                }
            ))
            return

        result = entry_fn(data[:])
        ok, payload = _coerce_result_to_states(result, data[:])
        if not ok:
            queue.put((False, payload))
            return

        payload["meta"] = _extract_meta(exec_globals)
        payload["meta"]["overview"] = payload["meta"].get("overview") or f"Custom entry: {entry_name}"
        queue.put((True, payload))

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        user_frame = None

        for frame in reversed(tb):
            if os.path.abspath(frame.filename) == os.path.abspath(file_path):
                user_frame = frame
                break

        if user_frame:
            line = user_frame.lineno
            code = user_frame.line or _get_source_line(file_path, line)
        else:
            line = None
            code = ""

        queue.put((
            False,
            {
                "message": _format_error_message(type(e).__name__, str(e), line, code)
            }
        ))


def run_in_sandbox(file_path: str, data):
    ok, message = controlled_check(file_path)
    if not ok:
        return False, {"message": message}

    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(target=_sandbox_worker, args=(file_path, data[:], queue))
    process.start()
    process.join(TIMEOUT_SECONDS)

    if process.is_alive():
        process.terminate()
        process.join()
        return False, {
            "message": f"TimeoutError: Custom file exceeded {TIMEOUT_SECONDS} seconds. Possible infinite loop."
        }

    if not queue.empty():
        return queue.get()

    return False, {
        "message": "SandboxError: No result returned from custom process."
    }


# ============================================================
# DETAYLI ANALIZ - Test Broken penceresi icin
# ============================================================

def _analyze_ast_detailed(tree, file_path, analysis):
    """AST'yi detayli analiz et - undefined vars, import errors, security checks"""

    # Tum tanimli degiskenleri topla
    defined_vars = set(_safe_builtins().keys())
    defined_functions = set()
    import_names = set()

    # Top-level tanimlamalari topla
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            defined_functions.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_vars.add(target.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_names.add(alias.asname or alias.name.split(".")[0])
            elif node.module:
                for alias in node.names:
                    import_names.add(alias.asname or alias.name)

    # Fonksiyon isimleri de tanimli sayilir
    defined_vars.update(defined_functions)
    defined_vars.update(import_names)

    # Fonksiyon parametrelerini topla (her fonksiyon icin)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # Parametre isimleri
            local_vars = set()
            for arg in node.args.args:
                local_vars.add(arg.arg)

            # Fonksiyon icindeki atamalari topla
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            local_vars.add(target.id)
                elif isinstance(child, ast.For):
                    if isinstance(child.target, ast.Name):
                        local_vars.add(child.target.id)
                    elif isinstance(child.target, ast.Tuple):
                        for elt in child.target.elts:
                            if isinstance(elt, ast.Name):
                                local_vars.add(elt.id)

            # Undefined variable kontrolu
            func_scope = defined_vars | local_vars
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                    if child.id not in func_scope and not hasattr(builtins, child.id):
                        code = _get_source_line(file_path, child.lineno)
                        analysis["warnings"].append(
                            f"Line {child.lineno}: Possibly undefined '{child.id}' | Code: {code.strip()}"
                        )

    # Import hatalari
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_IMPORTS and root not in ("math", "random"):
                    code = _get_source_line(file_path, node.lineno)
                    analysis["errors"].append(
                        f"Line {node.lineno}: Import '{alias.name}' not allowed | Code: {code.strip()}"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    code = _get_source_line(file_path, node.lineno)
                    analysis["errors"].append(
                        f"Line {node.lineno}: Import '{node.module}' not allowed | Code: {code.strip()}"
                    )

    # Tehlikeli fonksiyon cagrilari
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                code = _get_source_line(file_path, node.lineno)
                analysis["errors"].append(
                    f"Line {node.lineno}: Forbidden call '{node.func.id}()' | Code: {code.strip()}"
                )

    return analysis


def analyze_python_file(file_path: str):
    """Detayli Python dosya analizi - Test Broken penceresi icin kullanilir"""
    analysis = {
        "errors": [],
        "warnings": [],
        "summary": "File looks good.",
    }

    # 1. Dosya okunabilir mi?
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        analysis["errors"].append(f"FileError: Cannot read file - {str(e)}")
        analysis["summary"] = "File cannot be read."
        return analysis

    # 2. Syntax hatasi var mi?
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        line = getattr(e, "lineno", None)
        code = _get_source_line(file_path, line) if line else ""
        analysis["errors"].append(
            f"SyntaxError at line {line}: {e.msg} | Code: {code.strip()}"
        )
        analysis["summary"] = f"Syntax error at line {line}"
        return analysis

    # 3. AST detayli kontrol (undefined vars, imports, security)
    analysis = _analyze_ast_detailed(tree, file_path, analysis)

    # 4. Entry function var mi?
    function_names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    if not any(name in function_names for name in SUPPORTED_ENTRYPOINTS):
        analysis["errors"].append(
            f"ContractError: No entry function found. "
            f"Use one of: {', '.join(SUPPORTED_ENTRYPOINTS)}"
        )

    # 5. Summary
    error_count = len(analysis["errors"])
    warning_count = len(analysis["warnings"])
    if error_count > 0:
        analysis["summary"] = f"{error_count} error(s), {warning_count} warning(s) found."
    elif warning_count > 0:
        analysis["summary"] = f"No errors, {warning_count} warning(s) found."
    else:
        analysis["summary"] = "File is valid and ready to execute."

    return analysis