import base64
import json

FULL_SHA = "a" * 40


def _json(value):
    return json.loads(value) if isinstance(value, str) else value


def _warp(direct_vm, value="2026-09-12T10:00:00Z"):
    direct_vm.warp(value)


def _create_program(contract, direct_vm, grantor, recipient):
    _warp(direct_vm)
    direct_vm.sender = grantor
    return _json(contract.create_program(str(recipient), "Siriron/grantseal", "GrantSeal", "Test grant program"))


def _make_active(contract, direct_vm, grantor, recipient):
    _create_program(contract, direct_vm, grantor, recipient)
    direct_vm.sender = grantor
    contract.define_milestone(1, "Ship contract", json.dumps(["Contract source exists", "Tests exist"]))
    contract.lock_program(1)
    direct_vm.sender = recipient
    contract.accept_program(1)


def test_program_and_milestone_storage_persist_with_pickling(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.check_pickling = True
    contract = direct_deploy("contracts/grantseal.py")
    created = _create_program(contract, direct_vm, direct_alice, direct_bob)
    assert created["program_id"] == 1
    program = _json(contract.get_program(1))
    assert program["status"] == "DRAFT"
    assert program["repo_id"] == "Siriron/grantseal"

    direct_vm.sender = direct_alice
    contract.define_milestone(1, "Milestone", json.dumps(["A real criterion"]))
    program = _json(contract.get_program(1))
    milestone = _json(contract.get_milestone(1))
    assert program["milestone_count"] == 1
    assert milestone["program_id"] == 1
    assert milestone["criteria"] == ["A real criterion"]


def test_authorization_and_lifecycle(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = direct_deploy("contracts/grantseal.py")
    _create_program(contract, direct_vm, direct_alice, direct_bob)

    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only grantor"):
        contract.define_milestone(1, "Nope", json.dumps(["Nope"]))

    direct_vm.sender = direct_alice
    contract.define_milestone(1, "M1", json.dumps(["Criterion"]))
    contract.lock_program(1)

    with direct_vm.expect_revert("only recipient"):
        contract.accept_program(1)

    direct_vm.sender = direct_bob
    contract.accept_program(1)
    assert _json(contract.get_program(1))["status"] == "ACTIVE"


def test_sha_requires_exact_full_commit_identity(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("invalid commit SHA"):
        contract.submit_milestone(1, "abcdef0", "short prefix")
    with direct_vm.expect_revert("invalid commit SHA"):
        contract.submit_milestone(1, "HEAD", "mutable ref")
    contract.submit_milestone(1, FULL_SHA, "exact object identity")
    assert _json(contract.get_milestone(1))["commit_sha"] == FULL_SHA


def test_challenge_response_deadline_and_authorization(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")

    with direct_vm.expect_revert("recipient cannot challenge"):
        contract.challenge_milestone(1, "self challenge")

    direct_vm.sender = direct_charlie
    contract.challenge_milestone(1, "criterion appears incomplete")
    direct_vm.sender = direct_bob
    contract.respond_to_challenge(1, "response")

    _warp(direct_vm, "2026-09-16T10:00:01Z")
    with direct_vm.expect_revert("response window closed"):
        contract.respond_to_challenge(1, "late")


def _mock_resolution_evidence(direct_vm, repo="Siriron/grantseal", sha=FULL_SHA):
    tree_sha = "b" * 40
    blob_sha = "c" * 40
    direct_vm.mock_web(r"https://api\\.github\\.com/repos/Siriron/grantseal$", {
        "status": 200, "body": json.dumps({"full_name": repo})
    })
    direct_vm.mock_web(r"/commits/" + sha, {
        "status": 200,
        "body": json.dumps({
            "sha": sha,
            "commit": {"tree": {"sha": tree_sha}},
            "files": [{"filename": "contracts/grantseal.py"}],
        }),
    })
    direct_vm.mock_web(r"/git/trees/" + tree_sha, {
        "status": 200,
        "body": json.dumps({"sha": tree_sha, "tree": [{"type": "blob", "path": "contracts/grantseal.py", "sha": blob_sha}]}),
    })
    encoded = base64.b64encode(b"# GrantSeal contract\n# criterion evidence\n").decode()
    direct_vm.mock_web(r"/git/blobs/" + blob_sha, {
        "status": 200, "body": json.dumps({"sha": blob_sha, "encoding": "base64", "content": encoded})
    })
    direct_vm.mock_llm(r".*", json.dumps({"outcome": "MET"}))


def test_resolution_uses_bounded_exact_sha_evidence(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    result = _json(contract.resolve_milestone(1))
    assert result["outcome"] == "MET"
    assert _json(contract.get_program(1))["resolved_milestone_count"] == 1


def test_inadequate_evidence_returns_inconclusive(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    direct_vm.mock_web(r"https://api\\.github\\.com/repos/Siriron/grantseal$", {"status": 404, "body": "{}"})
    direct_vm.sender = direct_alice
    result = _json(contract.resolve_milestone(1))
    assert result["outcome"] == "INCONCLUSIVE"


def test_single_appeal_and_closure_rules(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_milestone(1)

    direct_vm.sender = direct_bob
    contract.appeal_milestone(1, "fresh appeal")
    assert _json(contract.get_program(1))["resolved_milestone_count"] == 0

    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_appeal(1)
    assert _json(contract.get_program(1))["resolved_milestone_count"] == 1

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("single appeal already used"):
        contract.appeal_milestone(1, "second appeal")

    direct_vm.sender = direct_alice
    contract.close_program(1)
    assert _json(contract.get_program(1))["status"] == "CLOSED"


def test_create_program_normalizes_studio_integer_address(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.check_pickling = True
    contract = direct_deploy("contracts/grantseal.py")
    direct_vm.sender = direct_alice
    recipient_int = int(str(direct_bob).removeprefix("0x"), 16)
    created = _json(contract.create_program(recipient_int, "Siriron/grantseal", "GrantSeal", "Integer address regression"))
    assert created["program_id"] == 1
    program = _json(contract.get_program(1))
    assert program["recipient"].lower() == str(direct_bob).lower()


def test_resolution_is_blocked_until_response_deadline(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("response window still open"):
        contract.resolve_milestone(1)


def test_close_requires_every_milestone_resolved(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _create_program(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    contract.define_milestone(1, "M1", json.dumps(["Criterion one"]))
    contract.define_milestone(1, "M2", json.dumps(["Criterion two"]))
    contract.lock_program(1)
    direct_vm.sender = direct_bob
    contract.accept_program(1)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("all program milestones must be terminally resolved"):
        contract.close_program(1)


def test_milestone_counts_increment_and_appeal_temporarily_decrements_resolved_count(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_milestone(1)
    assert _json(contract.get_program(1))["resolved_milestone_count"] == 1
    direct_vm.sender = direct_bob
    contract.appeal_milestone(1, "appeal")
    assert _json(contract.get_program(1))["resolved_milestone_count"] == 0


def test_appeal_window_expires(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_milestone(1)
    _warp(direct_vm, "2026-09-18T10:00:02Z")
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("appeal window closed"):
        contract.appeal_milestone(1, "late appeal")


def test_resolution_rejects_repository_identity_mismatch(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    direct_vm.mock_web(r"https://api\\.github\\.com/repos/Siriron/grantseal$", {
        "status": 200, "body": json.dumps({"full_name": "someone-else/grantseal"})
    })
    direct_vm.mock_web(r"/commits/" + FULL_SHA, {
        "status": 200, "body": json.dumps({"sha": FULL_SHA, "commit": {"tree": {"sha": "b" * 40}}})
    })
    direct_vm.sender = direct_alice
    result = _json(contract.resolve_milestone(1))
    assert result["outcome"] == "INCONCLUSIVE"


def test_only_recipient_or_challenger_can_appeal(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = direct_deploy("contracts/grantseal.py")
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_milestone(1)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only recipient or challenger may appeal"):
        contract.appeal_milestone(1, "unauthorized")
