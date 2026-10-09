from flask import Response, jsonify


def error_response(
    message: str,
    code: str,
    status_code: int,
    fields: dict[str, str] | None = None,
) -> tuple[Response, int]:
    error = {"message": message, "code": code}
    if fields:
        error["fields"] = fields
    return jsonify(error=error), status_code
