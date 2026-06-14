from modules.territorial_risk.domain.explainability import decompose_relative_mortality_score


def test_decompose_relative_mortality_score_returns_bounded_contributions() -> None:
    contributions = decompose_relative_mortality_score(
        observed_value=10.0,
        baseline_value=8.0,
        ratio=1.25,
    )
    assert len(contributions) == 3
    assert contributions[0].contribution == 50.0
    assert contributions[-1].contribution == 62.5
