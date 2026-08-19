import unittest

from workflow_automation import Pipeline, Step, TransientStepError


class PipelineTests(unittest.TestCase):
    def test_runs_steps_in_order(self) -> None:
        pipeline = Pipeline([
            Step("one", lambda state: {**state, "count": 1}),
            Step("two", lambda state: {**state, "count": state["count"] + 1}),
        ])
        result = pipeline.run({"id": 1})
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["workflow_status"], "completed")

    def test_skips_duplicate_payload(self) -> None:
        calls = []
        pipeline = Pipeline([Step("track", lambda state: calls.append(1) or state)])
        pipeline.run({"id": 1})
        result = pipeline.run({"id": 1})
        self.assertEqual(calls, [1])
        self.assertEqual(result["workflow_status"], "duplicate_skipped")

    def test_retries_transient_failure(self) -> None:
        attempts = []
        def flaky(state: dict) -> dict:
            attempts.append(1)
            if len(attempts) == 1:
                raise TransientStepError("temporary API failure")
            return {**state, "sent": True}
        result = Pipeline([Step("send", flaky, retries=1)]).run({"id": 1})
        self.assertTrue(result["sent"])
        self.assertEqual(len(attempts), 2)


if __name__ == "__main__":
    unittest.main()
