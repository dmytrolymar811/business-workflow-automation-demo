import json

from .pipeline import Pipeline, Step


def validate_lead(state: dict) -> dict:
    required = {"name", "email", "need"}
    missing = required - state.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
    if "@" not in state["email"]:
        raise ValueError("Invalid email address")
    return state


def normalize_lead(state: dict) -> dict:
    return {**state, "name": state["name"].strip().title(), "email": state["email"].strip().lower()}


def qualify_lead(state: dict) -> dict:
    text = state["need"].lower()
    priority = "high" if any(term in text for term in ("urgent", "automation", "integration")) else "normal"
    return {**state, "priority": priority}


def main() -> None:
    pipeline = Pipeline([
        Step("validate", validate_lead),
        Step("normalize", normalize_lead),
        Step("qualify", qualify_lead),
    ])
    result = pipeline.run({
        "name": "alex smith",
        "email": "Alex@Example.com",
        "need": "We need an urgent CRM integration and lead automation.",
    })
    print(json.dumps(result, indent=2))
    print(json.dumps([record.__dict__ for record in pipeline.history], indent=2))


if __name__ == "__main__":
    main()
