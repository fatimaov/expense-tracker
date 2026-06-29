from flask import Response, jsonify


def error_response(
    message: str,
    code: str,
    status_code: int,
) -> tuple[Response, int]:
    return jsonify(error={"message": message, "code": code}), status_code
