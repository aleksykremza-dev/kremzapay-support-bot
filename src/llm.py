# Copyright (c) 2026 Oleksii Kremza. Licensed under PolyForm Noncommercial 1.0.0, see LICENSE.
import json
import logging
import time

import httpx

import config

log = logging.getLogger(__name__)


class LLMUnavailable(Exception):
    pass


class LLMBadOutput(Exception):
    pass


def generate(prompt: str, num_predict: int, json_mode: bool = False) -> str:
    body = {
        "model": config.ANSWER_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "num_predict": num_predict},
    }
    if json_mode:
        body["format"] = "json"
    last_error = None
    for attempt in range(1, config.LLM_RETRIES + 2):
        started = time.monotonic()
        try:
            response = httpx.post(config.OLLAMA_URL + "/api/generate", json=body,
                                  timeout=config.LLM_TIMEOUT_S)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            log.warning("ollama %s attempt %d failed: %s", config.OLLAMA_URL, attempt, exc)
            continue
        text = str(payload.get("response", "")).strip()
        log.info("ollama %s prompt=%d chars answer=%d chars %.1fs",
                 config.ANSWER_MODEL, len(prompt), len(text), time.monotonic() - started)
        if not text:
            raise LLMBadOutput("empty response")
        return text
    raise LLMUnavailable(f"{config.OLLAMA_URL}: {last_error}") from last_error


def generate_json(prompt: str, num_predict: int) -> dict:
    text = generate(prompt, num_predict, json_mode=True)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMBadOutput(text[:200]) from exc
    if not isinstance(data, dict):
        raise LLMBadOutput(text[:200])
    return data


def ping() -> bool:
    try:
        response = httpx.get(config.OLLAMA_URL + "/api/tags", timeout=config.PING_TIMEOUT_S)
    except httpx.HTTPError as exc:
        log.warning("ollama %s not reachable: %s", config.OLLAMA_URL, exc)
        return False
    return response.status_code == 200
