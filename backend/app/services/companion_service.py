import re

from ..services.transaction_evidence_service import TransactionEvidenceService


MAX_COMPANION_RECORDS = 25
RECORD_QUERY = re.compile(r"^find records matching\s*:\s*(.*)$", re.IGNORECASE)


class CompanionQuestionError(ValueError):
    pass


def _classify_question(question: str) -> tuple[str | None, str | None]:
    normalized = question.strip()
    matching = RECORD_QUERY.fullmatch(normalized)
    if matching:
        description = matching.group(1).strip()
        return ("matching", description) if description else (None, "Add a description after “Find records matching:”.")
    if re.match(r"^(find|show|list|search)\s+(me\s+)?(the\s+)?records?\b", normalized, re.IGNORECASE):
        return None, "Use the format “Find records matching: <description>” to find records."

    text = normalized.casefold()
    if any(term in text for term in ("afford", "should i", "how can i", "reduce", "cut back", "save more", "budget", "recommend", "invest", "compare")):
        return None, "I can answer transaction totals, category breakdowns, missing expense context, or supported record matches, but not provide advice or comparisons."
    if re.search(r"\b(on|for|at)\s+(food|groceries|transport|accommodation|activities|rent|coffee|shopping)\b", text):
        return None, "For a supported record subset, use “Find records matching: <description>”."
    if any(term in text for term in ("missing context", "missing optional context", "without context", "missing b/u/c", "missing reflective context", "untagged expenses")):
        return "missing_context", None
    if any(term in text for term in ("breakdown", "by category", "categories")):
        if any(term in text for term in ("income", "earned", "earnings")):
            return "income_categories", None
        if any(term in text for term in ("expense", "spending", "spent")):
            return "expense_categories", None
        return None, "Specify whether you want income or expense categories."
    if any(term in text for term in ("net amount", "net result", "net total", "what is my net", "what's my net", "my net", "net this month")):
        return "net", None
    asks_total = any(term in text for term in ("total", "how much", "amount of", "what did i"))
    if asks_total and any(term in text for term in ("income", "earned", "earnings")):
        return "income_total", None
    if asks_total and any(term in text for term in ("expense", "spending", "spent", "spend")):
        return "expense_total", None
    return None, "Ask about income, expenses, net amount, category breakdowns, missing expense context, or use the supported record-matching format."


def build_companion_evidence(user_id: int, scope: str, question: str, evidence_service=None) -> tuple[str | None, str | None, dict]:
    """Classify supported requests and construct only their minimum evidence."""
    intent, clarification = _classify_question(question)
    service = evidence_service or TransactionEvidenceService()
    if intent is None:
        base = service.build(user_id, scope)
        evidence = {key: base[key] for key in ("scope", "timezone", "period", "exclusions", "warnings")}
        return intent, clarification, evidence

    base = service.build(user_id, scope)
    common = {key: base[key] for key in ("scope", "timezone", "period", "exclusions", "warnings")}
    if intent in {"income_total", "expense_total", "net"}:
        key = {"income_total": "income", "expense_total": "expense", "net": "net"}[intent]
        return intent, None, {**common, "included_record_count": base["source_record_count"], "total": {key: base["totals"][key]}}
    if intent in {"income_categories", "expense_categories"}:
        transaction_type = intent.removesuffix("_categories").replace("_", " ")
        transaction_type = "income" if transaction_type == "income" else "expense"
        categories = [item for item in base["category_totals"] if item["transaction_type"] == transaction_type]
        return intent, None, {
            **common, "included_record_count": base["transaction_counts"][transaction_type],
            "transaction_type": transaction_type, "category_totals": categories,
        }
    if intent == "missing_context":
        records = sorted(base["expenses_missing_context"], key=lambda row: (row["transaction_date"], row["id"]), reverse=True)
        truncated = len(records) > MAX_COMPANION_RECORDS
        warnings = list(common["warnings"])
        if truncated:
            warnings.append("Only the 25 newest records missing context are included.")
        return intent, None, {
            **common,
            "included_record_count": len(records),
            "missing_context_count": len(records),
            "records": records[:MAX_COMPANION_RECORDS],
            "truncated": truncated,
            "warnings": warnings,
        }
    if intent == "matching":
        _, description = _classify_question(question)
        return intent, None, service.find_matching(user_id, scope, description, MAX_COMPANION_RECORDS)
    raise CompanionQuestionError("Unsupported Companion question.")


COMPANION_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["kind", "message", "missing_or_ambiguous_information"],
    "properties": {
        "kind": {"type": "string", "enum": ["answer", "clarification"]},
        "message": {"type": "string"},
        "missing_or_ambiguous_information": {"type": ["string", "null"]},
    },
}

COMPANION_SYSTEM_INSTRUCTIONS = (
    "Answer only the supported question using the supplied deterministic application evidence. "
    "Do not calculate or invent financial facts. Identify the supplied period and included evidence subset, "
    "and acknowledge applicable exclusions and warnings. Be concise and non-judgmental. "
    "Return kind=answer for a supported answer or clarification only if the supplied evidence cannot answer it. "
    "Never return a proposal or action. Return only the requested JSON object."
)


def validate_companion_response(response: object, evidence: dict) -> dict:
    if not isinstance(response, dict) or set(response) != {"kind", "message", "missing_or_ambiguous_information"}:
        raise ValueError("The Companion response did not match the supported answer contract.")
    if response["kind"] not in {"answer", "clarification"}:
        raise ValueError("The Companion response kind is not supported.")
    message = response["message"]
    missing = response["missing_or_ambiguous_information"]
    if not isinstance(message, str) or not message.strip() or len(message) > 4000:
        raise ValueError("The Companion response did not match the supported answer contract.")
    if missing is not None and (not isinstance(missing, str) or len(missing) > 1000):
        raise ValueError("The Companion response did not match the supported answer contract.")
    if response["kind"] == "clarification" and not missing:
        raise ValueError("The Companion clarification is incomplete.")
    if response["kind"] == "answer" and missing is not None:
        raise ValueError("The Companion answer contains clarification-only fields.")
    return {
        "kind": response["kind"],
        "message": message.strip(),
        "missing_or_ambiguous_information": missing,
        "evidence": evidence,
    }
