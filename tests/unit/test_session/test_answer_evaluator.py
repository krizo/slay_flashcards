from learning.sessions.test_session import TestSessionConfig, AnswerEvaluation, AnswerEvaluator


def test_answer_evaluator_exact_match(default_test_config):
    """Test exact answer matching."""
    evaluator = AnswerEvaluator(default_test_config)

    evaluation, score = evaluator.evaluate_answer("chien", "chien")

    assert evaluation == AnswerEvaluation.CORRECT
    assert score == 1.0


def test_answer_evaluator_case_insensitive_match(default_test_config):
    """Test case-insensitive matching."""
    evaluator = AnswerEvaluator(default_test_config)

    evaluation, score = evaluator.evaluate_answer("CHIEN", "chien")

    assert evaluation == AnswerEvaluation.CORRECT
    assert score == 1.0


def test_answer_evaluator_case_sensitive_mismatch(strict_test_config):
    """Test case-sensitive matching fails with different case."""
    evaluator = AnswerEvaluator(strict_test_config)

    evaluation, score = evaluator.evaluate_answer("CHIEN", "chien")

    assert evaluation == AnswerEvaluation.INCORRECT
    assert score == 0.0


def test_answer_evaluator_punctuation_normalization(default_test_config):
    """Test punctuation is properly normalized."""
    evaluator = AnswerEvaluator(default_test_config)

    test_cases = [
        ("chien.", "chien"),
        ("chien!", "chien"),
        ("chien?", "chien"),
        ("chien;", "chien"),
        ("chien:", "chien"),
    ]

    for user_answer, correct_answer in test_cases:
        evaluation, score = evaluator.evaluate_answer(user_answer, correct_answer)
        assert evaluation == AnswerEvaluation.CORRECT
        assert score == 1.0


def test_answer_evaluator_whitespace_normalization(default_test_config):
    """Test whitespace is properly normalized."""
    evaluator = AnswerEvaluator(default_test_config)

    test_cases = [
        ("  chien  ", "chien"),
        ("le   chien", "le chien"),
        ("\t chien \n", "chien"),
    ]

    for user_answer, correct_answer in test_cases:
        evaluation, score = evaluator.evaluate_answer(user_answer, correct_answer)
        assert evaluation == AnswerEvaluation.CORRECT
        assert score == 1.0


def test_answer_evaluator_strict_matching_rejects_typos():
    """Test strict matching mode rejects typos."""
    config = TestSessionConfig(strict_matching=True, case_sensitive=False)
    evaluator = AnswerEvaluator(config)

    evaluation, score = evaluator.evaluate_answer("chein", "chien")

    assert evaluation == AnswerEvaluation.INCORRECT
    assert score == 0.0


def test_answer_evaluator_fuzzy_matching_typos(default_test_config):
    """Test fuzzy matching gives partial credit for typos."""
    evaluator = AnswerEvaluator(default_test_config)

    evaluation, score = evaluator.evaluate_answer("chein", "chien")

    assert evaluation == AnswerEvaluation.PARTIAL
    assert 0.7 < score < 1.0  # Should get significant partial credit


def test_answer_evaluator_completely_wrong_answer(default_test_config):
    """Test completely wrong answers get zero score."""
    evaluator = AnswerEvaluator(default_test_config)

    evaluation, score = evaluator.evaluate_answer("cat", "chien")

    assert evaluation == AnswerEvaluation.INCORRECT
    assert score == 0.0


def test_answer_evaluator_empty_answer(default_test_config):
    """Test empty answers are handled correctly."""
    evaluator = AnswerEvaluator(default_test_config)

    test_cases = ["", "   ", "\t", "\n"]

    for empty_answer in test_cases:
        evaluation, score = evaluator.evaluate_answer(empty_answer, "chien")
        assert evaluation == AnswerEvaluation.INCORRECT
        assert score == 0.0


def test_answer_evaluator_similarity_threshold():
    """Test similarity threshold affects partial credit."""
    # Lenient threshold
    lenient_config = TestSessionConfig(
        strict_matching=False,
        similarity_threshold=0.6,
        allow_partial_credit=True
    )
    lenient_evaluator = AnswerEvaluator(lenient_config)

    # Strict threshold
    strict_config = TestSessionConfig(
        strict_matching=False,
        similarity_threshold=0.9,
        allow_partial_credit=True
    )
    strict_evaluator = AnswerEvaluator(strict_config)

    # Test with a moderately similar answer
    user_answer = "chein"
    correct_answer = "chien"

    lenient_eval, lenient_score = lenient_evaluator.evaluate_answer(user_answer, correct_answer)
    strict_eval, strict_score = strict_evaluator.evaluate_answer(user_answer, correct_answer)

    # Lenient should give partial credit
    assert lenient_eval == AnswerEvaluation.PARTIAL
    assert lenient_score > 0.6

    # Strict might reject it entirely or give lower score
    assert strict_eval in [AnswerEvaluation.INCORRECT, AnswerEvaluation.PARTIAL]


def test_answer_evaluator_partial_credit_disabled():
    """Test behavior when partial credit is disabled."""
    config = TestSessionConfig(
        strict_matching=False,
        allow_partial_credit=False,
        similarity_threshold=0.8
    )
    evaluator = AnswerEvaluator(config)

    evaluation, score = evaluator.evaluate_answer("chein", "chien")

    # Should not give partial credit even for close matches
    assert evaluation == AnswerEvaluation.INCORRECT
    assert score == 0.0

