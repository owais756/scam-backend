from fastapi import APIRouter
from app.services.scam_classifier import predict_message
from app.services.entity_extractor import extract_entities
from app.services.graph_builder import (
    build_graph_from_entities,
    get_graph_info,
    get_central_nodes,
    get_graph_data
)

router = APIRouter()


# 🔥 Risk weight by entity type
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
def predict(data: dict):
    message = data.get("message", "").strip()

    if not message:
        return {"error": "Message is required"}

    # 1️⃣ ML prediction
    result = predict_message(message)

    # 2️⃣ Extract entities
    entities = extract_entities(message)
    entities = {k: v for k, v in entities.items() if v}

    # 3️⃣ Build graph
    G = build_graph_from_entities(entities)
    graph_info = get_graph_info(G)
    central_nodes = get_central_nodes(G)
    graph_data = get_graph_data(G)

    # 4️⃣ Risk Score (Weighted + Centrality Based)

    risk_score = 0
    entity_count = 0

    for node in graph_data["nodes"]:
        if node["type"] != "message":
            weight = RISK_WEIGHTS.get(node["type"], 0.3)
            risk_score += weight * node["centrality_score"]
            entity_count += 1

    if entity_count > 0:
        risk_score = risk_score / entity_count
    else:
        risk_score = 0

    risk_score = round(risk_score, 3)

    if risk_score > 0.6:
        risk_level = "High"
    elif risk_score > 0.3:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # 5️⃣ Graph Meaning (REAL INTERPRETATION)

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
        f"This graph shows a star-shaped communication network. "
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
        "graph_summary": graph_summary
    }