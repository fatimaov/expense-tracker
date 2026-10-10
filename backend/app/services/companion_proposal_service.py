from decimal import Decimal

from .transaction_evidence_service import EvidenceSelectionError, TransactionEvidenceService
from .transaction_service import (
    TransactionForbiddenError,
    TransactionNotFoundError,
    _validate_transaction_payload,
    get_transaction,
    serialize_created_transaction,
)


PROPOSAL_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["kind", "message", "missing_or_ambiguous_information"],
    "properties": {
        "kind": {"type": "string", "enum": ["answer", "clarification", "proposal"]},
        "message": {"type": "string"},
        "missing_or_ambiguous_information": {"type": ["string", "null"]},
        "proposal": {
            "type": "object",
            "additionalProperties": False,
            "required": ["operation", "target_transaction_id", "affected_fields", "proposed_values", "uncertainty"],
            "properties": {
                "operation": {"type": "string", "enum": ["edit_transaction", "soft_delete_transaction", "change_transaction_context"]},
                "target_transaction_id": {"type": "integer", "minimum": 1},
                "affected_fields": {"type": "array", "items": {"type": "string", "enum": ["amount", "transaction_date", "category_key", "notes", "b_u_c", "reflective_context"]}},
                "proposed_values": {"type": "object", "additionalProperties": {"type": ["string", "null"]}},
                "uncertainty": {"type": "string", "maxLength": 1000},
            },
        },
    },
}

PROPOSAL_SYSTEM_INSTRUCTIONS = (
    "Use only the supplied selected transaction and deterministic evidence. The user selected this one target; "
    "never select or identify another record. Return an answer or clarification for non-action requests. "
    "For a supported explicit request, prepare exactly one proposal using edit_transaction, "
    "soft_delete_transaction, or change_transaction_context. Do not combine operations. "
    "edit_transaction may change only amount, transaction_date, category_key, and/or notes. "
    "change_transaction_context is expense-only and may change only b_u_c and/or reflective_context; "
    "use null to clear a context value. Never change transaction_type. Return only the requested JSON object. "
    "Do not calculate expected effects or provide replacement evidence."
)


class TargetTransactionUnavailable(ValueError):
    """The selected target cannot safely be used in this request's scope."""


class StaleProposalVersion(ValueError):
    """The record changed after the proposal was prepared."""


def build_target_evidence(user_id: int, scope: str, target_id: int, evidence_service=None):
    service = evidence_service or TransactionEvidenceService()
    try:
        base = service.build(user_id, scope, selected_ids=[target_id])
    except EvidenceSelectionError as error:
        raise TargetTransactionUnavailable("The selected transaction is unavailable.") from error
    if base["exclusions"].get("outside_scope", 0):
        raise TargetTransactionUnavailable("The selected transaction is outside the requested scope.")
    try:
        transaction = get_transaction(target_id, user_id)
    except (TransactionForbiddenError, TransactionNotFoundError) as error:
        raise TargetTransactionUnavailable("The selected transaction is unavailable.") from error
    serialized = serialize_created_transaction(transaction)
    evidence = {
        "scope": base["scope"],
        "timezone": base["timezone"],
        "period": base["period"],
        "exclusions": base["exclusions"],
        "warnings": base["warnings"],
        "target_transaction": serialized,
    }
    return transaction, evidence


