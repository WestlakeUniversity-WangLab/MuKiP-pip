"""
Language server for MuKiP setup files (.mukip).

This module is the standalone port of the language-server portion of
MuKiP-Visual (its `--server` mode / `server.py`). Previously the VSCode
extension launched MuKiP-Visual just to talk to this server; now the server is
bundled directly into the `mukip` PyPI package, so the VSCode extension only
needs a Python environment with `mukip` installed.

Protocol (JSON lines over stdin/stdout, one message per line):
  request:  {"id": <number>, "type": "validate"|"complete"|"hover", ...}
  response: {"id": <number>, "result": {...}}

Supported request types:
  - validate: parse the document and report diagnostics (syntax + component rules)
  - complete: return field-name completions at a position
  - hover:    return the tooltip for a field at a position

All MuKiP-specific work (JSON5 parsing, component pattern validation,
completion generation) is delegated to the MuKiP engine through JPype. Debug
logs are written to stderr so they never corrupt the stdout JSON channel.
"""

import json
import sys
from typing import Any, Dict, List

from . import lang as lang_module
from .jvm_manager import get_class

# MuKiP classes, resolved lazily once the JVM is up.
_MKM = None
_JSON5 = None
_PATTERN_EXCEPTION = None
_PATTERN_EXCEPTION_LIST = None


def _ensure_java():
    """Start the JVM (if needed) and resolve the MuKiP classes + texts."""
    global _MKM, _JSON5, _PATTERN_EXCEPTION, _PATTERN_EXCEPTION_LIST
    if _MKM is not None:
        return

    # get_class() starts the JVM and initializes MuKiP components on first use.
    _MKM = get_class("com.wang_lab.mukip.components.model.KineticModel").class_.getField("Companion").get(None)
    _JSON5 = get_class("com.wang_lab.mukip.misc.json5.Json5")
    _PATTERN_EXCEPTION = get_class(
        "com.wang_lab.mukip.misc.input_pattern.pattern_exception.PatternException").class_
    _PATTERN_EXCEPTION_LIST = get_class(
        "com.wang_lab.mukip.misc.input_pattern.pattern_exception.PatternExceptionList").class_


class Server:
    """A JSON-lines language server backed by the MuKiP engine."""

    def __init__(self, lang: str = "en_us"):
        self.lang = lang
        self.analysis = None
        self.key_range = None
        self.error = None
        self.element = None
        self.text = ""
        self.text_hash = 0
        self.text_lengths = []

    def start(self):
        _ensure_java()
        # Load the requested language's texts (tooltips etc.) from MuKiP.
        lang_module.lang.data = {}
        lang_module.lang.load_from_mukip(self.lang)

        def update_internal_state(text: str):
            h = hash(text)
            if h == self.text_hash:
                return
            self.text = text
            self.text_lengths = [len(t) for t in self.text.splitlines(keepends=True)]
            try:
                self.analysis = _JSON5.parseToJson5ElementAndRanges(self.text)
                self.key_range = self.analysis.getFirst()
                self.element = _JSON5.parseToJson5Element(self.text)
                self.error = None
            except Exception as je:
                self.error = je
            self.text_hash = h

        def get_pos(offset: int) -> dict:
            i = 0
            length = offset
            while True:
                if length < self.text_lengths[i]:
                    return {"line": i, "character": length}
                length -= self.text_lengths[i]
                i += 1

        def get_offset(pos: dict) -> int:
            line = pos["line"]
            char = pos["character"]
            for i in range(line):
                char += self.text_lengths[i]
            return char

        def get_diagnostics() -> List[Dict]:
            diagnostics = []
            if self.error:
                # Locate the parse error if the exception exposes a position;
                # otherwise fall back to the start of the document.
                try:
                    pos = get_pos(int(self.error.getIndex()))
                except Exception:
                    pos = {"line": 0, "character": 0}
                try:
                    message = str(self.error.getMessage())
                except Exception:
                    message = str(self.error)
                diagnostics.append({
                    "range": {"start": pos, "end": pos},
                    "message": message,
                    "severity": 0
                })
            if self.analysis:
                for duplicate_info in self.analysis.getSecond():
                    duplicate_range = duplicate_info.getSecond()
                    diagnostics.append({
                        "range": {"start": get_pos(int(duplicate_range.getStart())),
                                  "end": get_pos(int(duplicate_range.getEnd()))},
                        "message": "Duplicate key",
                        "severity": 1
                    })
            if self.element:
                try:
                    # genClass(j, keyName) - JPype cannot use Kotlin default args,
                    # so pass the optional keyName explicitly as None.
                    _MKM.genClass(self.element, None)
                except Exception as e:
                    errors = []
                    if e.__class__ == _PATTERN_EXCEPTION:
                        errors.append(e)
                    elif e.__class__ == _PATTERN_EXCEPTION_LIST:
                        for error in e.getExceptions():
                            errors.append(error)
                    for error in errors:
                        error_range = self.key_range.get(error.getPath())
                        if error_range:
                            diagnostics.append({
                                "range": {"start": get_pos(int(error_range.getStart())),
                                          "end": get_pos(int(error_range.getEnd()))},
                                "message": str(error.getMessage()),
                                "severity": 1
                            })
            return diagnostics

        def get_key_path_at_position(offset: int) -> str:
            if self.key_range:
                for key_path, source_range in dict(self.key_range).items():
                    if int(source_range.getStart()) <= offset <= int(source_range.getEnd()):
                        return str(key_path)
            return ""

        def get_completions(key_path: str) -> List[Dict]:
            try:
                completions = _MKM.getPattern().getCompletion(key_path, self.element)
                if completions:
                    return json.loads(str(completions.toString()))
                return []
            except Exception as e:
                print(f"[mukip.server] completion ERROR: {e}", file=sys.stderr)
                return []

        def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
            req_type = request.get("type")
            position = request.get("position")
            text = request.get("text", "")

            if req_type == "validate":
                update_internal_state(text)
                return {"diagnostics": get_diagnostics()}

            if req_type == "complete":
                if not position:
                    return {"items": []}
                update_internal_state(text)
                key_path = get_key_path_at_position(get_offset(position))
                items = get_completions(key_path)
                return {"items": items}

            if req_type == "hover":
                if not position:
                    return {"contents": []}
                update_internal_state(text)
                key_path = get_key_path_at_position(get_offset(position))
                cp = _MKM.getPattern().getClassPath(key_path, self.element)
                if cp is None:
                    return {"contents": []}
                class_path = str(cp.getSecond())
                if class_path:
                    tooltip = lang_module.lang.getTooltip(class_path)
                    return {"contents": [tooltip] if tooltip else []}
                return {"contents": []}

            return {"error": f"Unknown request type: {req_type}"}

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            try:
                result = handle_request(req)
                response = {"id": req.get("id"), "result": result}
                sys.stdout.buffer.write((json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8'))
                sys.stdout.flush()
            except Exception as e:
                error_resp = {
                    "id": req.get("id") if 'req' in locals() else 0,
                    "result": {"error": str(e)}
                }
                sys.stdout.buffer.write((json.dumps(error_resp, ensure_ascii=False) + '\n').encode('utf-8'))
                sys.stdout.flush()

        sys.exit(0)


def main():
    """Console entry point: `mukip-server` or `python -m mukip.server`."""
    # Optional: `--lang <code>` to select MuKiP's bundled language.
    lang = "en_us"
    args = sys.argv[1:]
    if "--lang" in args:
        i = args.index("--lang")
        if i + 1 < len(args):
            lang = args[i + 1]
    Server(lang=lang).start()


if __name__ == "__main__":
    main()
