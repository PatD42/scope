from __future__ import annotations

import copy
import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_TOOL_PATH = REPO_ROOT / "src_shared/scripts/audit-artifacts.py"
POLICY_PATH = REPO_ROOT / "src_shared/config/audit-policy.yaml"
AUDIT_COMMAND_PATH = REPO_ROOT / "src_shared/commands/audit_epic.md"
REVIEWER_PATH = REPO_ROOT / "src_shared/commands/audit_epic/reviewer-audit.md"


def _load_audit_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("scope_audit_artifacts", AUDIT_TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = _load_audit_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _dump(path: Path, value: object) -> None:
    _write(path, yaml.safe_dump(value, sort_keys=False))


def _load(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _build_repo(
    tmp_path: Path,
    *,
    risk: str = "low",
    capabilities: list[str] | None = None,
    runtime_required: bool = False,
) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    epic = repo / "docs/epics/E-001-auditable-delivery"
    source = repo / "src/delivery.py"
    test = repo / "tests/test_delivery.py"
    evidence = repo / "tmp_debug/runtime-evidence.txt"

    _write(epic / "acceptance-criteria.md", "# Acceptance Criteria\n\n## AC-001\nDeliver it.\n")
    _write(source, "def delivered() -> bool:\n    return True\n")
    _write(test, "def test_delivered() -> None:\n    assert True\n")
    _write(evidence, "1 passed, 0 failed, 0 errors, 0 skipped\n")
    _dump(
        epic / "refinement-profile.yaml",
        {
            "schema_version": 3,
            "epic_id": "E-001",
            "author_provider": "codex",
            "architecture_scope": "backend",
            "risk_level": risk,
            "capabilities": capabilities or ["content_configuration"],
            "review": {
                "assignments": [
                    {"provider": "claude", "mission": "semantic_core"}
                ],
                "maximum_full_reviews": 1,
                "maximum_targeted_verifications": 1,
            },
        },
    )
    _dump(
        epic / "refinement-manifest.yaml",
        {
            "schema_version": 3,
            "epic_id": "E-001",
            "requirements": [
                {
                    "id": "AC-001",
                    "source": {
                        "artifact": "acceptance-criteria.md",
                        "anchor": "AC-001",
                    },
                    "summary": "The real delivery path succeeds.",
                    "type": "behavior",
                    "risk": risk,
                    "implementation_required": True,
                    "affected_surfaces": ["src/delivery.py"],
                    "proof_obligations": ["Run the delivery test."],
                    "owner_story": "story-01",
                }
            ],
            "decisions": [],
            "artifacts": [],
            "open_items": [],
        },
    )
    _dump(
        epic / "acceptance-traceability.yaml",
        {
            "schema_version": 3,
            "epic_id": "E-001",
            "acceptance_items": [
                {
                    "id": "AC-001",
                    "story": "story-01",
                    "source": {
                        "artifact": "acceptance-criteria.md",
                        "anchor": "AC-001",
                    },
                    "proof_obligation_ids": ["proof-001"],
                    "implementation": {
                        "actual_files": ["src/delivery.py"],
                    },
                    "tests": {
                        "actual_tests": ["tests/test_delivery.py"],
                    },
                    "runtime_evidence": {
                        "required": runtime_required,
                        "commands": ["pytest -q tests/test_delivery.py"]
                        if runtime_required
                        else [],
                        "evidence": ["tmp_debug/runtime-evidence.txt"]
                        if runtime_required
                        else [],
                    },
                    "status": "verified",
                    "audit_notes": "Implementation handoff evidence.",
                }
            ],
        },
    )
    _dump(
        epic / "file-plan-story-01.yaml",
        {
            "epic_id": "E-001",
            "story_id": "story-01",
            "story_title": "Deliver the behavior",
            "depends_on": [],
            "required_contracts": [],
            "required_touchpoints": [],
            "candidate_files": ["src/delivery.py"],
            "forbidden_changes": [],
            "proof_obligations": [
                {
                    "id": "proof-001",
                    "acceptance_rows": ["AC-001"],
                    "required_evidence": "unit",
                    "command": "pytest -q tests/test_delivery.py",
                    "success_condition": "The delivery test passes.",
                    "freshness": "reusable",
                }
            ],
        },
    )
    fingerprint = AUDIT.repository_fingerprint(repo, epic)
    output_hash = AUDIT._file_sha256(evidence)
    test_record = {
        "id": "story-01-proof-001",
        "kind": "test",
        "command": "pytest -q tests/test_delivery.py",
        "cwd": ".",
        "status": "pass",
        "exit_code": 0,
        "output": "tmp_debug/runtime-evidence.txt",
        "output_sha256": output_hash,
        "started_at": "2026-07-28T10:00:00Z",
        "completed_at": "2026-07-28T10:00:01Z",
        "repository_fingerprint": fingerprint,
        "acceptance_rows": ["AC-001"],
        "proof_obligation_ids": ["proof-001"],
        "test_ids": ["tests/test_delivery.py"],
        "test_summary": {
            "passed": 1,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        },
    }
    commands = [test_record]
    if runtime_required:
        runtime_record = {
            **test_record,
            "id": "story-01-runtime-001",
            "kind": "runtime",
            "command": "python -m delivery_smoke",
            "test_ids": [],
        }
        commands.append(runtime_record)
        trace = _load(epic / "acceptance-traceability.yaml")
        trace["acceptance_items"][0]["runtime_evidence"]["commands"] = [
            "python -m delivery_smoke"
        ]
        _dump(epic / "acceptance-traceability.yaml", trace)
    _dump(
        epic / "implementation-evidence.yaml",
        {
            "schema_version": 3,
            "epic_id": "E-001",
            "repository": {
                "head": "no-git-head",
                "fingerprint": fingerprint,
            },
            "stories": [
                {
                    "story_id": "story-01",
                    "status": "verified",
                    "acceptance_rows": ["AC-001"],
                    "strategy": {
                        "inspected_paths": ["src/delivery.py"],
                        "selected_approach": "Preserve the direct delivery path.",
                        "candidate_files_used": ["src/delivery.py"],
                        "candidate_files_skipped": [],
                        "discovered_files": [],
                    },
                    "files_changed": ["src/delivery.py"],
                    "tests_added_or_updated": ["tests/test_delivery.py"],
                    "contract_checks": [],
                    "commands_run": commands,
                    "value_proof": "The delivery path returns success.",
                    "remaining_unproven_work": [],
                }
            ],
            "epic_level": {
                "commands_run": [],
                "coverage": {},
                "operational_deliverables": [],
                "blocked_rows": [],
            },
            "audit_ready": True,
        },
    )
    return repo, epic


def _prepare(
    repo: Path,
    epic: Path,
    *,
    mode: str = "full",
    cycle_id: str = "audit-v3",
    findings: list[str] | None = None,
    siblings: list[str] | None = None,
    allow_extra: bool = False,
    reason: str = "",
) -> Path:
    args = SimpleNamespace(
        epic_dir=epic,
        repo_root=repo,
        policy=POLICY_PATH,
        mode=mode,
        cycle_id=cycle_id,
        finding=findings or [],
        sibling_surface=siblings or [],
        allow_extra=allow_extra,
        reason=reason,
    )
    assert AUDIT.prepare(args) == 0
    return sorted((epic / "reviews").glob("audit-*"))[-1]


def _finding(
    *,
    finding_id: str = "AUDIT-001",
    status: str = "open",
    disposition: str = "remediation_required",
) -> dict[str, object]:
    return {
        "id": finding_id,
        "fingerprint": f"implementation-delivery-{finding_id.lower()}",
        "first_seen_attempt": "audit-001",
        "severity": "major",
        "category": "implementation",
        "source": "reviewer",
        "detected_by": ["codex"],
        "disposition": disposition,
        "status": status,
        "title": "Delivery behavior is not proved",
        "evidence": ["tmp_debug/runtime-evidence.txt"],
        "affected_acceptance_ids": ["AC-001"],
        "affected_files": ["src/delivery.py"],
        "impact": "The promised outcome may not be delivered.",
        "owner": "implementation" if disposition == "remediation_required" else "user",
        "closure_test": "Run the real delivery path and observe success.",
    }


def _refresh_repository_fingerprint(repo: Path, epic: Path) -> None:
    path = epic / "implementation-evidence.yaml"
    evidence = _load(path)
    fingerprint = AUDIT.repository_fingerprint(repo, epic)
    head = AUDIT._run_git(repo, "rev-parse", "HEAD")
    evidence["repository"] = {
        "head": head[0] if head else "no-git-head",
        "fingerprint": fingerprint,
    }
    for story in evidence["stories"]:
        for record in story["commands_run"]:
            record["repository_fingerprint"] = fingerprint
    for record in evidence["epic_level"]["commands_run"]:
        record["repository_fingerprint"] = fingerprint
    _dump(path, evidence)


def _set_evidence_results(epic: Path, attempt_dir: Path, status: str = "pass") -> None:
    matrix_path = attempt_dir / "audit-verification-matrix.yaml"
    matrix = _load(matrix_path)
    scoped = set(_load(attempt_dir / "audit-attempt.yaml")["scope"]["acceptance_rows"])
    for row in matrix["rows"]:
        if row["id"] in scoped:
            row["status"] = status
            row["audit_notes"] = f"Direct evidence result: {status}."
    _dump(matrix_path, matrix)

    attempt_path = attempt_dir / "audit-attempt.yaml"
    attempt = _load(attempt_path)
    for gate in attempt["gates"]:
        gate["status"] = status if status in {"pass", "fail", "blocked"} else "fail"
        if gate["status"] != "pass":
            gate["reused"] = False
        gate["evidence"] = ["tmp_debug/runtime-evidence.txt"]
        gate["reason"] = "" if gate["status"] != "blocked" else "External proof unavailable."
    _dump(attempt_path, attempt)


def _complete_attempt(
    repo: Path,
    epic: Path,
    attempt_dir: Path,
    *,
    status: str = "pass",
    skip_reviews: bool = False,
) -> None:
    _set_evidence_results(epic, attempt_dir, "pass" if status == "pass" else status)
    attempt_path = attempt_dir / "audit-attempt.yaml"
    attempt = _load(attempt_path)
    outputs: list[dict[str, str]] = []
    if skip_reviews:
        attempt["review"]["skipped_reason"] = "Mechanical evidence is not reviewable."
    else:
        for assignment in attempt["review"]["required_assignments"]:
            provider = assignment["provider"]
            mission = assignment["mission"]
            output_path = attempt_dir / f"review-{provider}-{mission}.md"
            metadata_path = attempt_dir / f"metadata-{provider}-{mission}.yaml"
            _write(
                output_path,
                f"# Review\n\nAUDIT_PROVIDER: {provider}\n"
                f"AUDIT_MISSION: {mission}\nDECISION: "
                f"{'pass' if status == 'pass' else 'findings'}\n"
                "COVERED_ACCEPTANCE_IDS: [AC-001]\n",
            )
            _dump(metadata_path, {"provider": provider, "status": "completed"})
            outputs.append(
                {
                    "provider": provider,
                    "mission": mission,
                    "path": str(output_path.relative_to(repo)),
                    "metadata_path": str(metadata_path.relative_to(repo)),
                }
            )
    attempt["review"]["outputs"] = outputs
    attempt["status"] = status
    attempt["decision_reason"] = f"Evidence supports {status}."
    _dump(attempt_path, attempt)

    matrix = _load(attempt_dir / "audit-verification-matrix.yaml")
    _dump(epic / "audit-verification-matrix.yaml", matrix)
    _write(epic / "epic_audit.md", f"# Epic Audit\n\nDecision: {status.upper()}\n")
    AUDIT.record_metrics(SimpleNamespace(epic_dir=epic, attempt_dir=attempt_dir))


def _validate(repo: Path, epic: Path, attempt: Path, phase: str) -> list[str]:
    return AUDIT.AuditValidator(epic, attempt, phase, POLICY_PATH, repo).validate()


def test_prepare_full_derives_scope_matrix_gate_and_three_provider_assignments(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)

    attempt_dir = _prepare(repo, epic)

    attempt = _load(attempt_dir / "audit-attempt.yaml")
    matrix = _load(attempt_dir / "audit-verification-matrix.yaml")
    findings = _load(epic / "audit-findings.yaml")
    assert attempt_dir.name == "audit-001"
    assert attempt["mode"] == "full"
    assert attempt["scope"]["acceptance_rows"] == ["AC-001"]
    assert attempt["review"]["required_assignments"] == [
        {"provider": "claude", "mission": "semantic_core"},
        {"provider": "codex", "mission": "semantic_core"},
        {"provider": "agy", "mission": "semantic_core"},
    ]
    assert attempt["gates"][0]["command"] == "pytest -q tests/test_delivery.py"
    assert attempt["gates"][0]["reused"] is True
    assert matrix["rows"][0]["id"] == "AC-001"
    assert matrix["rows"][0]["implementation"]["actual_files"] == ["src/delivery.py"]
    assert matrix["rows"][0]["status"] == "ready"
    assert findings == {"schema_version": 3, "epic_id": "E-001", "findings": []}
    assert (attempt_dir / "review-packet.yaml").is_file()


@pytest.mark.parametrize(
    ("risk", "expected_focus"),
    [
        ("low", []),
        ("medium", []),
        ("high", ["llm_ml"]),
        ("critical", ["llm_ml"]),
    ],
)
def test_prepare_selects_all_providers_and_capability_focus_from_risk(
    tmp_path: Path,
    risk: str,
    expected_focus: list[str],
) -> None:
    repo, epic = _build_repo(tmp_path, risk=risk, capabilities=["llm_ml"])

    attempt = _load(_prepare(repo, epic) / "audit-attempt.yaml")

    assert {
        assignment["provider"]
        for assignment in attempt["review"]["required_assignments"]
    } == {"claude", "codex", "agy"}
    assert attempt["capability_focus"] == expected_focus


def test_critical_gate_requires_fresh_independent_execution(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path, risk="critical")

    attempt = _load(_prepare(repo, epic) / "audit-attempt.yaml")

    assert attempt["gates"][0]["freshness"] == "fresh"
    assert attempt["gates"][0]["reused"] is False
    assert attempt["gates"][0]["status"] == "pending"


def test_targeted_prepare_requires_remediated_finding_and_scopes_siblings(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    _prepare(repo, epic)
    findings_path = epic / "audit-findings.yaml"
    findings = _load(findings_path)
    findings["findings"] = [_finding(status="open")]
    _dump(findings_path, findings)

    with pytest.raises(ValueError, match="not ready for verification"):
        _prepare(repo, epic, mode="targeted", findings=["AUDIT-001"])

    findings["findings"][0]["status"] = "remediated_pending_verification"
    _dump(findings_path, findings)
    attempt_dir = _prepare(
        repo,
        epic,
        mode="targeted",
        findings=["AUDIT-001", "AUDIT-001"],
        siblings=["src/sibling.py", "src/sibling.py"],
    )
    attempt = _load(attempt_dir / "audit-attempt.yaml")
    assert attempt["mode"] == "targeted"
    assert attempt["scope"] == {
        "acceptance_rows": ["AC-001"],
        "finding_ids": ["AUDIT-001"],
        "sibling_surfaces": ["src/sibling.py"],
    }
    assert attempt["review"]["required_assignments"] == [
        {"provider": "codex", "mission": "semantic_core"}
    ]


def test_targeted_deterministic_finding_uses_closure_gates_without_reviewer(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    _prepare(repo, epic)
    finding = _finding(status="remediated_pending_verification")
    finding["source"] = "deterministic"
    finding["detected_by"] = []
    _dump(
        epic / "audit-findings.yaml",
        {"schema_version": 3, "epic_id": "E-001", "findings": [finding]},
    )

    attempt = _load(
        _prepare(repo, epic, mode="targeted", findings=["AUDIT-001"])
        / "audit-attempt.yaml"
    )

    assert attempt["review"]["required_assignments"] == []
    assert "deterministic closure" in attempt["review"]["skipped_reason"]


def test_targeted_prepare_rejects_missing_unknown_and_unscoped_findings(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    _prepare(repo, epic)

    with pytest.raises(ValueError, match="at least one"):
        _prepare(repo, epic, mode="targeted")
    with pytest.raises(ValueError, match="unknown targeted findings"):
        _prepare(repo, epic, mode="targeted", findings=["AUDIT-404"])

    findings = _load(epic / "audit-findings.yaml")
    unscoped = _finding(status="remediated_pending_verification")
    unscoped["affected_acceptance_ids"] = []
    findings["findings"] = [unscoped]
    _dump(epic / "audit-findings.yaml", findings)
    with pytest.raises(ValueError, match="do not reference any current acceptance rows"):
        _prepare(repo, epic, mode="targeted", findings=["AUDIT-001"])


def test_attempt_budget_requires_explicit_extra_reason(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    _prepare(repo, epic)

    with pytest.raises(ValueError, match="already has 1 full attempt"):
        _prepare(repo, epic)
    with pytest.raises(ValueError, match="requires --reason"):
        _prepare(repo, epic, allow_extra=True)

    extra = _prepare(repo, epic, allow_extra=True, reason="User authorized a new full audit.")
    assert extra.name == "audit-002"


def test_prepare_rejects_bad_mode_identity_and_duplicate_traceability(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    args = SimpleNamespace(
        epic_dir=epic,
        repo_root=repo,
        policy=POLICY_PATH,
        mode="invented",
        cycle_id="audit-v3",
        finding=[],
        sibling_surface=[],
        allow_extra=False,
        reason="",
    )
    with pytest.raises(ValueError, match="unsupported audit mode"):
        AUDIT.prepare(args)

    trace_path = epic / "acceptance-traceability.yaml"
    trace = _load(trace_path)
    trace["epic_id"] = "E-WRONG"
    _dump(trace_path, trace)
    with pytest.raises(ValueError, match="epic_id mismatch"):
        AUDIT.prepare(SimpleNamespace(**{**vars(args), "mode": "full"}))

    _write(trace_path, "schema_version: 2\nepic_id: E-001\nepic_id: E-002\n")
    with pytest.raises(ValueError, match="duplicate key 'epic_id'"):
        AUDIT.prepare(SimpleNamespace(**{**vars(args), "mode": "full"}))


def test_prepare_records_git_changes_against_main(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    _write(repo / "src/removed.py", "VALUE = 1\n")
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Scope Test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "scope@example.test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
    _write(repo / "src/delivery.py", "def delivered() -> bool:\n    return False\n")
    _write(repo / "src/untracked.py", "VALUE = 1\n")
    (repo / "src/removed.py").unlink()
    evidence = _load(epic / "implementation-evidence.yaml")
    evidence["stories"][0]["files_changed"].extend(
        ["src/untracked.py", "src/removed.py"]
    )
    evidence["stories"][0]["strategy"]["discovered_files"].extend(
        ["src/untracked.py", "src/removed.py"]
    )
    _dump(epic / "implementation-evidence.yaml", evidence)
    _refresh_repository_fingerprint(repo, epic)

    attempt = _load(_prepare(repo, epic) / "audit-attempt.yaml")

    assert "src/delivery.py" in attempt["changed_files"]
    assert "src/untracked.py" in attempt["changed_files"]
    assert "src/removed.py" in attempt["changed_files"]


def test_prepare_rejects_missing_v2_handoff_and_policy_helper_errors(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    (epic / "refinement-profile.yaml").unlink()

    with pytest.raises(ValueError, match="missing refinement profile"):
        _prepare(repo, epic)
    assert AUDIT._infer_repo_root(epic) == repo.resolve()
    assert AUDIT._infer_repo_root(tmp_path / "outside") == Path.cwd().resolve()
    with pytest.raises(ValueError, match="invalid risk_level"):
        AUDIT._risk_and_capabilities(
            {"risk_level": "invalid", "capabilities": []}
        )
    with pytest.raises(ValueError, match="capabilities must be a list"):
        AUDIT._risk_and_capabilities(
            {"risk_level": "medium", "capabilities": "bad"}
        )
    assert AUDIT._requirements_by_id({"requirements": "bad"}) == {}
    assert AUDIT._string_list("bad") == []
    with pytest.raises(ValueError, match="cannot determine epic_id"):
        AUDIT._epic_id({}, {}, {})
    with pytest.raises(ValueError, match="must be a mapping"):
        AUDIT._full_assignments({"risk_review_policy": []}, "low")
    with pytest.raises(ValueError, match="has no providers"):
        AUDIT._full_assignments({"risk_review_policy": {}}, "low")
    with pytest.raises(ValueError, match="non-empty strings"):
        AUDIT._full_assignments(
            {
                "risk_review_policy": {"low": {"providers": [""]}},
                "review_providers": ["claude"],
            },
            "low",
        )


def test_matrix_and_gate_derivation_defensive_paths(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    policy = _load(POLICY_PATH)
    base = {
        "acceptance_items": [
            {
                "id": "AC-001",
                "story": "story",
                "requirement": "documentation only",
                "source": {},
                "implementation": {},
                "tests": {},
                "runtime_evidence": {},
            }
        ]
    }
    matrix = AUDIT._derive_matrix(
        epic,
        "audit-001",
        "E-001",
        "medium",
        base,
        {
            "requirements": [
                {"id": "AC-001", "risk": "invalid", "implementation_required": False}
            ]
        },
        policy,
    )
    assert matrix["rows"][0]["risk_level"] == "medium"
    assert matrix["rows"][0]["priority"] == "documentation"

    for bad_items, message in (
        ([], "non-empty acceptance_items"),
        (["bad"], "must be a mapping"),
        ([{}], "id must be a non-empty string"),
        ([base["acceptance_items"][0], base["acceptance_items"][0]], "duplicate"),
    ):
        with pytest.raises(ValueError, match=message):
            AUDIT._derive_matrix(
                epic,
                "audit-001",
                "E-001",
                "low",
                {"acceptance_items": bad_items},
                {},
                policy,
            )

    _dump(epic / "file-plan-story-02.yaml", {"proof_obligations": "bad"})
    _dump(
        epic / "file-plan-story-03.yaml",
        {
            "proof_obligations": [
                "bad",
                {
                    "id": "other-row",
                    "acceptance_rows": ["AC-404"],
                    "command": "pytest ignored.py",
                },
                {
                    "id": "duplicate",
                    "acceptance_rows": ["AC-001"],
                    "command": "pytest -q tests/test_delivery.py",
                },
            ]
        },
    )
    gates = AUDIT._boundary_gates(epic, {"AC-001"}, _load(epic / "refinement-manifest.yaml"), [])
    assert len(gates) == 1


def test_prepare_ignores_malformed_historical_attempt_and_rejects_bad_findings_shape(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    _write(epic / "reviews/audit-001/audit-attempt.yaml", "epic_id: [unterminated\n")
    attempt = _prepare(repo, epic)
    assert attempt.name == "audit-002"

    other_repo, other_epic = _build_repo(tmp_path / "other")
    _dump(other_epic / "audit-findings.yaml", {"schema_version": 3, "epic_id": "E-001", "findings": {}})
    with pytest.raises(ValueError, match="must contain a findings list"):
        _prepare(other_repo, other_epic)


def test_pre_review_validation_passes_with_complete_direct_evidence(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path, runtime_required=True)
    attempt = _prepare(repo, epic)
    _set_evidence_results(epic, attempt)

    assert _validate(repo, epic, attempt, "pre_review") == []


def test_evidence_verifier_accepts_full_and_story_scopes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, epic = _build_repo(tmp_path)
    args = SimpleNamespace(
        epic_dir=epic,
        repo_root=repo,
        policy=POLICY_PATH,
        story="",
    )

    assert AUDIT.verify_evidence(args) == 0
    assert "audit-ready handoff" in capsys.readouterr().out
    args.story = "story-01"
    assert AUDIT.verify_evidence(args) == 0
    assert "story=story-01" in capsys.readouterr().out
    assert AUDIT.print_fingerprint(
        SimpleNamespace(epic_dir=epic, repo_root=repo)
    ) == 0
    assert "sha256:" in capsys.readouterr().out


def test_evidence_verifier_rejects_stale_output_and_malformed_records(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    path = epic / "implementation-evidence.yaml"
    evidence = _load(path)
    story = evidence["stories"][0]
    record = story["commands_run"][0]
    evidence["schema_version"] = 2
    evidence["epic_id"] = "WRONG"
    evidence["repository"] = {"head": "wrong", "fingerprint": "sha256:wrong"}
    story["status"] = "invented"
    story["strategy"]["selected_approach"] = ""
    story["strategy"]["candidate_files_used"] = []
    story["files_changed"].append("src/missing.py")
    story["remaining_unproven_work"] = []
    record.update(
        {
            "kind": "test",
            "command": "",
            "status": "pass",
            "exit_code": 7,
            "output_sha256": "sha256:wrong",
            "acceptance_rows": [1],
            "proof_obligation_ids": "bad",
            "test_ids": ["tests/missing.py::test_missing"],
            "test_summary": {
                "passed": -1,
                "failed": 1,
                "errors": "bad",
                "skipped": -1,
            },
        }
    )
    story["commands_run"].extend(
        [
            "bad",
            {
                **record,
                "id": "inspection",
                "kind": "inspection",
                "command": "",
                "inspection": "",
                "exit_code": 0,
                "test_ids": [],
            },
        ]
    )
    evidence["epic_level"]["commands_run"] = ["bad"]
    evidence["epic_level"]["blocked_rows"] = ["AC-001"]
    evidence["audit_ready"] = False
    _dump(path, evidence)

    errors = AUDIT.ImplementationEvidenceVerifier(
        epic, POLICY_PATH, repo
    ).validate()
    joined = "\n".join(errors)

    for expected in (
        "schema_version must be 3",
        "epic_id does not match",
        "HEAD does not match",
        "repository fingerprint does not match",
        "status must be one of",
        "selected_approach",
        "unclassified changed files",
        "path does not exist",
        "commands_run entries must be mappings",
        "passing command must have exit_code 0",
        "output_sha256 does not match",
        "test_summary.passed",
        "passing test command reports failures",
        "inspection must be a non-empty string",
        "inspection exit_code must be null",
        "audit_ready must be true",
        "blocked_rows",
    ):
        assert expected in joined


def test_evidence_verifier_rejects_stale_source_and_missing_story(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, epic = _build_repo(tmp_path)
    _write(repo / "src/delivery.py", "def delivered() -> bool:\n    return False\n")

    args = SimpleNamespace(
        epic_dir=epic,
        repo_root=repo,
        policy=POLICY_PATH,
        story="missing-story",
    )
    assert AUDIT.verify_evidence(args) == 1
    error = capsys.readouterr().err
    assert "repository fingerprint does not match" in error
    assert "has no story 'missing-story'" in error


def test_pre_review_rejects_pending_or_missing_required_evidence(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path, runtime_required=True)
    attempt = _prepare(repo, epic)
    matrix_path = attempt / "audit-verification-matrix.yaml"
    matrix = _load(matrix_path)
    matrix["rows"][0]["implementation"]["actual_files"] = []
    matrix["rows"][0]["tests"]["required_assertions"] = []
    matrix["rows"][0]["tests"]["actual_tests"] = []
    matrix["rows"][0]["runtime_evidence"]["commands"] = []
    matrix["rows"][0]["runtime_evidence"]["evidence"] = []
    _dump(matrix_path, matrix)
    attempt_path = attempt / "audit-attempt.yaml"
    attempt_data = _load(attempt_path)
    attempt_data["gates"][0]["status"] = "pending"
    attempt_data["gates"][0]["reused"] = False
    attempt_data["gates"][0]["evidence"] = []
    _dump(attempt_path, attempt_data)

    errors = _validate(repo, epic, attempt, "pre_review")

    assert any("no actual implementation files" in error for error in errors)
    assert any("no required assertions" in error for error in errors)
    assert any("no actual tests" in error for error in errors)
    assert any("no runtime command" in error for error in errors)
    assert any("no runtime evidence" in error for error in errors)
    assert any("gates[1] remains pending" in error for error in errors)


def test_validator_rederives_immutable_matrix_fields(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    _set_evidence_results(epic, attempt)
    matrix_path = attempt / "audit-verification-matrix.yaml"
    matrix = _load(matrix_path)
    matrix["rows"][0]["requirement"] = "A reviewer invented a different requirement."
    matrix["rows"][0]["implementation"]["actual_files"] = ["src/fake.py"]
    _dump(matrix_path, matrix)

    errors = _validate(repo, epic, attempt, "pre_review")

    assert any("requirement differs from derived traceability" in error for error in errors)
    assert any("implementation differs from derived traceability" in error for error in errors)


def test_complete_pass_requires_and_accepts_provider_outputs_and_published_artifacts(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path, risk="medium")
    attempt = _prepare(repo, epic)
    _complete_attempt(repo, epic, attempt)

    assert _validate(repo, epic, attempt, "complete") == []


def test_complete_rejects_missing_mismatched_or_malformed_provider_outputs(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    _complete_attempt(repo, epic, attempt)
    attempt_path = attempt / "audit-attempt.yaml"
    data = _load(attempt_path)
    output = repo / data["review"]["outputs"][0]["path"]
    _write(
        output,
        "# Review\n\nAUDIT_PROVIDER: invented\nAUDIT_MISSION: invented\n"
        "DECISION: invented\nCOVERED_ACCEPTANCE_IDS: []\n",
    )
    data["review"]["required_assignments"].append(
        {"provider": "invented", "mission": "semantic_core"}
    )
    _dump(attempt_path, data)

    errors = _validate(repo, epic, attempt, "complete")

    assert any("unknown provider 'invented'" in error for error in errors)
    assert any("declares AUDIT_PROVIDER 'invented'" in error for error in errors)
    assert any("declares AUDIT_MISSION 'invented'" in error for error in errors)
    assert any("unsupported DECISION 'invented'" in error for error in errors)
    assert any("has no output for assignments: invented/semantic_core" in error for error in errors)

    _write(output, "# Review without markers\n")
    errors = _validate(repo, epic, attempt, "complete")
    assert any("output has no valid AUDIT_PROVIDER" in error for error in errors)
    assert any("output has no valid AUDIT_MISSION" in error for error in errors)
    assert any("output has no valid DECISION" in error for error in errors)


def test_finding_schema_and_reciprocal_matrix_links_are_enforced(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    _set_evidence_results(epic, attempt, "fail")
    findings = _load(epic / "audit-findings.yaml")
    first = _finding()
    second = copy.deepcopy(first)
    second["id"] = "AUDIT-002"
    second["evidence"] = []
    second["affected_acceptance_ids"] = ["AC-404"]
    findings["findings"] = [first, second]
    _dump(epic / "audit-findings.yaml", findings)
    matrix_path = attempt / "audit-verification-matrix.yaml"
    matrix = _load(matrix_path)
    matrix["rows"][0]["finding_ids"] = ["AUDIT-404", "AUDIT-002"]
    _dump(matrix_path, matrix)

    errors = _validate(repo, epic, attempt, "pre_review")

    assert any("duplicate finding fingerprints" in error for error in errors)
    assert any("references unknown acceptance rows: AC-404" in error for error in errors)
    assert any("evidence must not be empty" in error for error in errors)
    assert any("references unknown findings: AUDIT-404" in error for error in errors)
    assert any("links finding AUDIT-002 without reciprocal scope" in error for error in errors)
    assert any("finding AUDIT-001 is missing from matrix row AC-001" in error for error in errors)


def test_record_metrics_counts_only_new_findings_and_preserves_provider_provenance(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    first = _finding()
    first["detected_by"] = ["codex", "agy"]
    second = _finding(finding_id="AUDIT-002")
    second["category"] = "mechanical"
    second["source"] = "deterministic"
    second["detected_by"] = []
    third = _finding(finding_id="AUDIT-003")
    third["first_seen_attempt"] = "audit-000"
    _dump(
        epic / "audit-findings.yaml",
        {
            "schema_version": 3,
            "epic_id": "E-001",
            "findings": [first, second, third],
        },
    )

    assert AUDIT.record_metrics(
        SimpleNamespace(epic_dir=epic, attempt_dir=attempt)
    ) == 0
    metrics = _load(attempt / "audit-attempt.yaml")["metrics"]

    assert metrics["new_findings"]["total"] == 2
    assert metrics["new_findings"]["by_category"] == {
        "implementation": 1,
        "mechanical": 1,
    }
    assert metrics["new_findings"]["by_source"] == {
        "deterministic": 1,
        "reviewer": 1,
    }
    assert metrics["new_findings"]["by_provider"] == {"agy": 1, "codex": 1}
    assert metrics["targeted_verification_required"] is True


def test_valid_fail_links_nonpassing_row_to_remediation_finding(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    findings = _load(epic / "audit-findings.yaml")
    findings["findings"] = [_finding()]
    _dump(epic / "audit-findings.yaml", findings)
    _complete_attempt(repo, epic, attempt, status="fail", skip_reviews=True)
    matrix_path = attempt / "audit-verification-matrix.yaml"
    matrix = _load(matrix_path)
    matrix["rows"][0]["finding_ids"] = ["AUDIT-001"]
    _dump(matrix_path, matrix)
    _dump(epic / "audit-verification-matrix.yaml", matrix)

    assert _validate(repo, epic, attempt, "complete") == []


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("pass", "PASS requires passing scoped rows/gates and no active findings"),
        ("fail", "FAIL requires non-passing evidence or remediation findings"),
        ("blocked", "BLOCKED requires decision-gated findings or blocked evidence"),
    ],
)
def test_completion_status_must_match_evidence(
    tmp_path: Path,
    status: str,
    expected: str,
) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    _complete_attempt(repo, epic, attempt, status=status)
    if status == "pass":
        findings = _load(epic / "audit-findings.yaml")
        findings["findings"] = [_finding()]
        _dump(epic / "audit-findings.yaml", findings)
        matrix_path = attempt / "audit-verification-matrix.yaml"
        matrix = _load(matrix_path)
        matrix["rows"][0]["finding_ids"] = ["AUDIT-001"]
        _dump(matrix_path, matrix)
        _dump(epic / "audit-verification-matrix.yaml", matrix)
    elif status in {"fail", "blocked"}:
        _set_evidence_results(epic, attempt, "pass")
        matrix = _load(attempt / "audit-verification-matrix.yaml")
        _dump(epic / "audit-verification-matrix.yaml", matrix)

    errors = _validate(repo, epic, attempt, "complete")

    assert any(expected in error for error in errors)


def test_targeted_pass_requires_named_findings_to_be_terminal(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    _prepare(repo, epic)
    findings_path = epic / "audit-findings.yaml"
    findings = _load(findings_path)
    findings["findings"] = [_finding(status="remediated_pending_verification")]
    _dump(findings_path, findings)
    targeted = _prepare(repo, epic, mode="targeted", findings=["AUDIT-001"])
    _complete_attempt(repo, epic, targeted)
    matrix_path = targeted / "audit-verification-matrix.yaml"
    matrix = _load(matrix_path)
    matrix["rows"][0]["finding_ids"] = ["AUDIT-001"]
    _dump(matrix_path, matrix)
    _dump(epic / "audit-verification-matrix.yaml", matrix)

    errors = _validate(repo, epic, targeted, "complete")
    assert any("PASS requires passing scoped rows/gates and no active findings" in error for error in errors)
    assert any("targeted PASS has unresolved findings: AUDIT-001" in error for error in errors)

    findings["findings"][0]["status"] = "verified"
    _dump(findings_path, findings)
    assert _validate(repo, epic, targeted, "complete") == []


def test_completion_requires_decision_report_matrix_and_nonpending_status(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    _set_evidence_results(epic, attempt)
    attempt_path = attempt / "audit-attempt.yaml"
    data = _load(attempt_path)
    data["review"]["skipped_reason"] = "Evidence failed."
    data["decision_reason"] = ""
    _dump(attempt_path, data)

    errors = _validate(repo, epic, attempt, "complete")

    assert any("status remains pending" in error for error in errors)
    assert any("missing published audit matrix" in error for error in errors)
    assert any("missing audit report" in error for error in errors)


def test_validator_early_guards_and_invalid_yaml(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    attempt = _prepare(repo, epic)
    assert AUDIT.AuditValidator(epic, attempt, "unknown", POLICY_PATH, repo).validate() == [
        "unsupported validation phase: unknown"
    ]
    assert "epic directory does not exist" in AUDIT.AuditValidator(
        repo / "missing", attempt, "pre_review", POLICY_PATH, repo
    ).validate()[0]
    assert "audit attempt directory does not exist" in AUDIT.AuditValidator(
        epic, repo / "missing", "pre_review", POLICY_PATH, repo
    ).validate()[0]

    _write(epic / "audit-findings.yaml", "- not-a-mapping\n")
    errors = _validate(repo, epic, attempt, "pre_review")
    assert any("must contain a YAML mapping" in error for error in errors)


def test_cli_main_reports_prepare_validation_success_and_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, epic = _build_repo(tmp_path)
    assert AUDIT.main(
        [
            "prepare",
            str(epic),
            "--repo-root",
            str(repo),
            "--policy",
            str(POLICY_PATH),
            "--mode",
            "full",
        ]
    ) == 0
    assert "reviews/audit-001" in capsys.readouterr().out
    attempt = epic / "reviews/audit-001"
    _set_evidence_results(epic, attempt)
    assert AUDIT.main(
        [
            "validate",
            str(epic),
            str(attempt),
            "--phase",
            "pre_review",
            "--repo-root",
            str(repo),
            "--policy",
            str(POLICY_PATH),
        ]
    ) == 0
    assert "Audit artifact validation passed" in capsys.readouterr().out

    (epic / "acceptance-traceability.yaml").unlink()
    assert AUDIT.main(
        [
            "prepare",
            str(epic),
            "--repo-root",
            str(repo),
            "--policy",
            str(POLICY_PATH),
            "--mode",
            "full",
            "--allow-extra",
            "--reason",
            "test error handling",
        ]
    ) == 1
    assert "Audit artifact operation failed" in capsys.readouterr().err


def test_command_and_reviewer_are_read_only_provider_based_and_isolated() -> None:
    command = AUDIT_COMMAND_PATH.read_text(encoding="utf-8")
    reviewer = REVIEWER_PATH.read_text(encoding="utf-8")
    combined = f"{command}\n{reviewer}".lower()

    assert "audit is read-only" in combined
    assert "one full audit" in command
    assert "one targeted" in command
    assert "semantic_core" in command
    assert "{{AUDIT_PROVIDER}}" in reviewer
    assert "claude, codex, and agy" in command.lower()
    assert "gpt-5.6-terra" in command
    assert 'model_reasoning_effort="\\"$CODEX_REASONING_EFFORT\\""' in command
    assert "--sandbox read-only" in command
    assert "--dangerously-skip-permissions" in command
    for coupled_term in (
        "glm-5.2",
        "auto-fix finding",
        "maximum audit attempts: 3",
        "compliance percentage",
    ):
        assert coupled_term not in combined
