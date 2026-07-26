from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = REPO_ROOT / "src_shared/scripts/validate-refinement.py"
POLICY_PATH = REPO_ROOT / "src_shared/config/refinement-policy.yaml"
COMMAND_PATH = REPO_ROOT / "src_shared/commands/epic_refine.md"
REVIEWER_PATH = REPO_ROOT / "src_shared/commands/epic_refine/reviewer-refinement.md"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "scope_validate_refinement", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REFINE = _load_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _dump(path: Path, value: object) -> None:
    _write(path, yaml.safe_dump(value, sort_keys=False))


def _load(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _assignments(risk: str, author: str) -> list[dict[str, str]]:
    if risk == "low":
        return [
            {
                "provider": "claude" if author == "codex" else "codex",
                "mission": "semantic_core",
            }
        ]
    result = [
        {"provider": "claude", "mission": "semantic_core"},
        {"provider": "codex", "mission": "semantic_core"},
    ]
    if risk in {"high", "critical"}:
        result.append(
            {"provider": author, "mission": "capability_specialist"}
        )
    return result


def _design(risk: str, capabilities: list[str]) -> str:
    challenges = [
        "authority-and-ownership",
        "producer-consumer-flow",
        "failure-and-partial-state",
        "proof-path",
    ]
    capability_challenges = {
        "content_configuration": [
            "single-content-authority",
            "renderer-validator-parity",
        ],
        "api_interface": [
            "request-response-completeness",
            "compatibility-and-errors",
        ],
    }
    for capability in capabilities:
        challenges.extend(capability_challenges.get(capability, []))
    challenge_text = "\n\n".join(
        f"### CHALLENGE-{challenge}\nResolved through the delivery contract."
        for challenge in challenges
    )
    high_risk = ""
    if risk in {"high", "critical"}:
        high_risk = """

### FLOW-AC-001
Authority: acceptance-criteria.md
Producer: deliver
Boundary: delivery service
State owner: delivery service
Consumer: caller
Failure policy: reject invalid input
Proof: proof-001

### HOSTILE-AC-001
Invalid case: malformed content
Rejection mechanism: validation error
Evidence: [EVIDENCE: src/service.py#def deliver]
"""
    return f"""# Design

## Current State and Evidence

The existing service owns delivery. [EVIDENCE: src/service.py#def deliver]

## Product and Architecture Decisions

### PDR-001: Preserve observable delivery

Status: Accepted

### ADR-001: Keep service ownership

Status: Accepted

## Architecture and Ownership

The delivery service remains authoritative.

## Failure and Partial States

Invalid values are rejected before state changes.

## Capability Challenges

{challenge_text}

## Hostile Cases

Malformed input is rejected.{high_risk}

## Verification Strategy

Run `pytest -q tests/test_service.py`.
"""


def _build_repo(
    tmp_path: Path,
    *,
    risk: str = "low",
    author: str = "codex",
    capabilities: list[str] | None = None,
) -> tuple[Path, Path]:
    if capabilities is None:
        capabilities = ["content_configuration"] if risk in {"high", "critical"} else []
    repo = tmp_path / "repo"
    epic = repo / "docs/epics/E-001-delivery"
    _write(
        epic / "details.md",
        """---
epic_id: E-001
title: Delivery
status: ready-for-implementation
---

# Delivery

The implementation preserves the approved outcome.
""",
    )
    _write(
        epic / "acceptance-criteria.md",
        "# Acceptance Criteria\n\n## AC-001: Deliver approved content\n",
    )
    _write(epic / "design.md", _design(risk, capabilities))
    _write(
        repo / "src/service.py",
        "def deliver(value: str) -> str:\n    return value\n",
    )
    _write(
        repo / "tests/test_service.py",
        "def test_delivery() -> None:\n    assert True\n",
    )
    _write(repo / "config/content.yaml", "delivery: enabled\n")

    assignments = _assignments(risk, author)
    _dump(
        epic / "refinement-profile.yaml",
        {
            "schema_version": 3,
            "epic_id": "E-001",
            "author_provider": author,
            "architecture_scope": "backend",
            "risk_level": risk,
            "capabilities": capabilities,
            "workflow_started_at": "2026-07-26T10:00:00Z",
            "workflow_completed_at": "2026-07-26T10:10:00Z",
            "review": {
                "assignments": assignments,
                "maximum_full_reviews": 1,
                "maximum_targeted_verifications": (
                    2 if risk in {"high", "critical"} else 1
                ),
            },
        },
    )

    REFINE.RefinementScaffolder(epic, POLICY_PATH, repo).run()
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = _load(manifest_path)
    requirement = manifest["requirements"][0]
    requirement["affected_surfaces"] = ["src/service.py#deliver"]
    requirement["proof_obligations"] = ["proof-001"]
    requirement["owner_story"] = "story-01"
    if capabilities:
        kind = "api_schema" if "api_interface" in capabilities else "authored_config"
        manifest["artifacts"] = [
            {
                "id": "artifact-001",
                "path": "config/content.yaml",
                "kind": kind,
                "authority": "canonical",
                "capabilities": capabilities,
            }
        ]
    _dump(manifest_path, manifest)
    _dump(
        epic / "file-plan-story-01.yaml",
        {
            "epic_id": "E-001",
            "story_id": "story-01",
            "story_title": "Deliver approved content",
            "depends_on": [],
            "required_contracts": [
                {
                    "id": "contract-001",
                    "contract": "src/service.py#deliver",
                    "obligation": "Return approved content",
                    "verification": "pytest -q tests/test_service.py",
                }
            ],
            "required_touchpoints": [
                {
                    "id": "touchpoint-001",
                    "surface": "src/service.py#deliver",
                    "obligation": "Preserve the caller boundary",
                    "evidence_required": "unit test",
                }
            ],
            "candidate_files": [
                {
                    "path": "src/service.py",
                    "reason": "Current owner",
                    "advisory": True,
                }
            ],
            "forbidden_changes": [
                {
                    "path_or_surface": "public delivery behavior",
                    "rule": "Requires renewed refinement",
                }
            ],
            "proof_obligations": [
                {
                    "id": "proof-001",
                    "acceptance_rows": ["AC-001"],
                    "required_evidence": "unit",
                    "command_hint": "pytest -q tests/test_service.py",
                    "success_condition": "The delivery test passes",
                }
            ],
        },
    )
    REFINE.RefinementScaffolder(epic, POLICY_PATH, repo).run()

    outputs: list[dict[str, str]] = []
    for assignment in assignments:
        provider = assignment["provider"]
        mission = assignment["mission"]
        output = epic / f"reviews/refine-v3-001/review-{provider}-{mission}.md"
        _write(
            output,
            f"# Review\n\nREVIEW_PROVIDER: {provider}\n"
            f"REVIEW_MISSION: {mission}\n\nDECISION: approved\n",
        )
        outputs.append(
            {
                "provider": provider,
                "mission": mission,
                "path": str(output.relative_to(repo)),
            }
        )
    _dump(
        epic / "refinement-findings.yaml",
        {
            "schema_version": 2,
            "epic_id": "E-001",
            "review": {
                "full_review_count": 1,
                "targeted_verification_count": 0,
                "completed_assignments": assignments,
                "outputs": outputs,
            },
            "findings": [],
        },
    )
    _write(
        epic / "refinement-review.md",
        "# Refinement Review\n\nDecision: Approved for implementation\n",
    )
    return repo, epic


def _validate(repo: Path, epic: Path, phase: str) -> tuple[list[str], object]:
    validator = REFINE.RefinementValidator(epic, phase, POLICY_PATH, repo)
    return validator.validate(), validator


def test_valid_handoff_passes_every_phase(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)

    for phase in REFINE.PHASE_ORDER:
        errors, _ = _validate(repo, epic, phase)
        assert errors == [], (phase, errors)


@pytest.mark.parametrize(
    ("risk", "author", "expected"),
    [
        ("low", "claude", ["codex:semantic_core"]),
        ("medium", "codex", ["claude:semantic_core", "codex:semantic_core"]),
        (
            "high",
            "claude",
            [
                "claude:semantic_core",
                "codex:semantic_core",
                "claude:capability_specialist",
            ],
        ),
        (
            "critical",
            "codex",
            [
                "claude:semantic_core",
                "codex:semantic_core",
                "codex:capability_specialist",
            ],
        ),
    ],
)
def test_risk_topology_is_exact(
    tmp_path: Path,
    risk: str,
    author: str,
    expected: list[str],
) -> None:
    repo, epic = _build_repo(tmp_path, risk=risk, author=author)

    errors, validator = _validate(repo, epic, "profile")

    assert errors == []
    assert [
        REFINE._assignment_key(row)
        for row in REFINE._expected_assignments(validator.profile, validator.policy)
    ] == expected


def test_profile_rejects_invalid_values_and_topology(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    path = epic / "refinement-profile.yaml"
    profile = _load(path)
    profile.update(
        {
            "schema_version": 2,
            "epic_id": "",
            "author_provider": "other",
            "architecture_scope": "planet",
            "risk_level": "extreme",
            "capabilities": ["unknown"],
            "review": {
                "assignments": [
                    {"provider": "other", "mission": "unknown"},
                    {"provider": "other", "mission": "unknown"},
                ],
                "maximum_full_reviews": 9,
                "maximum_targeted_verifications": 9,
            },
        }
    )
    _dump(path, profile)

    errors, _ = _validate(repo, epic, "profile")
    joined = "\n".join(errors)

    for expected in (
        "schema_version",
        "epic_id must be a non-empty string",
        "author_provider",
        "architecture_scope",
        "risk_level",
        "unknown capability",
        "invalid provider",
        "invalid mission",
        "duplicate review.assignments",
        "must match risk/provider topology",
    ):
        assert expected in joined


def test_high_risk_requires_capability(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path, risk="high")
    profile_path = epic / "refinement-profile.yaml"
    profile = _load(profile_path)
    profile["capabilities"] = []
    _dump(profile_path, profile)

    errors, _ = _validate(repo, epic, "profile")

    assert any("requires at least one capability" in error for error in errors)


def test_product_rejects_missing_duplicate_ids_and_decision_heading(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    _write(
        epic / "acceptance-criteria.md",
        "# Acceptance\n\n## AC-001: First\n\n## AC-001: Duplicate\n",
    )
    _write(epic / "design.md", "# Design\n")

    errors, _ = _validate(repo, epic, "product")
    joined = "\n".join(errors)

    assert "duplicate stable acceptance requirement ids" in joined
    assert "missing heading: Product and Architecture Decisions" in joined

    _write(epic / "acceptance-criteria.md", "# Acceptance\n\nNo stable ID.\n")
    errors, _ = _validate(repo, epic, "product")
    assert any("must contain AC-, ERR-, or E2E- headings" in e for e in errors)


def test_requirement_cross_references_do_not_redeclare_canonical_ids(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    acceptance = epic / "acceptance-criteria.md"
    _write(
        acceptance,
        "# Acceptance Criteria\n\n## AC-001: Deliver\n\n"
        "The E2E proof references AC-001 without redeclaring it.\n",
    )

    errors, _ = _validate(repo, epic, "product")

    assert errors == []


def test_scaffolder_preserves_semantic_judgment_and_actual_evidence(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    trace_path = epic / "acceptance-traceability.yaml"
    manifest = _load(manifest_path)
    manifest["requirements"][0]["summary"] = "User-confirmed summary"
    manifest["requirements"].append(
        {
            "id": "AC-STALE",
            "source": {"artifact": "acceptance-criteria.md", "anchor": "AC-001"},
            "summary": "Removed scope",
        }
    )
    manifest["decisions"].append(
        {
            "id": "ADR-STALE",
            "source": {"artifact": "design.md", "anchor": "ADR-001"},
            "summary": "Removed decision",
            "status": "accepted",
        }
    )
    _dump(manifest_path, manifest)
    trace = _load(trace_path)
    trace["acceptance_items"][0]["implementation"]["actual_files"] = [
        "src/service.py"
    ]
    trace["acceptance_items"][0]["tests"]["actual_tests"] = [
        "tests/test_service.py"
    ]
    trace["acceptance_items"][0]["status"] = "verified"
    _dump(trace_path, trace)

    written = REFINE.RefinementScaffolder(epic, POLICY_PATH, repo).run()

    assert written == [manifest_path, trace_path]
    regenerated_manifest = _load(manifest_path)
    assert regenerated_manifest["requirements"][0]["summary"] == "User-confirmed summary"
    assert [row["id"] for row in regenerated_manifest["requirements"]] == ["AC-001"]
    assert {row["id"] for row in regenerated_manifest["decisions"]} == {
        "PDR-001",
        "ADR-001",
    }
    generated = _load(trace_path)["acceptance_items"][0]
    assert generated["implementation"]["actual_files"] == ["src/service.py"]
    assert generated["tests"]["actual_tests"] == ["tests/test_service.py"]
    assert generated["status"] == "verified"


@pytest.mark.parametrize(
    ("artifact", "message"),
    [
        ("refinement-profile.yaml", "legacy profiles are not supported"),
        ("refinement-manifest.yaml", "legacy refinement manifest"),
        ("acceptance-traceability.yaml", "legacy acceptance traceability"),
    ],
)
def test_scaffolder_rejects_legacy_artifacts(
    tmp_path: Path,
    artifact: str,
    message: str,
) -> None:
    repo, epic = _build_repo(tmp_path)
    path = epic / artifact
    document = _load(path)
    document["schema_version"] = 2
    _dump(path, document)

    with pytest.raises(ValueError, match=message):
        REFINE.RefinementScaffolder(epic, POLICY_PATH, repo).run()


def test_architecture_reports_manifest_and_design_defects(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = _load(manifest_path)
    requirement = manifest["requirements"][0]
    requirement.update(
        {
            "source": {"artifact": "../outside.md", "anchor": ""},
            "summary": "",
            "type": "invented",
            "risk": "extreme",
            "implementation_required": "yes",
            "affected_surfaces": [""],
            "proof_obligations": "not-a-list",
        }
    )
    manifest["requirements"].append(dict(requirement))
    manifest["decisions"][0].update(
        {
            "source": "not-a-mapping",
            "summary": "",
            "status": "rejected",
        }
    )
    manifest["artifacts"] = [
        {
            "id": "artifact-001",
            "path": "missing.yaml",
            "kind": "authored_config",
            "authority": "invented",
            "capabilities": ["unknown"],
        },
        {
            "id": "artifact-001",
            "path": "config/content.yaml",
            "kind": "authored_config",
            "authority": "canonical",
            "capabilities": [],
        },
    ]
    manifest["open_items"] = [{"id": "", "status": "invented"}]
    _dump(manifest_path, manifest)
    _write(
        epic / "design.md",
        """# Design

## Product and Architecture Decisions

[EVIDENCE: /absolute/path#anchor]
[EVIDENCE: src/service.py]
[EVIDENCE: src/service.py#missing-anchor]
""",
    )

    errors, _ = _validate(repo, epic, "architecture")
    joined = "\n".join(errors)
    for expected in (
        "source.artifact must be repository-relative",
        "summary must be a non-empty string",
        "type must be one of",
        "risk must be one of",
        "implementation_required must be boolean",
        "affected_surfaces values must be non-empty strings",
        "proof_obligations must be a list",
        "duplicate requirement ids",
        "source must be a mapping",
        "status must be accepted",
        "artifact path does not exist",
        "unknown capability",
        "duplicate artifact ids",
        "open_items[1] id must be a non-empty string",
        "missing required heading",
        "evidence path must be repository-relative",
        "evidence marker must use path#anchor",
        "evidence anchor not found",
        "missing architecture challenge",
    ):
        assert expected in joined


def test_selected_capability_requires_tagged_native_artifact(tmp_path: Path) -> None:
    repo, epic = _build_repo(
        tmp_path, risk="high", capabilities=["api_interface"]
    )
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = _load(manifest_path)
    manifest["artifacts"] = []
    _dump(manifest_path, manifest)

    errors, _ = _validate(repo, epic, "architecture")
    assert any("no artifact tagged for selected capability api_interface" in e for e in errors)

    manifest["artifacts"] = [
        {
            "id": "artifact-001",
            "path": "config/content.yaml",
            "kind": "authored_config",
            "authority": "canonical",
            "capabilities": ["api_interface"],
        }
    ]
    _dump(manifest_path, manifest)
    errors, _ = _validate(repo, epic, "architecture")
    assert any("requires an accepted native artifact kind" in e for e in errors)


def test_high_risk_requires_complete_flow_and_hostile_sections(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path, risk="high")
    design_path = epic / "design.md"
    text = design_path.read_text(encoding="utf-8")
    text = text.replace("Failure policy: reject invalid input\n", "")
    text = text.replace("Rejection mechanism: validation error\n", "")
    _write(design_path, text)

    errors, _ = _validate(repo, epic, "architecture")

    assert any("FLOW-AC-001 missing field Failure policy:" in e for e in errors)
    assert any(
        "HOSTILE-AC-001 missing field Rejection mechanism:" in e for e in errors
    )


def test_reconciliation_reports_plan_ownership_and_dependency_defects(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    first_path = epic / "file-plan-story-01.yaml"
    first = _load(first_path)
    first["depends_on"] = ["story-02", "story-01", "missing-story"]
    first["candidate_files"][0]["advisory"] = False
    first["required_contracts"].append(
        {"id": "contract-001", "contract": "", "obligation": "", "verification": ""}
    )
    first["proof_obligations"][0]["acceptance_rows"] = ["UNKNOWN-001"]
    _dump(first_path, first)
    second = dict(first)
    second["story_id"] = "story-02"
    second["depends_on"] = ["story-01"]
    second["required_contracts"] = []
    second["required_touchpoints"] = []
    second["candidate_files"] = []
    second["forbidden_changes"] = []
    second["proof_obligations"] = []
    _dump(epic / "file-plan-story-02.yaml", second)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = _load(manifest_path)
    manifest["requirements"][0]["owner_story"] = "missing-owner"
    manifest["open_items"] = [{"id": "OPEN-001", "status": "open"}]
    _dump(manifest_path, manifest)

    errors, _ = _validate(repo, epic, "reconcile")
    joined = "\n".join(errors)
    for expected in (
        "remains unresolved",
        "advisory must be true",
        "duplicate required_contracts ids",
        "references unknown acceptance rows",
        "depends on itself",
        "depends on unknown story",
        "story dependency cycle includes",
        "references unknown owner_story",
        "has no story proof obligation",
    ):
        assert expected in joined


def test_traceability_must_match_generated_authorities(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    path = epic / "acceptance-traceability.yaml"
    trace = _load(path)
    row = trace["acceptance_items"][0]
    row.update(
        {
            "story": "story-other",
            "source": {},
            "proof_obligation_ids": ["proof-other"],
            "implementation": "bad",
            "tests": {"actual_tests": [1]},
            "runtime_evidence": {
                "required": "yes",
                "commands": "bad",
                "evidence": [],
            },
            "status": "unknown",
            "audit_notes": [],
        }
    )
    trace["acceptance_items"].append(dict(row, id="AC-EXTRA"))
    _dump(path, trace)

    errors, _ = _validate(repo, epic, "reconcile")
    joined = "\n".join(errors)
    for expected in (
        "story does not match manifest owner_story",
        "source does not match manifest",
        "proof_obligation_ids do not match story plans",
        "implementation must be a mapping",
        "actual_tests values must be non-empty strings",
        "commands must be a list",
        "runtime_evidence.required must be boolean",
        "status must be one of",
        "audit_notes must be a string",
        "has non-implementation rows",
    ):
        assert expected in joined


def test_review_requires_exact_outputs_and_valid_findings(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path, risk="medium")
    findings_path = epic / "refinement-findings.yaml"
    findings = _load(findings_path)
    findings["review"]["full_review_count"] = 2
    findings["review"]["targeted_verification_count"] = 4
    findings["review"]["completed_assignments"] = [
        {"provider": "claude", "mission": "semantic_core"}
    ]
    output = findings["review"]["outputs"][0]
    findings["review"]["outputs"] = [output, dict(output)]
    output_path = repo / output["path"]
    _write(output_path, "# Review without identity markers\n")
    findings["findings"] = [
        {
            "id": "RF-001",
            "fingerprint": "same",
            "severity": "extreme",
            "category": "invented",
            "status": "corrected",
            "evidence": "",
            "required_correction": "",
            "affected_manifest_ids": ["UNKNOWN"],
            "owner": "",
            "verification_assignments": [
                {"provider": "codex", "mission": "semantic_core"}
            ],
            "closure_test": "",
            "requires_user": "no",
        },
        {
            "id": "RF-001",
            "fingerprint": "same",
            "severity": "minor",
            "category": "testability",
            "status": "verified",
            "evidence": "Observed",
            "affected_manifest_ids": ["AC-001"],
            "owner": "architect",
            "verification_assignments": [
                {"provider": "claude", "mission": "semantic_core"}
            ],
            "closure_test": "Inspect correction",
            "requires_user": False,
        },
        {
            "id": "RF-002",
            "fingerprint": "accepted-risk",
            "severity": "minor",
            "category": "architecture",
            "status": "accepted_risk",
            "evidence": "Residual risk",
            "affected_manifest_ids": ["AC-001"],
            "owner": "user",
            "verification_assignments": [
                {"provider": "claude", "mission": "semantic_core"}
            ],
            "closure_test": "User accepts the risk",
            "requires_user": False,
        },
    ]
    _dump(findings_path, findings)

    errors, _ = _validate(repo, epic, "review")
    joined = "\n".join(errors)
    for expected in (
        "review.full_review_count must be 1",
        "targeted verification count exceeds",
        "completed_assignments do not satisfy profile",
        "duplicate review output paths",
        "review output lacks REVIEW_PROVIDER/REVIEW_MISSION",
        "review.outputs do not cover all assignments",
        "severity must be one of",
        "category must be one of",
        "evidence must be a non-empty string",
        "required_correction must be a non-empty string",
        "correction_evidence must be a non-empty string",
        "verification_evidence must be a non-empty string",
        "references unknown manifest ids",
        "references incomplete assignments",
        "owner must be a non-empty string",
        "closure_test must be a non-empty string",
        "requires_user must be boolean",
        "accepted_risk requires explicit user approval",
        "duplicate finding ids",
        "duplicate finding fingerprints",
    ):
        assert expected in joined


def test_handoff_rejects_active_findings_status_and_decision(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = _load(findings_path)
    findings["findings"] = [
        {
            "id": "RF-001",
            "fingerprint": "delivery-proof",
            "severity": "major",
            "category": "testability",
            "status": "open",
            "evidence": "No integration proof",
            "required_correction": "Add proof",
            "affected_manifest_ids": ["AC-001"],
            "owner": "architect",
            "verification_assignments": [
                {"provider": "claude", "mission": "semantic_core"}
            ],
            "closure_test": "Run proof",
            "requires_user": False,
        }
    ]
    _dump(findings_path, findings)
    _write(
        epic / "details.md",
        "---\nepic_id: E-001\nstatus: draft\n---\n\n# Delivery\n",
    )
    _write(epic / "refinement-review.md", "# Refinement Review\n\nIncomplete\n")

    errors, _ = _validate(repo, epic, "handoff")
    joined = "\n".join(errors)

    assert "remains open at handoff" in joined
    assert "status must be ready-for-implementation" in joined
    assert "must contain 'Decision: Approved for implementation'" in joined


def test_advisories_are_non_blocking_and_metrics_are_recorded(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    details_path = epic / "details.md"
    details = details_path.read_text(encoding="utf-8")
    _write(details_path, details + "\nThe system must preserve this prose.\n")
    metadata = epic / "reviews/refine-v3-001/metadata-claude-semantic_core.yaml"
    _dump(
        metadata,
        {
            "reviews": [
                {
                    "duration_seconds": 12,
                    "retry_count": 0,
                }
            ]
        },
    )

    errors, validator = _validate(repo, epic, "handoff")
    metrics = validator.metrics()

    assert errors == []
    assert any("possible untracked normative statement" in a for a in validator.advisories)
    assert metrics["review_duration_seconds"] == 12
    assert metrics["review_retry_count"] == 0
    assert metrics["review_output_count"] == 1
    assert metrics["review_metadata_count"] == 1
    assert metrics["workflow_elapsed_seconds"] == 600


def test_validator_early_guards_and_yaml_errors(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    invalid_phase = REFINE.RefinementValidator(
        epic, "invented", POLICY_PATH, repo
    ).validate()
    assert invalid_phase == ["unsupported validation phase: invented"]

    missing_epic = REFINE.RefinementValidator(
        repo / "missing", "profile", POLICY_PATH, repo
    ).validate()
    assert any("epic directory does not exist" in e for e in missing_epic)

    missing_repo = REFINE.RefinementValidator(
        epic, "profile", POLICY_PATH, repo / "missing"
    ).validate()
    assert any("repository root does not exist" in e for e in missing_repo)

    bad_policy = tmp_path / "bad-policy.yaml"
    _write(bad_policy, "schema_version: 1\nschema_version: 2\n")
    errors = REFINE.RefinementValidator(epic, "profile", bad_policy, repo).validate()
    assert any("duplicate key" in e for e in errors)

    _write(epic / "refinement-profile.yaml", "epic_id: [unterminated\n")
    errors, _ = _validate(repo, epic, "profile")
    assert any("invalid refinement profile" in e for e in errors)


def test_cli_scaffold_validation_and_metrics(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo, epic = _build_repo(tmp_path)
    metrics_path = tmp_path / "metrics.yaml"

    assert (
        REFINE.main(
            [
                str(epic),
                "--phase",
                "handoff",
                "--policy",
                str(POLICY_PATH),
                "--repo-root",
                str(repo),
                "--scaffold",
                "--metrics-output",
                str(metrics_path),
            ]
        )
        == 0
    )
    assert _load(metrics_path)["phase"] == "handoff"
    assert "Refinement validation passed" in capsys.readouterr().out

    profile_path = epic / "refinement-profile.yaml"
    profile = _load(profile_path)
    profile["schema_version"] = 2
    _dump(profile_path, profile)
    assert (
        REFINE.main(
            [
                str(epic),
                "--phase",
                "profile",
                "--policy",
                str(POLICY_PATH),
                "--repo-root",
                str(repo),
                "--scaffold",
            ]
        )
        == 1
    )
    assert "Refinement scaffold failed" in capsys.readouterr().err


def test_helper_guards_and_scaffold_malformed_rows(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    assert REFINE._infer_repo_root(epic) == repo
    assert REFINE._infer_repo_root(tmp_path / "elsewhere") == Path.cwd().resolve()
    with pytest.raises(ValueError, match="missing fixture"):
        REFINE._load_yaml(tmp_path / "missing.yaml", "fixture")
    non_mapping = tmp_path / "list.yaml"
    _write(non_mapping, "- item\n")
    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        REFINE._load_yaml(non_mapping, "fixture")
    assert (
        REFINE.RefinementScaffolder._line_summary("AC-999", "AC-999")
        == "Complete judgment for AC-999"
    )

    scaffolder = REFINE.RefinementScaffolder(epic, POLICY_PATH, repo)
    trace = scaffolder._traceability(
        _load(epic / "refinement-profile.yaml"),
        {
            "requirements": [
                "bad",
                {"id": "AC-X", "implementation_required": False},
                {"id": 42, "implementation_required": True},
            ]
        },
        tmp_path / "new-traceability.yaml",
    )
    assert trace["acceptance_items"] == []

    _dump(
        epic / "file-plan-story-99.yaml",
        {
            "story_id": 99,
            "proof_obligations": ["bad"],
        },
    )
    _dump(
        epic / "file-plan-story-98.yaml",
        {
            "story_id": "story-98",
            "proof_obligations": ["bad"],
        },
    )
    assert scaffolder._proof_index()["AC-001"][0][0] == "story-01"


def test_policy_shape_profile_shape_and_required_artifact_errors(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))

    malformed_policy = dict(policy)
    malformed_policy["phase_required_artifacts"] = []
    malformed_path = tmp_path / "malformed-policy.yaml"
    _dump(malformed_path, malformed_policy)
    errors = REFINE.RefinementValidator(
        epic, "profile", malformed_path, repo
    ).validate()
    assert "policy phase_required_artifacts must be a mapping" in errors

    missing_phase_policy = dict(policy)
    missing_phase_policy["phase_required_artifacts"] = {}
    missing_phase_path = tmp_path / "missing-phase-policy.yaml"
    _dump(missing_phase_path, missing_phase_policy)
    errors = REFINE.RefinementValidator(
        epic, "profile", missing_phase_path, repo
    ).validate()
    assert any("policy has no artifact list" in error for error in errors)

    bad_artifact_policy = dict(policy)
    bad_artifact_policy["phase_required_artifacts"] = {"profile": [42, "missing.md"]}
    bad_artifact_path = tmp_path / "bad-artifact-policy.yaml"
    _dump(bad_artifact_path, bad_artifact_policy)
    errors = REFINE.RefinementValidator(
        epic, "profile", bad_artifact_path, repo
    ).validate()
    assert sum("missing profile artifact" in error for error in errors) == 2

    profile_path = epic / "refinement-profile.yaml"
    profile = _load(profile_path)
    profile["review"] = []
    _dump(profile_path, profile)
    errors, _ = _validate(repo, epic, "profile")
    assert any("review must be a mapping" in error for error in errors)

    profile["review"] = {
        "assignments": ["bad"],
        "maximum_full_reviews": 9,
        "maximum_targeted_verifications": 9,
    }
    _dump(profile_path, profile)
    errors, _ = _validate(repo, epic, "profile")
    assert any("review.assignments[1] must be a mapping" in error for error in errors)
    assert any("review.maximum_full_reviews must be 1" in error for error in errors)

    profile["review"]["assignments"] = []
    _dump(profile_path, profile)
    errors, _ = _validate(repo, epic, "profile")
    assert any("review.assignments must be a non-empty list" in error for error in errors)


def test_missing_and_malformed_phase_artifacts_report_cleanly(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    (epic / "design.md").unlink()
    errors, _ = _validate(repo, epic, "product")
    assert any("missing product artifact" in error for error in errors)
    assert any("cannot read product artifact" in error for error in errors)

    _write(epic / "design.md", _design("low", []))
    _write(epic / "refinement-manifest.yaml", "requirements: [unterminated\n")
    errors, _ = _validate(repo, epic, "architecture")
    assert any("invalid refinement manifest" in error for error in errors)

    _write(epic / "refinement-manifest.yaml", "{}\n")
    errors, _ = _validate(repo, epic, "architecture")
    assert any("schema_version" in error for error in errors) is False

    repo2, epic2 = _build_repo(tmp_path / "second")
    (epic2 / "file-plan-story-01.yaml").unlink()
    errors, _ = _validate(repo2, epic2, "reconcile")
    assert any("missing implementation boundary plans" in error for error in errors)


def test_ready_status_and_review_output_read_errors(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    validator = REFINE.RefinementValidator(epic, "handoff", POLICY_PATH, repo)

    _write(epic / "details.md", "# No frontmatter\n")
    validator._validate_ready_status()
    assert any("must start with YAML frontmatter" in error for error in validator.errors)

    validator.errors.clear()
    _write(epic / "details.md", "---\nstatus: [unterminated\n---\n")
    validator._validate_ready_status()
    assert any("invalid frontmatter" in error for error in validator.errors)

    validator.errors.clear()
    _write(epic / "details.md", "---\n- list\n---\n")
    validator._validate_ready_status()
    assert any("frontmatter in" in error and "must be a mapping" in error for error in validator.errors)

    validator.errors.clear()
    _write(
        epic / "details.md",
        "---\nepic_id: E-001\nstatus: ready-for-implementation\n---\n",
    )
    (epic / "refinement-review.md").unlink()
    validator._validate_ready_status()
    assert any("cannot read" in error for error in validator.errors)

    validator.errors.clear()
    assert validator._review_markers(epic, epic / "findings.yaml") == {}
    assert any("cannot read review output" in error for error in validator.errors)


def test_metrics_tolerate_invalid_metadata_and_count_findings(tmp_path: Path) -> None:
    repo, epic = _build_repo(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = _load(findings_path)
    findings["review"]["targeted_verification_count"] = 1
    findings["findings"] = [
        {"severity": "major", "category": "architecture"},
        "not-a-row",
    ]
    _dump(findings_path, findings)
    _write(
        epic / "reviews/refine-v3-001/metadata-invalid.yaml",
        "reviews: [unterminated\n",
    )
    _dump(
        epic / "reviews/refine-v3-001/metadata-rows.yaml",
        {"reviews": ["bad", {"duration_seconds": 3, "retry_count": 1}]},
    )
    _dump(
        epic / "reviews/refine-v3-001/metadata-shape.yaml",
        {"reviews": "bad"},
    )
    profile = _load(epic / "refinement-profile.yaml")
    profile["workflow_completed_at"] = "not-a-date"
    _dump(epic / "refinement-profile.yaml", profile)
    details = (epic / "details.md").read_text(encoding="utf-8")
    _write(epic / "details.md", details + "\n".join(["This must be tracked."] * 30))

    _, validator = _validate(repo, epic, "profile")
    metrics = validator.metrics()

    assert len(validator.advisories) == 25
    assert metrics["review_duration_seconds"] == 3
    assert metrics["review_retry_count"] == 1
    assert metrics["targeted_verification_count"] == 1
    assert metrics["findings_by_severity"] == {"major": 1}
    assert metrics["findings_by_category"] == {"architecture": 1}
    assert metrics["workflow_elapsed_seconds"] is None


def test_validation_helpers_cover_source_identity_and_collection_errors(
    tmp_path: Path,
) -> None:
    repo, epic = _build_repo(tmp_path)
    validator = REFINE.RefinementValidator(epic, "architecture", POLICY_PATH, repo)
    validator.policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    validator.profile = {"epic_id": "E-001"}
    marker = epic / "refinement-manifest.yaml"

    validator._validate_source({}, marker, "row")
    validator._validate_source(
        {"artifact": "missing.md", "anchor": "A"}, marker, "row"
    )
    validator._validate_source(
        {"artifact": "acceptance-criteria.md", "anchor": ""}, marker, "row"
    )
    validator._validate_source(
        {"artifact": "acceptance-criteria.md", "anchor": "MISSING"}, marker, "row"
    )
    validator._match_epic_id({"epic_id": "OTHER"}, marker)
    assert validator._resolve_repo_path(str(epic)) == epic
    validator._require_mapping_list({}, "rows", marker, allow_empty=False)
    validator._require_mapping_list(
        {"rows": []}, "rows", marker, allow_empty=False
    )
    validator._require_mapping_list(
        {"rows": ["bad"]}, "rows", marker, allow_empty=True
    )
    validator._require_string_list([], "values", marker, allow_empty=False)
    validator._require_allowed("x", None, "value", marker)
    validator._check_unique([["not-hashable"]], "values", marker)

    joined = "\n".join(validator.errors)
    for expected in (
        "source.artifact must be non-empty",
        "source artifact does not exist",
        "source.anchor must be non-empty",
        "source anchor not found",
        "does not match profile",
        "rows must be a list",
        "rows must not be empty",
        "rows[1] must be a mapping",
        "values must not be empty",
        "policy allowed values",
        "contains a non-scalar value",
    ):
        assert expected in joined


def test_command_and_reviewer_encode_v3_quality_controls() -> None:
    command = COMMAND_PATH.read_text(encoding="utf-8")
    reviewer = REVIEWER_PATH.read_text(encoding="utf-8")

    for expected in (
        "design.md",
        "Phase 2: Evidence-Backed Adversarial Design",
        "Phase 3: Implementation Handoff and Reconciliation",
        "Launch all required assignment commands before waiting",
        "--ignore-user-config",
        "--safe-mode",
        "--retries 0",
        "gpt-5.6-terra",
    ):
        assert expected in command
    assert "pre-review-audit.yaml" in command
    assert "Do not create the removed split epic files" in command
    assert "REVIEW_PROVIDER" in reviewer
    assert "REVIEW_MISSION" in reviewer
    assert "semantic_core" in reviewer
