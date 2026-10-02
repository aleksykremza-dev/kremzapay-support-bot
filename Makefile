PY = uv run python
REPORTS = data/reports

.PHONY: test test-func test-oos test-accuracy test-load test-stress test-stability test-all codemap ingest coverage

test:
	uv run pytest -q

test-func:
	$(PY) tests/live/func_by_category.py

test-oos:
	$(PY) tests/live/out_of_scope.py

test-accuracy:
	$(PY) src/eval_cascade.py

test-load:
	$(PY) tests/live/load.py

test-stress:
	$(PY) tests/live/stress.py

test-stability:
	$(PY) tests/live/stability.py --minutes 60

test-all: test test-func test-oos test-accuracy test-load test-stress
	@echo "ALL TESTS PASSED"

codemap:
	$(PY) tools/codemap.py --out $(REPORTS)/codemap.json

coverage:
	$(PY) tools/question_coverage.py

ingest:
	$(PY) src/ingest.py
