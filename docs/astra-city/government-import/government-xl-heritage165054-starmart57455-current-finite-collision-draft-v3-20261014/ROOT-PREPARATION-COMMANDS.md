# ROOT-only v3 preparation and validation schema

These are proposed commands; no execution is represented by this document. Use the Astra worktree as cwd. Keep logs in a new exclusive ROOT preparation directory and pin all contract.filePins plus caller/contract/review before and after. Never overwrite prior preparation or outputs.

```sh
HERITAGE_DRAFT=docs/astra-city/government-import/government-xl-heritage165054-starmart57455-current-finite-collision-draft-v3-20261014
HERITAGE_PREP="$HERITAGE_DRAFT/ROOT-actual-preparation-v1"
mkdir "$HERITAGE_PREP"
/tmp/astra-city-venv/bin/python -m unittest discover -s "$HERITAGE_DRAFT" -p test_exact_source_attribute_json_zero_sign_transport_v1.py -v > "$HERITAGE_PREP/tests.log" 2>&1
# Record real test exit immediately; require Ran 12 tests, exit0 and OK.
/tmp/astra-city-venv/bin/python -c 'import importlib.util,sys; from pathlib import Path; p=Path(sys.argv[1]); sys.path.insert(0,str(p.parent)); s=importlib.util.spec_from_file_location("heritage_collision_v3_import",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)' "$HERITAGE_DRAFT/heritage-starmart-current-finite-draft-v3.py" > "$HERITAGE_PREP/import.log" 2>&1
/tmp/astra-city-venv/bin/python "$HERITAGE_DRAFT/heritage-starmart-current-finite-draft-v3.py" --preflight-only > "$HERITAGE_PREP/preflight.log" 2>&1
```

ROOT saves truthful immutable validation only after actual12PASS/import0/preflight0 and all literal before/end pins agree. Exact caller-required validation JSON shape:

```json
{
  "allPassed": true,
  "exitCode": 0,
  "testCount": 12,
  "testedCodePins": {"<caller path>":"<actual current SHA>","<helper path>":"<actual current SHA>","<test path>":"<actual current SHA>"},
  "inputContractSHA256": "<actual final input-contract.json SHA>",
  "testLog": {"path":"<repository-relative immutable actual tests.log>","sha256":"<actual log SHA>"}
}
```

`testedCodePins` must equal input-contract.testedCodePins exactly; copy the literal map, not guessed paths or hashes. Actual run evidence should also include commands/exit codes and complete before/end literal pins, separate import/preflight log SHA, current/capture/pose hashes. No validation output is fabricated in this draft.

Only after ROOT accepts actual prep and obtains a fresh maintained exact4-resource lease, the reviewed supervisor invokes:

```sh
/tmp/astra-city-venv/bin/python "$HERITAGE_DRAFT/heritage-starmart-current-finite-draft-v3.py" --calculate-current-full-collision-only --lease-file <ROOT-fresh-exact-lease> --test-validation "$HERITAGE_PREP/validation.json" --test-validation-sha256 <actual-validation-SHA>
```

Normal worker has no Node capture/source-world decoder. Preserve original source, all capture arrays and historical errors; no physical or installation credit.
