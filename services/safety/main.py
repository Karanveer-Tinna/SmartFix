"""
SmartFix Safety Engine Service — Exercise 4 (Enhanced with Llama Guard 3:1b)

Evaluates safety constraints using Meta's Llama Guard 3 (1B) via the local Ollama API.
Returns ALLOWED / WARNING / BLOCKED with required safety precautions and LOTO enforcement.
"""

import logging
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from services.safety.guardrails import guardrails_engine, GuardrailCheckResult
except ImportError:
    try:
        from guardrails import guardrails_engine, GuardrailCheckResult
    except ImportError:
        guardrails_engine = None

logger = logging.getLogger("smartfix.safety-service")

app = FastAPI(
    title="SmartFix Safety Engine Service",
    description="Enterprise AI Safety Service powered by Llama Guard 3 (1B) through Ollama API",
    version="0.5.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SafetyEvaluationRequest(BaseModel):
    equipment_id: str = Field(..., description="Target equipment ID (e.g., EQ-1023, HA-MICRO-01)")
    question: str = Field(..., description="Technician troubleshooting question text")
    equipment_data: dict[str, Any] = Field(default_factory=dict, description="Optional equipment metadata")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "smartfix-safety-engine",
        "safety_engine": "Llama-Guard-3:1B",
        "guardrails": "Llama-Guard-3-Active",
        "ollama_url": getattr(guardrails_engine, "ollama_url", "http://127.0.0.1:11434"),
        "model": getattr(guardrails_engine, "model", "llama-guard3:1b"),
    }


@app.post("/safety/guardrails/evaluate")
async def evaluate_guardrails(body: SafetyEvaluationRequest) -> dict[str, Any]:
    """
    Evaluates technician query and context across the 5 SmartFix Guardrails
    backed by Llama Guard 3 (1B) semantic safety classification.
    """
    eq_id = body.equipment_id.upper()
    eq_name = body.equipment_data.get("name", eq_id)
    context = f"Equipment ID: {eq_id} ({eq_name})"

    g1 = await guardrails_engine.async_evaluate_llama_guard(
        query=body.question,
        guardrail_name="Guardrail 1: Safety Circuit Breaker (Llama Guard 3:1b)",
        equipment_context=context,
        fallback_decision="BLOCKED",
    )
    g2 = await guardrails_engine.async_evaluate_llama_guard(
        query=body.question,
        guardrail_name="Guardrail 2: Prompt Injection Defense (Llama Guard 3:1b)",
        equipment_context="Security Boundary: Maintenance Diagnostics Only",
        fallback_decision="INTERCEPTED",
    )
    g3 = guardrails_engine.check_code_sandbox_security(body.question)
    g4 = guardrails_engine.check_hallucination_grounding(body.question, [])
    g5 = guardrails_engine.check_output_schema({
        "decision": g1.decision,
        "warnings": g1.warnings,
        "required_precautions": ["Mandatory Lockout/Tagout (LOTO)"],
    })

    all_checks = [g1, g2, g3, g4, g5]
    any_blocked = any(not g.passed for g in all_checks)

    return {
        "equipment_id": eq_id,
        "overall_decision": "BLOCKED" if any_blocked else "ALLOWED",
        "guardrail_checks": [g.model_dump() for g in all_checks],
        "evaluator": "SmartFix Enterprise Guardrails Suite (Llama Guard 3:1b)",
    }


@app.post("/safety/evaluate")
async def evaluate_safety(body: SafetyEvaluationRequest) -> dict[str, Any]:
    """
    Evaluates equipment safety using Llama Guard 3:1b through Ollama API.
    Determines if query constitutes a BLOCKED lethal hazard, a WARNING requiring precautions,
    or an ALLOWED standard operation.
    """
    eq_id = body.equipment_id.upper()
    q_lower = body.question.lower()
    eq_name = body.equipment_data.get("name", eq_id)
    eq_category = body.equipment_data.get("category", "")
    equipment_context = f"Equipment: {eq_name} [{eq_id}] | Category: {eq_category}"

    # Query Llama Guard 3:1b
    res = await guardrails_engine.async_evaluate_llama_guard(
        query=body.question,
        guardrail_name="Llama Guard 3 Circuit Breaker",
        equipment_context=equipment_context,
        fallback_decision="BLOCKED",
    )

    warnings = list(res.warnings)
    rules_triggered = list(res.violation_categories)
    required_precautions: list[str] = []

    if not res.passed:
        # Llama Guard 3 flagged unsafe operation -> BLOCKED
        decision = "BLOCKED"
        rules_triggered.append("LLAMA-GUARD-01: Lethal Operational Hazard Intercepted")
        required_precautions.extend([
            "Perform main breaker Lockout/Tagout (LOTO) before opening equipment casing.",
            "Verify Zero Energy State with a calibrated multimeter before touching internal terminals.",
            "Never bypass safety door interlocks, thermal cutoffs, or ground fault protections.",
        ])

        if any(w in q_lower for w in ["capacitor", "microwave", "ha-micro-01"]):
            required_precautions.append(
                "Discharge high-voltage capacitor (>2,000V DC) using a 20k-Ohm 20W insulated HV probe."
            )
        if any(w in q_lower for w in ["conveyor", "belt", "spin", "drum", "ha-wash-04", "eq-2045"]):
            required_precautions.append(
                "Press Emergency Stop (E-STOP) and confirm drive motor has completely stopped before servicing."
            )
        if any(w in q_lower for w in ["toaster", "ha-toast-02"]):
            required_precautions.append(
                "Unplug appliance from AC socket immediately; never insert conductive metal utensils into live slots."
            )

    else:
        # Check for non-lethal caution / warning conditions (thermal surfaces, hydraulic pressures)
        is_warning = any(
            w in q_lower
            for w in [
                "heating element", "hot surface", "temperature", "thermal", "burner",
                "pressure", "hydraulic", "degreaser", "grease", "drain pump"
            ]
        ) or eq_id in ["HA-TOAST-02", "HA-AIRFRY-03", "HA-OVEN-05", "EQ-1023"]

        if is_warning:
            decision = "WARNING"
            rules_triggered.append("LLAMA-GUARD-WARN: Elevated Operational Caution Required")
            warnings.append("WARNING: Operation involves hot surfaces, mechanical tension, or pressurized fluid lines.")
            required_precautions.extend([
                "Ensure appliance is disconnected from mains AC power before disassembly or cleaning.",
                "Allow thermal components to cool down completely (minimum 30–45 minutes).",
                "Wear heat-resistant safety gloves and safety eye protection.",
                "Verify hydraulic line pressure reads 0 bar before loosening fittings.",
            ])
        else:
            decision = "ALLOWED"
            required_precautions.append(
                "Follow standard operating maintenance protocols and ensure equipment is powered down before servicing."
            )

    return {
        "equipment_id": eq_id,
        "decision": decision,
        "warnings": warnings,
        "rules_triggered": rules_triggered,
        "required_precautions": required_precautions,
        "evaluated_by": "Llama Guard 3:1b via Ollama API",
        "llama_guard_result": {
            "passed": res.passed,
            "categories": res.violation_categories,
            "raw_response": res.raw_model_response,
        },
    }
