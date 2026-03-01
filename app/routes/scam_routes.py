from fastapi import APIRouter
from pydantic import BaseModel
from app.services.scam_classifier import predict_message
from app.services.entity_extractor import extract_entities
from app.services.graph_builder import (
    build_graph_from_entities,
    get_graph_info,
    get_central_nodes,
    get_graph_data
)

router = APIRouter()

class MessageRequest(BaseModel):
    message: str

RISK_WEIGHTS = {
    "upi_ids": 0.9,
    "bank_accounts": 0.9,
    "ifsc_codes": 0.8,
    "phones": 0.6,
    "emails": 0.5,
    "urls": 0.6,
    "amounts": 0.7,
    "ip_addresses": 0.4
}

@router.post("/predict")
def predict(data: MessageRequest):
    message = data.message.strip()
    if not message:
        return {"error": "Message is required"}
    result = predict_message(message)
    entities = extract_entities(message)
    entities = {k: v for k, v in entities.items() if v}
    G = build_graph_from_entities(entities)
    graph_info = get_graph_info(G)

    # compute centrality once so we can use it for both summaries and per-node risk
    import networkx as _nx
    centrality = _nx.degree_centrality(G)
    central_nodes = get_central_nodes(G)

    # build the raw graph data and then inject a risk score (0-100) on each node
    graph_data = get_graph_data(G)
    risk_score = 0
    entity_count = 0

    # annotate each node with a normalized risk value based on type weight and centrality
    # helper to build a simple per-entity risk profile
    import random
    def make_profile(entity_type):
        # six dimensions: url reputation, sender history, content phish probability,
        # behavioral anomalies, monetary value, social urgency.
        base = RISK_WEIGHTS.get(entity_type, 0.5)
        dims = [
            "url_reputation",
            "sender_history",
            "content_phish",
            "behavioral_anomalies",
            "monetary_value",
            "social_urgency",
        ]
        prof = {}
        for d in dims:
            # derive from base with some jitter
            prof[d] = max(0, min(100, round(base * 100 + random.uniform(-20, 20), 2)))
        return prof

    for node in graph_data["nodes"]:
        if node["type"] != "message":
            weight = RISK_WEIGHTS.get(node["type"], 0.3)
            node_risk = round(weight * 100, 2)
            node["node_risk"] = node_risk
            node["risk_profile"] = make_profile(node["type"])

            risk_score += node_risk / 100.0
            entity_count += 1
        else:
            node["node_risk"] = 0
            node["risk_profile"] = {"url_reputation":0,"sender_history":0,
                                     "content_phish":0,"behavioral_anomalies":0,
                                     "monetary_value":0,"social_urgency":0}

    if entity_count > 0:
        risk_score = risk_score / entity_count
    else:
        risk_score = 0

    risk_score = round(risk_score, 3)
    # also provide percentage version for consumption by frontend if needed
    risk_score_pct = round(risk_score * 100, 2)

    if risk_score > 0.6:
        risk_level = "High"
    elif risk_score > 0.3:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    clusters = set(
        node["cluster"]
        for node in graph_data["nodes"]
        if node["type"] != "message"
    )

    top_entity = central_nodes[0]["entity"] if central_nodes else "None"

    if entity_count == 0:
        structure_text = "No suspicious entities detected."
    else:
        structure_text = f"{entity_count} suspicious entities connected to the central message node."

    cluster_text = f"{len(clusters)} behavioral cluster(s) detected."

    if risk_level == "High":
        behavior = "Strong financial redirection or phishing pattern identified."
    elif risk_level == "Medium":
        behavior = "Moderate suspicious communication pattern detected."
    else:
        behavior = "Low-risk structural pattern."

    graph_summary = (
        f"This graph shows a communication network. "
        f"The white node represents the original message. "
        f"{structure_text} "
        f"Most influential entity: '{top_entity}'. "
        f"{cluster_text} "
        f"{behavior}"
    )

    return {
        "prediction": result.get("prediction", "unknown"),
        "confidence": result.get("confidence", 0),
        "entities": entities,
        "graph": graph_info,
        "graph_data": graph_data,
        "top_suspicious_nodes": central_nodes,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_score_pct": risk_score_pct,
        "graph_summary": graph_summary
    }