def validate_proposal_response(response: object, target, evidence: dict) -> dict:
    if not isinstance(response, dict):
        raise ValueError("The Companion response was not a JSON object.")
    kind = response.get("kind")
    common_keys = {"kind", "message", "missing_or_ambiguous_information"}
    if kind in {"answer", "clarification"}:
        if set(response) - common_keys:
            raise ValueError("The Companion response contains unsupported fields.")
        from .companion_service import validate_companion_response

        return validate_companion_response(response, evidence)

    if kind != "proposal" or set(response) != common_keys | {"proposal"}:
        raise ValueError("The Companion response kind is not supported.")
    message = response.get("message")
    missing = response.get("missing_or_ambiguous_information")
    if not isinstance(message, str) or not message.strip() or len(message) > 4000 or missing is not None:
        raise ValueError("The Companion proposal response is malformed.")
    raw = response["proposal"]
    proposal_keys = {"operation", "target_transaction_id", "affected_fields", "proposed_values", "uncertainty"}
    if not isinstance(raw, dict) or set(raw) != proposal_keys:
        raise ValueError("The Companion proposal is malformed.")
    operation = raw["operation"]
    if operation not in {"edit_transaction", "soft_delete_transaction", "change_transaction_context"}:
        raise ValueError("The proposal operation is not supported.")
    if type(raw["target_transaction_id"]) is not int or raw["target_transaction_id"] != target.id:
        raise ValueError("The proposal target does not match the selected transaction.")
    affected = raw["affected_fields"]
    proposed = raw["proposed_values"]
    if not isinstance(affected, list) or any(not isinstance(field, str) for field in affected):
        raise ValueError("The proposal fields are malformed.")
    if len(affected) != len(set(affected)) or not isinstance(proposed, dict) or set(affected) != set(proposed):
        raise ValueError("The proposal fields do not match its values.")
    uncertainty = raw["uncertainty"]
    if not isinstance(uncertainty, str) or not uncertainty.strip() or len(uncertainty) > 1000:
        raise ValueError("The proposal uncertainty is malformed.")

    edit_fields = {"amount", "transaction_date", "category_key", "notes"}
    context_fields = {"b_u_c", "reflective_context"}
    if operation == "edit_transaction":
        allowed = edit_fields
        if not affected:
            raise ValueError("An edit proposal must include at least one field.")
    elif operation == "change_transaction_context":
        allowed = context_fields
        if target.transaction_type != "expense" or not affected:
            raise ValueError("Expense context can only be proposed for an expense.")
    else:
        allowed = set()
        if affected or proposed:
            raise ValueError("A deletion proposal cannot change fields.")
    if set(affected) - allowed:
        raise ValueError("The proposal includes fields that are not supported for this operation.")

    current = serialize_created_transaction(target)
    validated_values = {}
    if operation == "edit_transaction":
        complete = {
            "transaction_type": target.transaction_type,
            "amount": proposed.get("amount", current["amount"]),
            "transaction_date": proposed.get("transaction_date", current["transaction_date"]),
            "category_key": proposed.get("category_key", current["category_key"]),
            "notes": proposed.get("notes", current["notes"] or ""),
            "b_u_c": current["b_u_c"],
            "reflective_context": current["reflective_context"],
        }
        validated = _validate_transaction_payload(complete)
        validated_values = dict(proposed)
        if "amount" in validated_values:
            validated_values["amount"] = format(validated["amount"], ".2f")
        if "transaction_date" in validated_values:
            validated_values["transaction_date"] = validated["transaction_date"].isoformat()
        if "category_key" in validated_values:
            validated_values["category_key"] = validated["category"].key
        if "notes" in validated_values:
            validated_values["notes"] = validated["notes"] or ""
    elif operation == "change_transaction_context":
        complete = {
            "transaction_type": target.transaction_type,
            "amount": current["amount"],
            "transaction_date": current["transaction_date"],
            "category_key": current["category_key"],
            "notes": current["notes"] or "",
            "b_u_c": proposed.get("b_u_c", current["b_u_c"]),
            "reflective_context": proposed.get("reflective_context", current["reflective_context"]),
        }
        _validate_transaction_payload(complete)
        validated_values = dict(proposed)

    effect = calculate_expected_effect(current, operation, validated_values)
    return {
        "kind": "proposal",
        "message": message.strip(),
        "missing_or_ambiguous_information": None,
        "evidence": evidence,
        "proposal": {
            "operation": operation,
            "target_transaction_id": target.id,
            "affected_fields": affected,
            "current_record": current,
            "proposed_values": validated_values,
            "uncertainty": uncertainty.strip(),
            "expected_effect": effect,
            "proposal_version": current["updated_at"],
        },
    }


def build_reviewed_proposal(user_id: int, scope: str, target_id: int, review: object, evidence_service=None) -> dict:
    """Revalidate user-edited proposal fields and refresh their deterministic preview."""
    if not isinstance(review, dict) or set(review) != {
        "operation", "affected_fields", "proposed_values", "proposal_version", "uncertainty",
    }:
        raise ValueError("The reviewed proposal is malformed.")
    target, evidence = build_target_evidence(user_id, scope, target_id, evidence_service)
    current = serialize_created_transaction(target)
    if review["proposal_version"] != current["updated_at"]:
        raise StaleProposalVersion("The selected transaction changed. Start a new Companion request.")
    if review["operation"] not in {"edit_transaction", "change_transaction_context"}:
        raise ValueError("Only edit and expense-context proposals can be edited.")
    response = {
        "kind": "proposal",
        "message": "Your edited proposal is ready for review.",
        "missing_or_ambiguous_information": None,
        "proposal": {
            "operation": review["operation"],
            "target_transaction_id": target_id,
            "affected_fields": review["affected_fields"],
            "proposed_values": review["proposed_values"],
            "uncertainty": review["uncertainty"],
        },
    }
    return validate_proposal_response(response, target, evidence)


def calculate_expected_effect(current: dict, operation: str, proposed: dict) -> dict:
    old_amount = Decimal(current["amount"])
    old_date = current["transaction_date"]
    old_category = current["category_key"]
    if operation == "soft_delete_transaction":
        new_record = None
    else:
        new_record = {**current, **proposed}
    new_category = new_record["category_key"] if new_record else None
    transaction_type = current["transaction_type"]

    contributions = {}

    def apply(month, category, amount, sign):
        entry = contributions.setdefault(month, {"income": Decimal("0"), "expense": Decimal("0"), "categories": {}})
        entry[transaction_type] += amount * sign
        entry["categories"][category] = entry["categories"].get(category, Decimal("0")) + amount * sign

    apply(old_date[:7], old_category, old_amount, Decimal("-1"))
    if new_record:
        apply(new_record["transaction_date"][:7], new_category, Decimal(new_record["amount"]), Decimal("1"))
    monthly = []
    for month, values in sorted(contributions.items()):
        income_delta = values["income"]
        expense_delta = values["expense"]
        monthly.append({
            "month": month,
            "income_delta": format(income_delta, ".2f"),
            "expense_delta": format(expense_delta, ".2f"),
            "net_delta": format(income_delta - expense_delta, ".2f"),
            "category_deltas": [
                {"category_key": key, "delta": format(delta, ".2f")}
                for key, delta in sorted(values["categories"].items()) if delta
            ],
        })

    changes_totals = operation == "soft_delete_transaction" or any(
        key in proposed for key in ("amount", "transaction_date")
    )
    changes_category = operation == "soft_delete_transaction" or old_category != new_category
    if changes_totals:
        return {"kind": "financial_change", "monthly_deltas": monthly}
    if changes_category:
        return {
            "kind": "category_reallocation",
            "monthly_deltas": monthly,
            "message": "Category totals are reallocated; overall income, expense, and net totals do not change.",
        }
    return {"kind": "no_financial_change", "message": "Income, expense, and net totals do not change."}
