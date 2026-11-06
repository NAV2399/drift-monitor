"""Event contract: converts one raw PaySim row into our clean event."""


def to_clean_event(raw):
    """Rename PaySim fields into our event contract."""
    return {
        "step": int(raw["step"]),
        "transaction_type": str(raw["type"]),
        "amount": float(raw["amount"]),
        "origin_account": str(raw["nameOrig"]),
        "origin_balance_before": float(raw["oldbalanceOrg"]),
        "origin_balance_after": float(raw["newbalanceOrig"]),
        "destination_account": str(raw["nameDest"]),
        "destination_balance_before": float(raw["oldbalanceDest"]),
        "destination_balance_after": float(raw["newbalanceDest"]),
        "is_fraud": bool(raw["isFraud"]),
    }
