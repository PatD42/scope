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
ARCHITECT_PATH = REPO_ROOT / "src_shared/agents/architect.md"


def _load_validator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "scope_validate_refinement", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_validator_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _dump(path: Path, value: object) -> None:
    _write(path, yaml.safe_dump(value, sort_keys=False))


def _document(title: str) -> str:
    return f"# {title}\n\nMaterialized test content.\n"


def _build_valid_epic(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    epic = repo / "docs/epics/E-001-adaptive-refinement"
    config_path = repo / "config/e-001.yaml"
    reviewer_output = epic / "reviews/refine-v2-001/implementation-readiness.md"

    _write(
        epic / "details.md",
        "---\nepic_id: E-001\ntitle: Adaptive refinement\n"
        "status: ready-for-implementation\n---\n\n# E-001\n",
    )
    _write(
        epic / "acceptance-criteria.md",
        "# Acceptance Criteria\n\n## AC-001\nBehavior.\n",
    )
    _write(epic / "pdr.md", "# Product Decisions\n\n## PDR-001\nDecision.\n")
    for name in (
        "system-context.md",
        "architecture.md",
        "adr.md",
        "test-strategy.md",
    ):
        _write(epic / name, _document(name))
    _write(config_path, "enabled: true\n")
    _write(
        reviewer_output,
        "# Review\n\nREVIEW_ROLE: implementation_readiness\nDECISION: approved\n",
    )
    _write(
        epic / "refinement-review.md",
        "# Refinement Review\n\nDecision: Approved for implementation\n",
    )

    _dump(
        epic / "refinement-profile.yaml",
        {
            "schema_version": 2,
            "epic_id": "E-001",
            "architecture_scope": "backend",
            "risk_level": "low",
            "capabilities": ["content_configuration"],
            "classification_rationale": "One reversible authored configuration change.",
            "review": {
                "roles": ["implementation_readiness"],
                "maximum_full_reviews": 1,
                "maximum_targeted_verifications": 1,
                "specialist_focus": "none",
            },
        },
    )
    _dump(
        epic / "refinement-manifest.yaml",
        {
            "schema_version": 2,
            "epic_id": "E-001",
            "requirements": [
                {
                    "id": "AC-001",
                    "source": {
                        "artifact": "acceptance-criteria.md",
                        "anchor": "AC-001",
                    },
                    "summary": "Configuration enables the selected behavior.",
                    "type": "behavior",
                    "risk": "low",
                    "implementation_required": True,
                    "affected_surfaces": ["config/e-001.yaml"],
                    "proof_obligations": [
                        "Load the configuration and observe enabled behavior."
                    ],
                    "owner_story": "story-01",
                }
            ],
            "decisions": [
                {
                    "id": "PDR-001",
                    "source": {"artifact": "pdr.md", "anchor": "PDR-001"},
                    "summary": "Use authored configuration.",
                    "status": "accepted",
                }
            ],
            "artifacts": [
                {
                    "id": "ART-001",
                    "path": "config/e-001.yaml",
                    "kind": "authored_config",
                    "capabilities": ["content_configuration"],
                    "authority": "canonical",
                }
            ],
            "open_items": [],
        },
    )
    _dump(
        epic / "file-plan-story-01.yaml",
        {
            "epic_id": "E-001",
            "story_id": "story-01",
            "story_title": "Implement configured behavior",
            "depends_on": [],
            "required_contracts": [],
            "required_touchpoints": [],
            "candidate_files": [],
            "forbidden_changes": [],
            "proof_obligations": [
                {
                    "id": "configured-behavior-proof",
                    "acceptance_rows": ["AC-001"],
                    "required_evidence": "unit",
                    "command_hint": "python3 -m pytest tests/unit/test_config.py",
                    "success_condition": "The configured behavior is enabled.",
                }
            ],
        },
    )
    _dump(
        epic / "acceptance-traceability.yaml",
        {
            "schema_version": 2,
            "epic_id": "E-001",
            "acceptance_items": [
                {
                    "id": "AC-001",
                    "story": "story-01",
                    "requirement": "Configuration enables the selected behavior.",
                    "source": {
                        "artifact": "acceptance-criteria.md",
                        "anchor": "AC-001",
                    },
                    "implementation": {"expected_files": [], "actual_files": []},
                    "tests": {
                        "expected_files": [],
                        "required_assertions": ["Configured behavior is enabled."],
                        "actual_tests": [],
                    },
                    "runtime_evidence": {
                        "required": False,
                        "commands": [],
                        "evidence": [],
                    },
                    "status": "planned",
                    "audit_notes": "",
                }
            ],
        },
    )
    _dump(
        epic / "refinement-findings.yaml",
        {
            "schema_version": 1,
            "epic_id": "E-001",
            "review": {
                "full_review_count": 1,
                "targeted_verification_count": 0,
                "completed_roles": ["implementation_readiness"],
                "outputs": [
                    "docs/epics/E-001-adaptive-refinement/reviews/"
                    "refine-v2-001/implementation-readiness.md"
                ],
            },
            "findings": [],
        },
    )
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    capability_checks = [
        {
            "capability": capability,
            "check_id": check_id,
            "evidence": "The authored configuration and loader contract agree.",
            "status": "passed",
        }
        for capability in ("common", "content_configuration")
        for check_id in policy["pre_review_challenges"][capability]
    ]
    fingerprint_validator = VALIDATOR.RefinementValidator(
        epic_dir=epic,
        phase="architecture",
        policy_path=POLICY_PATH,
        repo_root=repo,
    )
    assert fingerprint_validator.validate() == []
    _dump(
        epic / "reviews/refine-v2-001/pre-review-audit.yaml",
        {
            "schema_version": 1,
            "epic_id": "E-001",
            "input_fingerprint": fingerprint_validator.pre_review_input_fingerprint(),
            "canonical_requirement_source": "acceptance-criteria.md",
            "covered_requirement_ids": ["AC-001"],
            "untracked_normative_statements": [],
            "unindexed_decision_ids": [],
            "contract_flows": [],
            "counterexamples": [],
            "capability_checks": capability_checks,
            "validation_commands": [
                {
                    "command": "python3 -c 'import yaml'",
                    "result": "passed",
                    "evidence": "Configuration parsed successfully.",
                }
            ],
            "unresolved_items": [],
        },
    )
    return repo, epic


def _validate(repo: Path, epic: Path, phase: str = "handoff") -> list[str]:
    validator = VALIDATOR.RefinementValidator(
        epic_dir=epic,
        phase=phase,
        policy_path=POLICY_PATH,
        repo_root=repo,
    )
    return validator.validate()


def _refresh_pre_review_fingerprint(repo: Path, epic: Path) -> None:
    validator = VALIDATOR.RefinementValidator(
        epic_dir=epic,
        phase="architecture",
        policy_path=POLICY_PATH,
        repo_root=repo,
    )
    assert validator.validate() == []
    audit_path = epic / "reviews/refine-v2-001/pre-review-audit.yaml"
    audit = yaml.safe_load(audit_path.read_text(encoding="utf-8"))
    audit["input_fingerprint"] = validator.pre_review_input_fingerprint()
    _dump(audit_path, audit)


def test_valid_low_risk_handoff_passes(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)

    assert _validate(repo, epic) == []


def test_architecture_phase_does_not_require_story_or_review_artifacts(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    for path in (
        epic / "file-plan-story-01.yaml",
        epic / "acceptance-traceability.yaml",
        epic / "refinement-findings.yaml",
        epic / "refinement-review.md",
    ):
        path.unlink()
    details = epic / "details.md"
    details.write_text(details.read_text().replace("ready-for-implementation", "draft"))
    manifest = yaml.safe_load((epic / "refinement-manifest.yaml").read_text())
    manifest["requirements"][0]["owner_story"] = None
    _dump(epic / "refinement-manifest.yaml", manifest)

    assert _validate(repo, epic, phase="architecture") == []


def test_duplicate_yaml_key_is_rejected(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile = epic / "refinement-profile.yaml"
    profile.write_text(profile.read_text() + "epic_id: E-duplicate\n")

    errors = _validate(repo, epic, phase="profile")

    assert any("duplicate key 'epic_id'" in error for error in errors)


def test_native_contract_capability_requires_accepted_artifact_kind(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile = yaml.safe_load((epic / "refinement-profile.yaml").read_text())
    profile["capabilities"] = ["api_interface"]
    _dump(epic / "refinement-profile.yaml", profile)
    manifest = yaml.safe_load((epic / "refinement-manifest.yaml").read_text())
    manifest["artifacts"][0]["capabilities"] = ["api_interface"]
    _dump(epic / "refinement-manifest.yaml", manifest)

    errors = _validate(repo, epic, phase="architecture")

    assert any("api_interface requires one artifact kind" in error for error in errors)


def test_missing_artifact_and_capability_coverage_are_rejected(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    (repo / "config/e-001.yaml").unlink()

    errors = _validate(repo, epic, phase="architecture")

    assert any("artifact path does not exist" in error for error in errors)


@pytest.mark.parametrize(
    ("depends_on", "expected"),
    [
        (["story-99"], "depends on unknown story"),
        (["story-01"], "depends on itself"),
    ],
)
def test_invalid_story_dependency_is_rejected(
    tmp_path: Path,
    depends_on: list[str],
    expected: str,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    plan_path = epic / "file-plan-story-01.yaml"
    plan = yaml.safe_load(plan_path.read_text())
    plan["depends_on"] = depends_on
    _dump(plan_path, plan)

    errors = _validate(repo, epic, phase="pre_review")

    assert any(expected in error for error in errors)


def test_dependency_cycle_is_rejected(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    first_path = epic / "file-plan-story-01.yaml"
    first = yaml.safe_load(first_path.read_text())
    first["depends_on"] = ["story-02"]
    _dump(first_path, first)
    second = dict(first)
    second["story_id"] = "story-02"
    second["story_title"] = "Second story"
    second["depends_on"] = ["story-01"]
    _dump(epic / "file-plan-story-02.yaml", second)

    errors = _validate(repo, epic, phase="pre_review")

    assert any("story dependency cycle" in error for error in errors)


def test_missing_owner_and_traceability_row_are_rejected(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["requirements"][0]["owner_story"] = None
    _dump(manifest_path, manifest)
    traceability_path = epic / "acceptance-traceability.yaml"
    traceability = yaml.safe_load(traceability_path.read_text())
    traceability["acceptance_items"] = [
        {
            **traceability["acceptance_items"][0],
            "id": "AC-OTHER",
        }
    ]
    _dump(traceability_path, traceability)

    errors = _validate(repo, epic, phase="pre_review")

    assert any("missing owner_story" in error for error in errors)
    assert any(
        "missing implementation requirements: AC-001" in error for error in errors
    )


def test_open_manifest_question_blocks_pre_review(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["open_items"] = [
        {
            "id": "OI-001",
            "issue": "Product policy is undecided.",
            "status": "user_question",
        }
    ]
    _dump(manifest_path, manifest)

    errors = _validate(repo, epic, phase="pre_review")

    assert any("remains unresolved at handoff" in error for error in errors)


def test_open_blocking_finding_blocks_handoff(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    findings["findings"] = [
        {
            "id": "RF-001",
            "fingerprint": "architecture-state-owner",
            "severity": "blocking",
            "category": "architecture",
            "status": "open",
            "evidence": "architecture.md does not name the state owner.",
            "required_correction": "Name the state owner in the architecture contract.",
            "affected_manifest_ids": ["AC-001"],
            "owner": "architect",
            "verification_roles": ["implementation_readiness"],
            "closure_test": "Name the owner and verify the native contract.",
            "requires_user": False,
        }
    ]
    _dump(findings_path, findings)

    errors = _validate(repo, epic)

    assert any("remains open at handoff" in error for error in errors)


def test_review_policy_and_output_are_enforced(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    findings["review"]["completed_roles"] = []
    findings["review"]["full_review_count"] = 2
    findings["review"]["outputs"] = ["docs/epics/missing-review.md"]
    _dump(findings_path, findings)

    errors = _validate(repo, epic)

    assert any("missing completed review roles" in error for error in errors)
    assert any("exceeds policy maximum" in error for error in errors)
    assert any("review output does not exist" in error for error in errors)


def test_review_output_must_prove_the_completed_role(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    output = epic / "reviews/refine-v2-001/implementation-readiness.md"
    _write(
        output, "# Review\n\nREVIEW_ROLE: architecture_coherence\nDECISION: approved\n"
    )

    errors = _validate(repo, epic)

    assert any("is not in completed_roles" in error for error in errors)
    assert any(
        "has no review output for roles: implementation_readiness" in error
        for error in errors
    )


def test_duplicate_review_outputs_and_malformed_completed_roles_are_rejected(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    findings["review"]["completed_roles"] = [
        "implementation_readiness",
        {"bad": "role"},
    ]
    findings["review"]["outputs"] *= 2
    _dump(findings_path, findings)

    errors = _validate(repo, epic)

    assert any(
        "completed_roles values must be non-empty strings" in error for error in errors
    )
    assert any("duplicate review outputs" in error for error in errors)


def test_review_output_requires_declared_role_marker(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    output = epic / "reviews/refine-v2-001/implementation-readiness.md"
    _write(output, "# Review\n\nDECISION: approved\n")

    errors = _validate(repo, epic)

    assert any("review output has no valid REVIEW_ROLE" in error for error in errors)


def test_profile_review_budget_cannot_be_below_policy_minimum(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile_path = epic / "refinement-profile.yaml"
    profile = yaml.safe_load(profile_path.read_text())
    profile["review"]["maximum_full_reviews"] = 0
    _dump(profile_path, profile)

    errors = _validate(repo, epic, phase="profile")

    assert any("is below policy minimum" in error for error in errors)


def test_handoff_epic_identity_and_traceability_version_are_enforced(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    plan_path = epic / "file-plan-story-01.yaml"
    plan = yaml.safe_load(plan_path.read_text())
    plan["epic_id"] = "E-WRONG"
    _dump(plan_path, plan)
    traceability_path = epic / "acceptance-traceability.yaml"
    traceability = yaml.safe_load(traceability_path.read_text())
    traceability["schema_version"] = 1
    traceability["epic_id"] = "E-WRONG"
    traceability["acceptance_items"][0]["id"] = "AC-UNKNOWN"
    _dump(traceability_path, traceability)

    errors = _validate(repo, epic, phase="pre_review")

    assert any("file-plan-story-01.yaml epic_id 'E-WRONG'" in error for error in errors)
    assert any("schema_version must be 2" in error for error in errors)
    assert any(
        "acceptance-traceability.yaml epic_id 'E-WRONG'" in error for error in errors
    )
    assert any("unknown manifest requirement 'AC-UNKNOWN'" in error for error in errors)


def test_any_open_finding_blocks_handoff(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    findings["findings"] = [
        {
            "id": "RF-001",
            "fingerprint": "minor-wording-gap",
            "severity": "minor",
            "category": "mechanical",
            "status": "open",
            "evidence": "One handoff label is ambiguous.",
            "required_correction": "Replace the ambiguous handoff label.",
            "affected_manifest_ids": ["AC-001"],
            "owner": "architect",
            "verification_roles": ["implementation_readiness"],
            "closure_test": "Correct or explicitly reject the finding.",
            "requires_user": False,
        }
    ]
    _dump(findings_path, findings)

    errors = _validate(repo, epic)

    assert any("remains open at handoff" in error for error in errors)


def test_review_phase_allows_open_findings_but_handoff_requires_verification(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    finding = {
        "id": "RF-001",
        "fingerprint": "architecture-state-owner",
        "severity": "blocking",
        "category": "architecture",
        "status": "open",
        "evidence": "architecture.md does not name the state owner.",
        "required_correction": "Name the state owner in the native contract.",
        "affected_manifest_ids": ["AC-001"],
        "owner": "architect",
        "verification_roles": ["implementation_readiness"],
        "closure_test": "The architecture and native contract name one owner.",
        "requires_user": False,
    }
    findings["findings"] = [finding]
    _dump(findings_path, findings)

    assert _validate(repo, epic, phase="review") == []

    finding["status"] = "corrected"
    _dump(findings_path, findings)
    errors = _validate(repo, epic, phase="review")

    assert any(
        "correction_evidence must be a non-empty string" in error for error in errors
    )

    finding["correction_evidence"] = "architecture.md now names the repository owner."
    _dump(findings_path, findings)
    errors = _validate(repo, epic)

    assert any("remains corrected at handoff" in error for error in errors)

    finding["status"] = "verified"
    finding["verification_evidence"] = "Targeted reviewer confirmed the owner contract."
    _dump(findings_path, findings)

    assert _validate(repo, epic) == []


def test_high_risk_profile_and_review_allow_two_targeted_verifications(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile_path = epic / "refinement-profile.yaml"
    profile = yaml.safe_load(profile_path.read_text())
    profile["risk_level"] = "high"
    profile["review"]["roles"] = [
        "architecture_coherence",
        "implementation_readiness",
        "capability_specialist",
    ]
    profile["review"]["maximum_targeted_verifications"] = 2
    _dump(profile_path, profile)
    _refresh_pre_review_fingerprint(repo, epic)

    for role in ("architecture_coherence", "capability_specialist"):
        _write(
            epic / f"reviews/refine-v2-001/{role}.md",
            f"# Review\n\nREVIEW_ROLE: {role}\nDECISION: approved\n",
        )
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    findings["review"]["completed_roles"] = profile["review"]["roles"]
    findings["review"]["outputs"].extend(
        [
            "docs/epics/E-001-adaptive-refinement/reviews/"
            "refine-v2-001/architecture_coherence.md",
            "docs/epics/E-001-adaptive-refinement/reviews/"
            "refine-v2-001/capability_specialist.md",
        ]
    )
    findings["review"]["targeted_verification_count"] = 2
    _dump(findings_path, findings)

    assert _validate(repo, epic, phase="review") == []

    findings["review"]["targeted_verification_count"] = 3
    _dump(findings_path, findings)
    errors = _validate(repo, epic, phase="review")

    assert any(
        "targeted_verification_count=3 exceeds policy maximum 2" in error
        for error in errors
    )


def test_high_risk_profile_requires_two_round_allowance(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile_path = epic / "refinement-profile.yaml"
    profile = yaml.safe_load(profile_path.read_text())
    profile["risk_level"] = "high"
    profile["review"]["roles"] = [
        "architecture_coherence",
        "implementation_readiness",
        "capability_specialist",
    ]
    profile["review"]["maximum_targeted_verifications"] = 1
    _dump(profile_path, profile)

    errors = _validate(repo, epic, phase="profile")

    assert any(
        "maximum_targeted_verifications=1 is below policy minimum 2" in error
        for error in errors
    )


def test_stable_error_and_e2e_ids_require_manifest_rows(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    acceptance = epic / "acceptance-criteria.md"
    acceptance.write_text(
        acceptance.read_text()
        + "\n| ERR-001 | Invalid input fails closed |\n"
        + "\n### E2E-001 Complete configured behavior\n\nExercise the workflow.\n"
    )

    errors = _validate(repo, epic, phase="architecture")

    assert any(
        "missing stable acceptance requirements: E2E-001, ERR-001" in error
        for error in errors
    )


def test_pre_review_requires_current_author_challenge_audit(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    audit_path = epic / "reviews/refine-v2-001/pre-review-audit.yaml"
    audit_path.unlink()

    assert _validate(repo, epic, phase="architecture") == []
    errors = _validate(repo, epic, phase="pre_review")
    assert any("missing pre-review audit" in error for error in errors)

    repo, epic = _build_valid_epic(tmp_path / "stale")
    architecture = epic / "architecture.md"
    architecture.write_text(
        architecture.read_text(encoding="utf-8") + "\nChanged contract.\n",
        encoding="utf-8",
    )
    errors = _validate(repo, epic, phase="pre_review")
    assert any("input_fingerprint is stale" in error for error in errors)


def test_high_risk_requirements_need_flows_and_counterexamples(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["requirements"][0]["risk"] = "high"
    _dump(manifest_path, manifest)
    _refresh_pre_review_fingerprint(repo, epic)

    errors = _validate(repo, epic, phase="pre_review")
    assert any(
        "high-risk requirements missing contract flows: AC-001" in error
        for error in errors
    )
    assert any(
        "high-risk requirements missing counterexamples: AC-001" in error
        for error in errors
    )

    audit_path = epic / "reviews/refine-v2-001/pre-review-audit.yaml"
    audit = yaml.safe_load(audit_path.read_text(encoding="utf-8"))
    audit["contract_flows"] = [
        {
            "id": "FLOW-001",
            "requirement_ids": ["AC-001"],
            "authority": "config/e-001.yaml",
            "producer": "configuration author",
            "transport": "configuration loader",
            "state_or_persistence": "in-memory immutable configuration",
            "consumer": "configured service",
            "proof": "configuration loader test",
            "status": "passed",
        }
    ]
    audit["counterexamples"] = [
        {
            "id": "ATTACK-001",
            "requirement_ids": ["AC-001"],
            "invalid_case": "The loader ignores the enabled flag.",
            "rejection_mechanism": "The loader assertion fails.",
            "evidence": "configured-behavior-proof",
            "status": "passed",
        }
    ]
    _dump(audit_path, audit)

    assert _validate(repo, epic, phase="pre_review") == []


def test_story_proof_and_traceability_ownership_must_align(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    plan_path = epic / "file-plan-story-01.yaml"
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["proof_obligations"] = []
    _dump(plan_path, plan)
    _refresh_pre_review_fingerprint(repo, epic)

    errors = _validate(repo, epic, phase="pre_review")
    assert any("AC-001 has no story proof obligation" in error for error in errors)

    repo, epic = _build_valid_epic(tmp_path / "owner")
    second_plan = yaml.safe_load(
        (epic / "file-plan-story-01.yaml").read_text(encoding="utf-8")
    )
    second_plan["story_id"] = "story-02"
    second_plan["story_title"] = "Verify configured behavior"
    second_plan["proof_obligations"] = []
    _dump(epic / "file-plan-story-02.yaml", second_plan)
    trace_path = epic / "acceptance-traceability.yaml"
    trace = yaml.safe_load(trace_path.read_text(encoding="utf-8"))
    trace["acceptance_items"][0]["story"] = "story-02"
    _dump(trace_path, trace)
    _refresh_pre_review_fingerprint(repo, epic)

    errors = _validate(repo, epic, phase="pre_review")
    assert any("does not match manifest owner_story" in error for error in errors)


def test_traceability_requires_assertions_commands_and_manifest_source(
    tmp_path: Path,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    trace_path = epic / "acceptance-traceability.yaml"
    trace = yaml.safe_load(trace_path.read_text(encoding="utf-8"))
    item = trace["acceptance_items"][0]
    item["tests"]["required_assertions"] = []
    item["runtime_evidence"] = {"required": True, "commands": [], "evidence": []}
    item["source"]["anchor"] = "Acceptance Criteria"
    _dump(trace_path, trace)
    _refresh_pre_review_fingerprint(repo, epic)

    errors = _validate(repo, epic, phase="pre_review")
    assert any(
        "tests.required_assertions must not be empty" in error for error in errors
    )
    assert any(
        "runtime_evidence.commands must not be empty" in error for error in errors
    )
    assert any(
        "source does not match manifest requirement source" in error for error in errors
    )


def test_manifest_indexes_all_stable_decisions(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    pdr = epic / "pdr.md"
    pdr.write_text(
        pdr.read_text(encoding="utf-8") + "\n## PDR-002\n\nStatus: Accepted\n",
        encoding="utf-8",
    )

    errors = _validate(repo, epic, phase="architecture")
    assert any("missing stable decisions: PDR-002" in error for error in errors)


def test_command_defines_bounded_convergence_and_targeted_reviewer_scope() -> None:
    command = COMMAND_PATH.read_text(encoding="utf-8")
    reviewer = REVIEWER_PATH.read_text(encoding="utf-8")
    architect = ARCHITECT_PATH.read_text(encoding="utf-8")

    assert "### Bounded correction convergence" in command
    assert "--phase review" in command
    assert "continue without asking the user" in command
    assert "targeted verification remains open" not in command
    assert "one full review" in command
    assert "two for high/critical" in command
    assert "### Pre-review contract challenge" in command
    assert "--print-input-fingerprint" in command
    assert "pre-review audit has the current input fingerprint" in reviewer
    assert "Scope Epic Refine V2 precedence" in architect
    assert "fewest independently verifiable stories" in architect
    assert "Do not restart a\n  broad review" in reviewer
    assert "status: corrected" in reviewer


def test_malformed_pre_review_audit_reports_contract_errors(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    audit_path = epic / "reviews/refine-v2-001/pre-review-audit.yaml"
    audit = yaml.safe_load(audit_path.read_text(encoding="utf-8"))
    audit.update(
        {
            "schema_version": 99,
            "epic_id": "OTHER",
            "input_fingerprint": "stale",
            "canonical_requirement_source": "details.md",
            "covered_requirement_ids": ["AC-UNKNOWN", 2],
            "untracked_normative_statements": ["details.md:1"],
            "unindexed_decision_ids": ["PDR-999"],
            "unresolved_items": ["open"],
            "contract_flows": [
                {
                    "id": "FLOW-001",
                    "requirement_ids": ["AC-UNKNOWN"],
                    "authority": "",
                    "producer": "",
                    "transport": "",
                    "state_or_persistence": "",
                    "consumer": "",
                    "proof": "",
                    "status": "open",
                },
                "not-a-row",
            ],
            "counterexamples": "bad",
            "capability_checks": [
                {
                    "capability": "common",
                    "check_id": "authority-and-ownership",
                    "evidence": "",
                    "status": "open",
                },
                {
                    "capability": "common",
                    "check_id": "authority-and-ownership",
                    "evidence": "duplicate",
                    "status": "passed",
                },
                "not-a-row",
            ],
            "validation_commands": [
                {"command": "", "result": "failed", "evidence": ""},
                "not-a-row",
            ],
        }
    )
    _dump(audit_path, audit)

    errors = _validate(repo, epic, phase="pre_review")
    expected_fragments = (
        "schema_version must be 1",
        "does not match profile",
        "input_fingerprint is stale",
        "canonical_requirement_source must be 'acceptance-criteria.md'",
        "covered_requirement_ids values must be non-empty strings",
        "missing covered implementation requirements: AC-001",
        "covers unknown requirements: AC-UNKNOWN",
        "untracked_normative_statements must be empty",
        "unindexed_decision_ids must be empty",
        "unresolved_items must be empty",
        "contract_flows[2] must be a mapping",
        "counterexamples must be a list",
        "references unknown requirements: AC-UNKNOWN",
        "status must be passed",
        "duplicate capability check",
        "missing capability checks",
        "result must be passed",
        "validation_commands[2] must be a mapping",
    )
    for fragment in expected_fragments:
        assert any(fragment in error for error in errors), fragment


@pytest.mark.parametrize(
    ("details_status", "review_decision", "expected"),
    [
        (
            "draft",
            "Decision: Approved for implementation",
            "status must be ready-for-implementation",
        ),
        (
            "ready-for-implementation",
            "Decision: Pending",
            "must contain 'Decision: Approved",
        ),
    ],
)
def test_ready_markers_are_required(
    tmp_path: Path,
    details_status: str,
    review_decision: str,
    expected: str,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    details = epic / "details.md"
    details.write_text(
        details.read_text().replace("ready-for-implementation", details_status)
    )
    _write(epic / "refinement-review.md", f"# Review\n\n{review_decision}\n")

    errors = _validate(repo, epic)

    assert any(expected in error for error in errors)


def test_cli_main_reports_success_and_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, epic = _build_valid_epic(tmp_path)

    assert (
        VALIDATOR.main(
            [
                str(epic),
                "--phase",
                "handoff",
                "--policy",
                str(POLICY_PATH),
                "--repo-root",
                str(repo),
            ]
        )
        == 0
    )
    assert "Refinement validation passed" in capsys.readouterr().out

    assert (
        VALIDATOR.main(
            [
                str(epic),
                "--phase",
                "architecture",
                "--policy",
                str(POLICY_PATH),
                "--repo-root",
                str(repo),
                "--print-input-fingerprint",
            ]
        )
        == 0
    )
    fingerprint = capsys.readouterr().out.strip()
    assert len(fingerprint) == 64
    int(fingerprint, 16)

    (epic / "refinement-profile.yaml").unlink()
    assert (
        VALIDATOR.main(
            [
                str(epic),
                "--phase",
                "profile",
                "--policy",
                str(POLICY_PATH),
                "--repo-root",
                str(repo),
            ]
        )
        == 1
    )
    assert "Refinement validation failed" in capsys.readouterr().err


def test_validator_early_guards_and_repo_root_inference(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    inferred = VALIDATOR.RefinementValidator(epic, "profile", POLICY_PATH)
    assert inferred.repo_root == repo.resolve()

    outside = tmp_path / "outside"
    outside.mkdir()
    fallback = VALIDATOR.RefinementValidator(outside, "profile", POLICY_PATH)
    assert fallback.repo_root == Path.cwd().resolve()

    invalid_phase = VALIDATOR.RefinementValidator(epic, "unknown", POLICY_PATH, repo)
    assert invalid_phase.validate() == ["unsupported validation phase: unknown"]

    missing_epic = VALIDATOR.RefinementValidator(
        repo / "missing", "profile", POLICY_PATH, repo
    )
    assert "epic directory does not exist" in missing_epic.validate()[0]

    missing_policy = VALIDATOR.RefinementValidator(
        epic, "profile", repo / "missing.yaml", repo
    )
    assert any(
        "missing refinement policy" in error for error in missing_policy.validate()
    )

    invalid_policy = repo / "invalid-policy.yaml"
    _write(invalid_policy, "- not-a-mapping\n")
    invalid = VALIDATOR.RefinementValidator(epic, "profile", invalid_policy, repo)
    assert any("must contain a YAML mapping" in error for error in invalid.validate())


def test_malformed_policy_shapes_are_reported(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    policy = yaml.safe_load(POLICY_PATH.read_text())
    policy["phase_required_artifacts"] = []
    policy["allowed_architecture_scopes"] = "backend"
    policy["capabilities"] = []
    policy["risk_review_policy"] = []
    policy_path = repo / "malformed-policy.yaml"
    _dump(policy_path, policy)

    validator = VALIDATOR.RefinementValidator(epic, "profile", policy_path, repo)
    errors = validator.validate()

    assert any(
        "phase_required_artifacts must be a mapping" in error for error in errors
    )
    assert any("allowed values for architecture_scope" in error for error in errors)
    assert any("policy capabilities must be a mapping" in error for error in errors)
    assert any("risk_review_policy must be a mapping" in error for error in errors)

    policy = yaml.safe_load(POLICY_PATH.read_text())
    policy["phase_required_artifacts"].pop("profile")
    policy["risk_review_policy"]["low"] = []
    _dump(policy_path, policy)
    errors = VALIDATOR.RefinementValidator(
        epic, "profile", policy_path, repo
    ).validate()
    assert any("no artifact list for phase profile" in error for error in errors)
    assert any("no review mapping for risk low" in error for error in errors)


def test_malformed_profile_reports_all_contract_errors(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile_path = epic / "refinement-profile.yaml"
    profile = yaml.safe_load(profile_path.read_text())
    profile.update(
        {
            "schema_version": 99,
            "epic_id": "",
            "classification_rationale": "",
            "architecture_scope": "invalid",
            "risk_level": "invalid",
            "capabilities": ["unknown", "unknown", {"not": "scalar"}],
            "review": {
                "roles": [],
                "maximum_full_reviews": -1,
                "maximum_targeted_verifications": 2,
            },
        }
    )
    _dump(profile_path, profile)

    errors = _validate(repo, epic, phase="profile")

    assert any("schema_version must be 2" in error for error in errors)
    assert any("epic_id must be a non-empty string" in error for error in errors)
    assert any(
        "classification_rationale must be a non-empty string" in error
        for error in errors
    )
    assert any("architecture_scope must be one of" in error for error in errors)
    assert any("risk_level must be one of" in error for error in errors)
    assert any("unknown capability" in error for error in errors)
    assert any("duplicate capabilities" in error for error in errors)
    assert any("contains a non-scalar value" in error for error in errors)
    assert any("review.roles must be a non-empty list" in error for error in errors)
    assert any("must be a non-negative integer" in error for error in errors)

    profile["review"] = "not-a-mapping"
    profile["capabilities"] = "not-a-list"
    _dump(profile_path, profile)
    errors = _validate(repo, epic, phase="profile")
    assert any("capabilities must be a list" in error for error in errors)
    assert any("review must be a mapping" in error for error in errors)


def test_malformed_manifest_rows_are_reported(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    requirement = manifest["requirements"][0]
    requirement.update(
        {
            "id": "",
            "source": "bad-source",
            "summary": "",
            "type": "unknown",
            "risk": "unknown",
            "implementation_required": "yes",
            "affected_surfaces": "bad",
            "proof_obligations": "bad",
        }
    )
    manifest["schema_version"] = 99
    manifest["epic_id"] = "OTHER"
    manifest["requirements"].append("not-a-row")
    manifest["decisions"] = [
        {
            "id": "",
            "source": {"artifact": "missing.md", "anchor": ""},
            "summary": "",
            "status": "",
        },
        "not-a-row",
    ]
    manifest["artifacts"] = [
        {
            "id": "ART-X",
            "path": "missing/artifact.yaml",
            "kind": "",
            "capabilities": "bad",
            "authority": "unknown",
        },
        {
            "id": "ART-X",
            "path": str((repo / "config/e-001.yaml").resolve()),
            "kind": "authored_config",
            "capabilities": ["unknown"],
            "authority": "canonical",
        },
    ]
    manifest["open_items"] = [
        {"id": "", "issue": "", "status": "unknown"},
        "not-a-row",
    ]
    _dump(manifest_path, manifest)

    errors = _validate(repo, epic, phase="architecture")

    expected_fragments = (
        "schema_version must be 2",
        "does not match profile",
        "requirements[2] must be a mapping",
        "source must be a mapping",
        "implementation_required must be boolean",
        "affected_surfaces must be a list",
        "proof_obligations must be a list",
        "source artifact does not exist",
        "artifact path does not exist",
        "capabilities must be a list",
        "references unknown capability",
        "duplicate artifact ids",
        "has no artifact tagged for selected capability",
    )
    for fragment in expected_fragments:
        assert any(fragment in error for error in errors), fragment


def test_missing_and_malformed_boundary_plans_are_reported(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    plan_path = epic / "file-plan-story-01.yaml"
    plan_path.unlink()
    errors = _validate(repo, epic, phase="pre_review")
    assert any("missing implementation boundary plans" in error for error in errors)

    _write(plan_path, "- not-a-mapping\n")
    errors = _validate(repo, epic, phase="pre_review")
    assert any("must contain a YAML mapping" in error for error in errors)

    _dump(
        plan_path,
        {
            "epic_id": "",
            "story_id": "story-01",
            "story_title": "",
            "depends_on": "not-a-list",
            "required_contracts": "bad",
            "required_touchpoints": "bad",
            "candidate_files": "bad",
            "forbidden_changes": "bad",
            "proof_obligations": "bad",
        },
    )
    duplicate = yaml.safe_load(plan_path.read_text())
    duplicate["story_title"] = "Duplicate"
    _dump(epic / "file-plan-story-02.yaml", duplicate)
    errors = _validate(repo, epic, phase="pre_review")
    assert any("depends_on must be a list" in error for error in errors)
    assert any("required_contracts must be a list" in error for error in errors)
    assert any("duplicate story_id" in error for error in errors)


def test_structured_boundary_entries_are_validated(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    plan_path = epic / "file-plan-story-01.yaml"
    plan = yaml.safe_load(plan_path.read_text())
    plan.update(
        {
            "required_contracts": [
                {
                    "id": "contract-1",
                    "contract": "",
                    "obligation": "Honor the authored configuration.",
                    "verification": "python3 -m pytest",
                },
                "not-a-mapping",
            ],
            "required_touchpoints": [
                {
                    "id": "touchpoint-1",
                    "surface": "configuration loader",
                    "obligation": "Load the flag.",
                    "evidence_required": "integration test",
                }
            ],
            "candidate_files": [
                {
                    "path": "src/config.py",
                    "reason": "Existing loader",
                    "advisory": False,
                }
            ],
            "forbidden_changes": [
                {"path_or_surface": "public schema", "rule": "Do not rename fields."}
            ],
            "proof_obligations": [
                {
                    "id": "proof-1",
                    "acceptance_rows": ["AC-UNKNOWN", 2],
                    "required_evidence": "integration",
                    "command_hint": "python3 -m pytest",
                    "success_condition": "The configured behavior is enabled.",
                }
            ],
        }
    )
    _dump(plan_path, plan)

    errors = _validate(repo, epic, phase="pre_review")

    assert any("contract must be a non-empty string" in error for error in errors)
    assert any("required_contracts[2] must be a mapping" in error for error in errors)
    assert any("candidate_files[1] advisory must be true" in error for error in errors)
    assert any("acceptance_rows values must be strings" in error for error in errors)
    assert any("unknown acceptance rows: AC-UNKNOWN" in error for error in errors)


@pytest.mark.parametrize(
    ("scope", "artifact_path", "expected"),
    [
        (
            "backend",
            "docs/architecture/frontend/13-specs/api.yaml",
            "backend architecture",
        ),
        (
            "frontend",
            "docs/architecture/backend/13-specs/api.yaml",
            "frontend architecture",
        ),
        (
            "system",
            "docs/architecture/backend/13-specs/api.yaml",
            "system architecture",
        ),
    ],
)
def test_architecture_artifact_path_must_match_profile_scope(
    tmp_path: Path,
    scope: str,
    artifact_path: str,
    expected: str,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    profile_path = epic / "refinement-profile.yaml"
    profile = yaml.safe_load(profile_path.read_text())
    profile["architecture_scope"] = scope
    _dump(profile_path, profile)
    _write(repo / artifact_path, "contract: test\n")
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["artifacts"][0]["path"] = artifact_path
    _dump(manifest_path, manifest)

    errors = _validate(repo, epic, phase="architecture")

    assert any(expected in error for error in errors)


def test_malformed_traceability_rows_are_reported(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    traceability_path = epic / "acceptance-traceability.yaml"
    traceability = yaml.safe_load(traceability_path.read_text())
    row = traceability["acceptance_items"][0]
    row.update(
        {
            "story": "story-missing",
            "requirement": "",
            "source": "bad",
            "implementation": "bad",
            "tests": "bad",
            "runtime_evidence": "bad",
            "status": "",
        }
    )
    traceability["acceptance_items"].append(dict(row))
    _dump(traceability_path, traceability)

    errors = _validate(repo, epic, phase="pre_review")

    assert any("references unknown story" in error for error in errors)
    assert any("implementation must be a mapping" in error for error in errors)
    assert any("duplicate acceptance traceability ids" in error for error in errors)

    traceability["acceptance_items"] = "not-a-list"
    _dump(traceability_path, traceability)
    errors = _validate(repo, epic, phase="pre_review")
    assert any("acceptance_items must be a list" in error for error in errors)


def test_malformed_findings_and_review_rows_are_reported(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    findings_path = epic / "refinement-findings.yaml"
    findings = yaml.safe_load(findings_path.read_text())
    invalid_finding = {
        "id": "RF-001",
        "fingerprint": "same",
        "severity": "invalid",
        "category": "invalid",
        "status": "invalid",
        "evidence": "",
        "affected_manifest_ids": ["AC-UNKNOWN"],
        "owner": "",
        "closure_test": "",
        "requires_user": "yes",
    }
    findings["findings"] = [invalid_finding, dict(invalid_finding), "not-a-row"]
    findings["review"]["targeted_verification_count"] = -1
    findings["review"]["outputs"] = "not-a-list"
    _dump(findings_path, findings)

    errors = _validate(repo, epic)

    assert any("review.outputs must be a list" in error for error in errors)
    assert any(
        "targeted_verification_count must be a non-negative integer" in error
        for error in errors
    )
    assert any("findings[3] must be a mapping" in error for error in errors)
    assert any("references unknown manifest ids" in error for error in errors)
    assert any("requires_user must be boolean" in error for error in errors)
    assert any("duplicate finding ids" in error for error in errors)
    assert any("duplicate finding fingerprints" in error for error in errors)

    findings["review"] = "not-a-mapping"
    findings["findings"] = []
    _dump(findings_path, findings)
    errors = _validate(repo, epic)
    assert any("review must be a mapping" in error for error in errors)
    assert any("review.completed_roles must be a list" in error for error in errors)


@pytest.mark.parametrize(
    ("details", "remove_review", "expected"),
    [
        ("# No frontmatter\n", False, "must start with YAML frontmatter"),
        ("---\nstatus: [\n---\n", False, "invalid frontmatter"),
        ("---\n- list\n---\n", False, "frontmatter in"),
        (
            "---\nepic_id: E-001\ntitle: Test\nstatus: ready-for-implementation\n---\n",
            True,
            "cannot read",
        ),
    ],
)
def test_malformed_ready_artifacts_are_reported(
    tmp_path: Path,
    details: str,
    remove_review: bool,
    expected: str,
) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    _write(epic / "details.md", details)
    if remove_review:
        (epic / "refinement-review.md").unlink()

    errors = _validate(repo, epic)

    assert any(expected in error for error in errors)


def test_absolute_and_repo_relative_sources_are_supported(tmp_path: Path) -> None:
    repo, epic = _build_valid_epic(tmp_path)
    manifest_path = epic / "refinement-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["requirements"][0]["source"]["artifact"] = str(
        (epic / "acceptance-criteria.md").resolve()
    )
    manifest["decisions"][0]["source"]["artifact"] = (
        "docs/epics/E-001-adaptive-refinement/pdr.md"
    )
    _dump(manifest_path, manifest)

    assert _validate(repo, epic, phase="architecture") == []
