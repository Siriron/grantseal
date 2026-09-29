import base64
import json
import sys

import pytest

FULL_SHA = "a" * 40


RESPONSE_WINDOW = 3 * 24 * 60 * 60   # production defaults; the windows are deploy-time constructor args
APPEAL_WINDOW = 2 * 24 * 60 * 60


def _addr(account):
    """Test accounts are raw bytes in genlayer-test; Studio and the CLI pass 0x-hex strings."""
    if isinstance(account, (bytes, bytearray)):
        return "0x" + bytes(account).hex()
    return str(account)


def _deploy(direct_deploy, response=RESPONSE_WINDOW, appeal=APPEAL_WINDOW):
    return direct_deploy("contracts/grantseal.py", response, appeal)


def _json(value):
    return json.loads(value) if isinstance(value, str) else value


def _warp(direct_vm, value="2026-09-12T10:00:00Z"):
    """Set the transaction timestamp the contract sees.

    The contract reads gl.message_raw["datetime"]. genlayer-test 0.29.2's warp() only patches
    datetime.datetime.now() and refreshes sender/origin on gl.message_raw, so it never updates
    "datetime". We set it on the same mutable dict the harness already writes sender/origin to.
    """
    direct_vm.warp(value)
    sys.modules["genlayer.gl"].message_raw["datetime"] = value


def _create_program(contract, direct_vm, grantor, recipient):
    _warp(direct_vm)
    direct_vm.sender = grantor
    return _json(contract.create_program(_addr(recipient), "Siriron/grantseal", "GrantSeal", "Test grant program"))


def _make_active(contract, direct_vm, grantor, recipient):
    _create_program(contract, direct_vm, grantor, recipient)
    direct_vm.sender = grantor
    contract.define_milestone(1, "Ship contract", json.dumps(["Contract source exists", "Tests exist"]))
    contract.lock_program(1)
    direct_vm.sender = recipient
    contract.accept_program(1)


