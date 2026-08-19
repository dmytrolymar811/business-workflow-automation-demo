# Business Workflow Automation Demo

A dependency-free Python example of a reliable event-driven business workflow. It validates incoming leads, enriches records, routes them by priority, retries transient failures, and writes an auditable execution log.

## Demonstrated practices

- explicit step contracts;
- input validation before side effects;
- retry policy for temporary failures;
- idempotency protection;
- structured execution history;
- clear separation between business rules and integrations;
- automated tests.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m workflow_automation.demo
python -m unittest discover -s tests -v
```

## Example flow

```text
web form -> validate -> normalize -> qualify -> CRM adapter -> notification adapter
```

The bundled adapters are safe in-memory demonstrations. Production deployments can connect the same interfaces to Gmail, Google Sheets, a CRM, n8n, Make, Zapier, APIs, or webhooks after credentials and technical feasibility are confirmed.

## License

MIT
