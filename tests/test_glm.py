import io
import json
import tempfile
import threading
import time
import unittest
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from app import settings
from core import bigmodel, engine
from core.jev_client import JevError, ask
from core.providers import BIGMODEL_ENV, BIGMODEL_MODEL
from core.questions import JUDGE_QUESTIONS, build_rank_question
from core.session import Session


def answers_for(questions):
    answers = {}
    for name, spec in questions.items():
        kind = spec["type"]
        if kind == "noul":
            answers[name] = dict(type=kind, noul=0.7)
        else:
            keys = list(spec["criteria"]) if kind == "choice" else list(map(str, range(len(spec["criteria"]))))
            answers[name] = dict(type=kind, confidence=0.8,
                                 probabilities={k: float(i == 0) for i, k in enumerate(keys)})
            answers[name][kind] = keys[0] if kind == "choice" else 0
    return {"answers": answers}


def envelope(data):
    return dict(choices=[dict(message=dict(content=json.dumps(data)), finish_reason="stop")],
                usage={"prompt_tokens": 12, "completion_tokens": 8})


class ProtocolTests(unittest.TestCase):
    def test_three_stages_and_same_credential(self):
        candidates = ["好，三点见", "行，我提前到", "图书馆门口等你"]
        responses = [answers_for(JUDGE_QUESTIONS), {"replies": candidates},
                     answers_for(build_rank_question(candidates))]
        calls = []
        def post(payload, key, timeout):
            calls.append((payload, key))
            return envelope(responses.pop(0))
        with patch.object(bigmodel, "_post", post):
            result = engine.analyze([("her", "明天三点见？")], "friends",
                                    judge_api_key="synthetic-token", draft_api_key="synthetic-token")
        self.assertEqual(result["candidates"], candidates)
        self.assertEqual(len(result["answers"]), 8)
        self.assertEqual(result["scores"], [1, 0, 0])
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(k == "synthetic-token" for _, k in calls))
        self.assertTrue(all(p["model"] == BIGMODEL_MODEL for p, _ in calls))
        self.assertTrue(all(p["response_format"] == {"type": "json_object"} for p, _ in calls))
        self.assertIn("判断参考", calls[1][0]["messages"][1]["content"])

    def test_failure_stops_without_blind_draft(self):
        with patch.object(bigmodel, "_post", return_value=envelope({"answers": {}})) as post:
            with self.assertRaises(JevError):
                engine.analyze([("her", "你好")], "friends", judge_api_key="fake", draft_api_key="fake")
        self.assertEqual(post.call_count, 1)

    def test_missing_invalid_and_nonfinite_answers(self):
        for alteration in (lambda x: x["answers"].pop("she_needs"),
                           lambda x: x["answers"]["literal_question"].update(noul=True),
                           lambda x: x["answers"]["danger_level"].update(score=10),
                           lambda x: x["answers"]["best_action"].update(choice="unknown"),
                           lambda x: x["answers"]["best_action"].update(confidence=float("nan")),
                           lambda x: x["answers"]["best_action"].update(probabilities={})):
            data = answers_for(JUDGE_QUESTIONS)
            alteration(data)
            with self.subTest(data_type=str(alteration)), self.assertRaises(JevError):
                bigmodel.validate_answers(data, JUDGE_QUESTIONS)

    def test_bad_replies_rejected(self):
        for value in (["a"], ["a", "a", "b"], ["a", 2, "b"], ["", "a", "b"], "private text"):
            with self.subTest(value=value), self.assertRaises(JevError):
                bigmodel.replies({"replies": value})

    def test_no_fabricated_recommendation_on_rank_failure(self):
        responses = [envelope(answers_for(JUDGE_QUESTIONS)), envelope({"replies": ["甲", "乙", "丙"]}),
                     envelope({"answers": {}})]
        with patch.object(bigmodel, "_post", side_effect=responses), self.assertRaises(JevError):
            engine.analyze([("her", "您好")], "friends", judge_api_key="fake", draft_api_key="fake")

    def test_errors_do_not_echo_response(self):
        for raw in ("private chat and credential", '{"answers":', "[1,2,3]"):
            with patch.object(bigmodel, "_post", return_value={"choices": [{"message": {"content": raw}}]}):
                with self.assertRaises(JevError) as caught:
                    bigmodel.complete("system", "user", "fake")
                self.assertNotIn(raw, str(caught.exception))

    def test_401_once_429_three_attempts(self):
        for code, expected in ((401, 1), (403, 1), (429, 3), (500, 3), (302, 1)):
            def fail(*args):
                raise urllib.error.HTTPError("https://example.invalid", code, "private secret", {}, io.BytesIO(b"private"))
            with patch.object(bigmodel, "_post", side_effect=fail) as post, patch.object(bigmodel.time, "sleep"):
                with self.assertRaises(JevError) as caught:
                    bigmodel.complete("s", "u", "fake")
            self.assertEqual(post.call_count, expected)
            self.assertNotIn("private", str(caught.exception))

    def test_requests_are_serialized(self):
        active = peak = 0
        counter = threading.Lock()
        def post(*args):
            nonlocal active, peak
            with counter:
                active += 1
                peak = max(peak, active)
            time.sleep(0.02)
            with counter:
                active -= 1
            return envelope({"ok": True})
        with patch.object(bigmodel, "_post", post), ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(bigmodel.complete, "s", "u", "fake") for _ in range(4)]
            for future in futures:
                future.result()
        self.assertEqual(peak, 1)

    def test_snapshot_controls_all_model_configuration(self):
        config = dict(relationship="friends", provider="zhipu", jev_provider="zhipu",
                      judge_api_key="one", draft_api_key="one", style="自然简短")
        with (patch.object(engine, "ask", return_value=answers_for(JUDGE_QUESTIONS)) as judge,
              patch.object(engine, "draft_candidates", side_effect=JevError("stop"))):
            with self.assertRaises(JevError):
                engine.analyze([], "ignored", request_config=config)
        self.assertEqual(judge.call_args.kwargs["api_key"], "one")
        self.assertNotIn("request_config", config)


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "config.json"
        self.path_patch = patch.object(settings, "_CONFIG", self.path)
        self.path_patch.start()
        self.values = {"JEV_API_KEY": "old-judge", "LLM_API_KEY": "old-draft"}
        self.read_patch = patch.object(settings, "_read_env", side_effect=lambda name: self.values.get(name, ""))
        self.write_patch = patch.object(settings, "_set_key", side_effect=lambda name, value: self.values.update({name: value}))
        self.read_patch.start()
        self.write_patch.start()

    def tearDown(self):
        self.write_patch.stop()
        self.read_patch.stop()
        self.path_patch.stop()
        self.temp.cleanup()

    def test_new_install_never_borrows_old_credentials(self):
        self.assertEqual(settings.jev_provider(), "zhipu")
        self.assertEqual(settings.draft_provider(), "zhipu")
        self.assertFalse(settings.has_jev_key())
        self.assertFalse(settings.has_llm_key())

    def test_single_key_persisted_outside_json(self):
        settings.save(jev_key_text="new-zhipu")
        self.assertEqual(settings.jev_key(), "new-zhipu")
        self.assertEqual(settings.llm_key(), "new-zhipu")
        self.assertEqual(self.values["JEV_API_KEY"], "old-judge")
        self.assertEqual(self.values["LLM_API_KEY"], "old-draft")
        self.assertNotIn("new-zhipu", self.path.read_text(encoding="utf-8"))
        self.assertNotIn("API_KEY", self.path.read_text(encoding="utf-8"))

    def test_legacy_implicit_defaults_preserved_on_save(self):
        self.path.write_text('{"relationship":"friends","context":14}', encoding="utf-8")
        self.assertEqual(settings.jev_provider(), "openrouter")
        self.assertEqual(settings.draft_provider(), "deepseek")
        settings.save(debug_view_on=True)
        self.assertEqual(settings.jev_provider(), "openrouter")
        self.assertEqual(settings.relationship(), "friends")
        self.assertEqual(settings.context(), 14)

    def test_cross_provider_form_key_is_empty(self):
        self.path.write_text('{"jev_provider":"openrouter","draft_provider":"deepseek"}', encoding="utf-8")
        self.assertEqual(settings.key_for("jev", "typesafe"), "")
        self.assertEqual(settings.key_for("draft", "zhipu"), "")
        self.assertEqual(settings.key_for("draft", "openrouter"), "")
        self.assertEqual(settings.key_for("draft", "deepseek"), "old-draft")

    def test_upstream_update_disabled_even_old_flag_enabled(self):
        self.path.write_text('{"check_update":true}', encoding="utf-8")
        self.assertFalse(settings.check_update())


class SessionTests(unittest.TestCase):
    def test_chat_target_message_and_config_invalidate_results(self):
        session = Session()
        ticket = session.ticket("群聊", 1, "甲")
        self.assertTrue(session.accepts(ticket, "群聊", 1, "甲"))
        for args in (("其他", 1, "甲"), ("群聊", 2, "甲"), ("群聊", 1, "乙")):
            self.assertFalse(session.accepts(ticket, *args))
        session.invalidate()
        self.assertFalse(session.accepts(ticket, "群聊", 1, "甲"))


if __name__ == "__main__":
    unittest.main()