def test_program_and_milestone_storage_persist_with_pickling(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.check_pickling = True
    contract = _deploy(direct_deploy)
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
    contract = _deploy(direct_deploy)
    _create_program(contract, direct_vm, direct_alice, direct_bob)

    direct_vm.sender = direct_charlie
    with pytest.raises(AssertionError, match="only grantor"):
        contract.define_milestone(1, "Nope", json.dumps(["Nope"]))

    direct_vm.sender = direct_alice
    contract.define_milestone(1, "M1", json.dumps(["Criterion"]))
    contract.lock_program(1)

    with pytest.raises(AssertionError, match="only recipient"):
        contract.accept_program(1)

    direct_vm.sender = direct_bob
    contract.accept_program(1)
    assert _json(contract.get_program(1))["status"] == "ACTIVE"


def test_sha_requires_exact_full_commit_identity(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    with pytest.raises(AssertionError, match="invalid commit SHA"):
        contract.submit_milestone(1, "abcdef0", "short prefix")
    with pytest.raises(AssertionError, match="invalid commit SHA"):
        contract.submit_milestone(1, "HEAD", "mutable ref")
    contract.submit_milestone(1, FULL_SHA, "exact object identity")
    assert _json(contract.get_milestone(1))["commit_sha"] == FULL_SHA


def test_challenge_response_deadline_and_authorization(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")

    with pytest.raises(AssertionError, match="recipient cannot challenge"):
        contract.challenge_milestone(1, "self challenge")

    direct_vm.sender = direct_charlie
    contract.challenge_milestone(1, "criterion appears incomplete")
    direct_vm.sender = direct_bob
    contract.respond_to_challenge(1, "response")

    _warp(direct_vm, "2026-09-16T10:00:01Z")
    with pytest.raises(AssertionError, match="response window closed"):
        contract.respond_to_challenge(1, "late")


def _mock_resolution_evidence(direct_vm, repo="Siriron/grantseal", sha=FULL_SHA, outcome="MET", repo_status=200):
    tree_sha = "b" * 40
    blob_sha = "c" * 40
    direct_vm.mock_web(r"https://api\.github\.com/repos/Siriron/grantseal$", {
        "status": repo_status, "body": json.dumps({"full_name": repo})
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
    direct_vm.mock_llm(r".*", json.dumps({"outcome": outcome}))


def test_resolution_uses_bounded_exact_sha_evidence(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
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
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    direct_vm.mock_web(r"https://api\.github\.com/repos/Siriron/grantseal$", {"status": 404, "body": "{}"})
    direct_vm.sender = direct_alice
    result = _json(contract.resolve_milestone(1))
    assert result["outcome"] == "INCONCLUSIVE"


def test_single_appeal_and_closure_rules(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
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
    with pytest.raises(AssertionError, match="single appeal already used"):
        contract.appeal_milestone(1, "second appeal")

    direct_vm.sender = direct_alice
    contract.close_program(1)
    assert _json(contract.get_program(1))["status"] == "CLOSED"


def test_create_program_normalizes_studio_integer_address(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.check_pickling = True
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_alice
    recipient_int = int(_addr(direct_bob).removeprefix("0x"), 16)
    created = _json(contract.create_program(recipient_int, "Siriron/grantseal", "GrantSeal", "Integer address regression"))
    assert created["program_id"] == 1
    program = _json(contract.get_program(1))
    assert program["recipient"].lower() == _addr(direct_bob).lower()


def test_resolution_is_blocked_until_response_deadline(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    direct_vm.sender = direct_alice
    with pytest.raises(AssertionError, match="response window still open"):
        contract.resolve_milestone(1)


def test_close_requires_every_milestone_resolved(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _create_program(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    contract.define_milestone(1, "M1", json.dumps(["Criterion one"]))
    contract.define_milestone(1, "M2", json.dumps(["Criterion two"]))
    contract.lock_program(1)
    direct_vm.sender = direct_bob
    contract.accept_program(1)
    direct_vm.sender = direct_alice
    with pytest.raises(AssertionError, match="all program milestones must be terminally resolved"):
        contract.close_program(1)


def test_milestone_counts_increment_and_appeal_temporarily_decrements_resolved_count(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
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
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_milestone(1)
    _warp(direct_vm, "2026-09-18T10:00:02Z")
    direct_vm.sender = direct_bob
    with pytest.raises(AssertionError, match="appeal window closed"):
        contract.appeal_milestone(1, "late appeal")


def test_resolution_rejects_repository_identity_mismatch(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    direct_vm.mock_web(r"https://api\.github\.com/repos/Siriron/grantseal$", {
        "status": 200, "body": json.dumps({"full_name": "someone-else/grantseal"})
    })
    direct_vm.mock_web(r"/commits/" + FULL_SHA, {
        "status": 200, "body": json.dumps({"sha": FULL_SHA, "commit": {"tree": {"sha": "b" * 40}}})
    })
    direct_vm.sender = direct_alice
    result = _json(contract.resolve_milestone(1))
    assert result["outcome"] == "INCONCLUSIVE"


def test_only_recipient_or_challenger_can_appeal(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    _mock_resolution_evidence(direct_vm)
    direct_vm.sender = direct_alice
    contract.resolve_milestone(1)
    direct_vm.sender = direct_charlie
    with pytest.raises(AssertionError, match="only recipient or challenger may appeal"):
        contract.appeal_milestone(1, "unauthorized")


# ----------------------------------------------------------------------------------------------
# Added for the Sep 2026 steward re-review. Each test below executes the real contract.
# ----------------------------------------------------------------------------------------------
import datetime as _dt


def _epoch(iso):
    return int(_dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc).timestamp())


def _submitted(contract, direct_vm, alice, bob):
    _make_active(contract, direct_vm, alice, bob)
    direct_vm.sender = bob
    contract.submit_milestone(1, FULL_SHA, "submission")


def _resolve(contract, direct_vm, alice, outcome, when="2026-09-16T10:00:01Z", **kw):
    _warp(direct_vm, when)
    direct_vm.clear_mocks()
    _mock_resolution_evidence(direct_vm, outcome=outcome, **kw)
    direct_vm.sender = alice
    return _json(contract.resolve_milestone(1))


@pytest.mark.parametrize("outcome", ["MET", "PARTIALLY_MET", "NOT_MET", "INCONCLUSIVE"])
def test_every_outcome_is_reachable_from_the_model_answer(direct_vm, direct_deploy, direct_alice, direct_bob, outcome):
    """Regression: exec_prompt(response_format='json') returns a dict. json.loads(dict) used to raise
    TypeError, which was swallowed into INCONCLUSIVE, so no other outcome was ever reachable."""
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    result = _resolve(contract, direct_vm, direct_alice, outcome)
    assert result["outcome"] == outcome
    assert _json(contract.get_milestone(1))["outcome"] == outcome


def test_outcome_is_case_and_spacing_tolerant(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    assert _resolve(contract, direct_vm, direct_alice, "partially met")["outcome"] == "PARTIALLY_MET"


@pytest.mark.parametrize("bad", ['{"outcome": "APPROVED"}', '{"verdict": "MET"}', "[]", '"MET"', "not json at all"])
def test_unusable_model_answer_fails_closed_to_inconclusive(direct_vm, direct_deploy, direct_alice, direct_bob, bad):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    _warp(direct_vm, "2026-09-16T10:00:01Z")
    direct_vm.clear_mocks()
    _mock_resolution_evidence(direct_vm)
    direct_vm.clear_llm_mocks() if hasattr(direct_vm, "clear_llm_mocks") else direct_vm._llm_mocks.clear()
    direct_vm.mock_llm(r".*", bad)
    direct_vm.sender = direct_alice
    assert _json(contract.resolve_milestone(1))["outcome"] == "INCONCLUSIVE"


@pytest.mark.parametrize("status", [403, 404, 500])
def test_http_error_never_becomes_evidence(direct_vm, direct_deploy, direct_alice, direct_bob, status):
    """Regression for the status_code bug: SDK responses expose .status. An HTTP error whose body
    still looks like a valid repo record must not bind the repository, so the model is never asked."""
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    result = _resolve(contract, direct_vm, direct_alice, "MET", repo_status=status)
    assert result["outcome"] == "INCONCLUSIVE"


def test_repository_identity_mismatch_is_inconclusive_even_if_model_says_met(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    assert _resolve(contract, direct_vm, direct_alice, "MET", repo="someone-else/grantseal")["outcome"] == "INCONCLUSIVE"


def test_appeal_is_an_independent_round_that_can_overturn_the_first_outcome(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    assert _resolve(contract, direct_vm, direct_alice, "MET")["outcome"] == "MET"
    direct_vm.sender = direct_bob
    contract.appeal_milestone(1, "please re-check")
    direct_vm.clear_mocks()
    _mock_resolution_evidence(direct_vm, outcome="NOT_MET")
    direct_vm.sender = direct_alice
    result = _json(contract.resolve_appeal(1))
    assert result["outcome"] == "NOT_MET" and result["appeal"] is True
    milestone = _json(contract.get_milestone(1))
    assert milestone["outcome"] == "NOT_MET" and milestone["appeal_outcome"] == "NOT_MET"


# ---- deploy-time windows ---------------------------------------------------------------------
def test_get_config_reports_the_deployed_windows(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/grantseal.py", 600, 900)
    assert _json(contract.get_config()) == {"response_window_seconds": 600, "appeal_window_seconds": 900}


@pytest.mark.parametrize("response,appeal,message", [
    (59, 900, "response window out of range"),
    (600, 59, "appeal window out of range"),
    (31 * 24 * 60 * 60, 900, "response window out of range"),
    (600, 31 * 24 * 60 * 60, "appeal window out of range"),
    (0, 0, "out of range"),
])
def test_window_bounds_are_enforced_at_deploy(direct_vm, direct_deploy, response, appeal, message):
    with pytest.raises(AssertionError, match=message):
        direct_deploy("contracts/grantseal.py", response, appeal)


def test_short_windows_are_enforced_to_the_second(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy("contracts/grantseal.py", 120, 300)
    _make_active(contract, direct_vm, direct_alice, direct_bob)   # warps to 2026-09-12T10:00:00Z
    direct_vm.sender = direct_bob
    submitted = _json(contract.submit_milestone(1, FULL_SHA, "submission"))
    assert submitted["response_deadline"] == _epoch("2026-09-12T10:00:00Z") + 120

    _warp(direct_vm, "2026-09-12T10:02:00Z")           # exactly at the deadline: still open
    direct_vm.sender = direct_alice
    with pytest.raises(AssertionError, match="response window still open"):
        contract.resolve_milestone(1)

    result = _resolve(contract, direct_vm, direct_alice, "MET", when="2026-09-12T10:02:01Z")
    assert result["outcome"] == "MET"
    assert _json(contract.get_milestone(1))["appeal_deadline"] == _epoch("2026-09-12T10:02:01Z") + 300

    _warp(direct_vm, "2026-09-12T10:07:02Z")           # one second past the appeal window
    direct_vm.sender = direct_bob
    with pytest.raises(AssertionError, match="appeal window closed"):
        contract.appeal_milestone(1, "too late")


def test_challenge_and_response_must_land_inside_the_short_window(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = direct_deploy("contracts/grantseal.py", 120, 300)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    _warp(direct_vm, "2026-09-12T10:01:00Z")
    direct_vm.sender = direct_charlie
    contract.challenge_milestone(1, "inside the window")
    direct_vm.sender = direct_bob
    contract.respond_to_challenge(1, "inside the window")
    _warp(direct_vm, "2026-09-12T10:02:01Z")
    direct_vm.sender = direct_bob
    with pytest.raises(AssertionError, match="response window closed"):
        contract.respond_to_challenge(1, "too late")


# ---- consensus logic (validator re-derivation) -----------------------------------------------
def test_validator_agrees_when_it_independently_reaches_the_same_result(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    _resolve(contract, direct_vm, direct_alice, "PARTIALLY_MET")
    assert direct_vm.run_validator() is True


def test_validator_rejects_a_different_outcome(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    _resolve(contract, direct_vm, direct_alice, "MET")
    direct_vm.clear_mocks()
    _mock_resolution_evidence(direct_vm, outcome="NOT_MET")     # validator's own model disagrees
    assert direct_vm.run_validator() is False


def test_validator_rejects_when_only_the_binding_evidence_differs(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    _resolve(contract, direct_vm, direct_alice, "MET")
    direct_vm.clear_mocks()
    _mock_resolution_evidence(direct_vm, outcome="MET", repo_status=404)   # validator cannot bind the repo
    assert direct_vm.run_validator() is False


def test_validator_rejects_a_leader_that_errored_or_returned_junk(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    _resolve(contract, direct_vm, direct_alice, "MET")
    assert direct_vm.run_validator(leader_error=Exception("boom")) is False
    assert direct_vm.run_validator(leader_result="MET") is False
    assert direct_vm.run_validator(leader_result={"outcome": "APPROVED", "repo_bound": True, "commit_bound": True, "coverage": True}) is False


def test_no_storage_object_crosses_into_the_nondet_closures(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.check_pickling = True
    contract = _deploy(direct_deploy)
    _submitted(contract, direct_vm, direct_alice, direct_bob)
    assert _resolve(contract, direct_vm, direct_alice, "MET")["outcome"] == "MET"
    direct_vm.sender = direct_bob
    contract.appeal_milestone(1, "again")
    direct_vm.clear_mocks()
    _mock_resolution_evidence(direct_vm, outcome="MET")
    direct_vm.sender = direct_alice
    assert _json(contract.resolve_appeal(1))["outcome"] == "MET"


def test_unauthorised_and_wrong_state_calls_are_rejected(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = _deploy(direct_deploy)
    _make_active(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_charlie
    with pytest.raises(AssertionError, match="only recipient"):
        contract.submit_milestone(1, FULL_SHA, "not the recipient")
    direct_vm.sender = direct_bob
    contract.submit_milestone(1, FULL_SHA, "submission")
    with pytest.raises(AssertionError, match="milestone already submitted"):
        contract.submit_milestone(1, FULL_SHA, "again")
    with pytest.raises(AssertionError, match="recipient cannot challenge own submission"):
        contract.challenge_milestone(1, "self challenge")
    direct_vm.sender = direct_alice
    with pytest.raises(AssertionError, match="no active challenge"):
        contract.respond_to_challenge(1, "nothing to answer")
    with pytest.raises(AssertionError, match="milestone not appealable"):
        contract.appeal_milestone(1, "not resolved yet")
