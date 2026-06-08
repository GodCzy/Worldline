from src.services.theme_module_contract import normalize_theme_payload


def test_theme_module_payload_preserves_knowledge_and_generation_contract():
    theme = normalize_theme_payload(
        {
            "id": "product-requirements",
            "name": "需求知识库世界线",
            "db_id": "kb_product_requirements",
            "knowledge_name": "产品需求知识库",
            "knowledge_type": "milvus",
            "knowledge_description": "PRD and research notes.",
            "objective": "生成可审查的需求分支。",
            "evidence_sources": ["PRD", "interview", "wiki"],
            "default_question": "哪些需求已经有证据支持？",
            "worldline": {
                "surfaces": {
                    "wiki": True,
                    "graph": True,
                    "timeline": False,
                    "quality_gate": True,
                    "mcp": False,
                    "workflow": True,
                },
                "generation": {
                    "mode": "focused",
                    "branch_budget": 5,
                    "quality_profile": "strict",
                },
                "capability_map": {"version": "worldline-capability-map-v1"},
            },
        }
    )

    assert theme["id"] == "product-requirements"
    assert theme["knowledge"]["knowledge_db_id"] == "kb_product_requirements"
    assert theme["knowledge"]["name"] == "产品需求知识库"
    assert theme["knowledge"]["kb_type"] == "milvus"
    assert theme["context"]["objective"] == "生成可审查的需求分支。"
    assert theme["context"]["evidence_sources"] == ["PRD", "interview", "wiki"]
    assert theme["worldline"]["generation"]["mode"] == "focused"
    assert theme["worldline"]["generation"]["branch_budget"] == 5
    assert theme["worldline"]["surfaces"]["timeline"] is False
    assert theme["worldline"]["surfaces"]["mcp"] is False
    assert theme["worldline"]["surfaces"]["workflow"] is True
    assert theme["worldline"]["capability_map"]["theme_id"] == theme["id"]
    assert theme["worldline"]["capability_map"]["db_id"] == "kb_product_requirements"
    assert theme["metadata"]["knowledge_name"] == "产品需求知识库"


def test_theme_module_payload_keeps_legacy_shape_defaults():
    theme = normalize_theme_payload(
        {
            "id": "legacy-module",
            "name": "Legacy Module",
            "context": {"knowledge_db_id": "kb_legacy"},
            "worldline": {"surfaces": {"graph": False}},
        },
        fixed_id="legacy-module",
    )

    assert theme["id"] == "legacy-module"
    assert theme["context"]["knowledge_db_id"] == "kb_legacy"
    assert theme["worldline"]["surfaces"]["wiki"] is True
    assert theme["worldline"]["surfaces"]["graph"] is False
    assert theme["worldline"]["surfaces"]["timeline"] is True
    assert theme["worldline"]["surfaces"]["quality_gate"] is True
    assert theme["worldline"]["surfaces"]["mcp"] is True
    assert theme["worldline"]["surfaces"]["workflow"] is True
