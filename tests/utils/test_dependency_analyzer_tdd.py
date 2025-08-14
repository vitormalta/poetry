from __future__ import annotations

import pytest
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poetry.poetry import Poetry
    from tests.types import FixtureDirGetter


class TestDependencyAnalyzerTDD:
    """
    TDD tests for the dependency analyzer
    """

    def test_should_create_dependency_analyzer_instance(self) -> None:
        """Test: Should create an instance of the dependency analyzer"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_dependency_health')

    def test_should_return_analysis_result_with_required_attributes(self) -> None:
        """Test: Should return a result with required attributes"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer, DependencyHealthResult

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert isinstance(result, DependencyHealthResult)
        assert hasattr(result, 'total_dependencies')
        assert hasattr(result, 'direct_dependencies')
        assert hasattr(result, 'transitive_dependencies')
        assert hasattr(result, 'conflict_score')
        assert hasattr(result, 'complexity_level')

    def test_should_calculate_total_dependencies_correctly(self) -> None:
        """Test: Should calculate total dependencies correctly"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        expected_total = result.direct_dependencies + result.transitive_dependencies
        assert result.total_dependencies == expected_total

    def test_should_return_conflict_score_between_zero_and_one(self) -> None:
        """Test: Should return conflict score between 0.0 and 1.0"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert 0.0 <= result.conflict_score <= 1.0

    def test_should_return_valid_complexity_level(self) -> None:
        """Test: Should return a valid complexity level"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        valid_levels = ["low", "medium", "high", "critical"]
        assert result.complexity_level in valid_levels

    def test_should_handle_empty_project_directory(self) -> None:
        """Test: Should handle an empty project directory"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert result.total_dependencies >= 0
        assert result.direct_dependencies >= 0
        assert result.transitive_dependencies >= 0

    def test_should_include_group_analysis_when_groups_specified(self) -> None:
        """Test: Should include group analysis when specified"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        test_project_path = Path("tests/fixtures/simple_project")

        if test_project_path.exists():
            result = analyzer.analyze_dependency_health(
                test_project_path,
                include_groups=["dev", "test"]
            )
            assert hasattr(result, 'group_analysis')
            assert result.group_analysis is not None
        else:
            result = analyzer.analyze_dependency_health(
                Path("."),
                include_groups=["dev", "test"]
            )
            assert hasattr(result, 'group_analysis')

    def test_should_calculate_dependency_tree_depth(self) -> None:
        """Test: Should calculate dependency tree depth"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert hasattr(result, 'dependency_tree_depth')
        assert result.dependency_tree_depth >= 0

    def test_should_identify_updatable_dependencies(self) -> None:
        """Test: Should identify updatable dependencies"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert hasattr(result, 'updatable_dependencies')
        assert result.updatable_dependencies >= 0

    def test_should_detect_security_vulnerabilities(self) -> None:
        """Test: Should detect security vulnerabilities"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert hasattr(result, 'security_vulnerabilities')
        assert result.security_vulnerabilities >= 0

    def test_should_provide_recommendations(self) -> None:
        """Test: Should provide improvement recommendations"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(Path("."))

        assert hasattr(result, 'recommendations')
        assert isinstance(result.recommendations, list)

    def test_should_handle_invalid_project_path(self) -> None:
        """Test: Should handle invalid project path"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()

        with pytest.raises(ValueError):
            analyzer.analyze_dependency_health(Path("/invalid/path"))

    def test_should_calculate_conflict_score_with_no_conflicts(self) -> None:
        """Test: Should calculate conflict score with no conflicts"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        score = analyzer._calculate_conflict_score(0, 10, 0)

        assert score == 0.0

    def test_should_calculate_conflict_score_with_conflicts(self) -> None:
        """Test: Should calculate conflict score with conflicts"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        score = analyzer._calculate_conflict_score(5, 20, 2)

        assert score > 0.0
        assert score <= 1.0

    def test_should_classify_complexity_levels_correctly(self) -> None:
        """Test: Should classify complexity levels correctly"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()

        assert analyzer._calculate_complexity_level(5) == "low"
        assert analyzer._calculate_complexity_level(15) == "medium"
        assert analyzer._calculate_complexity_level(50) == "high"
        assert analyzer._calculate_complexity_level(100) == "critical"

    def test_should_handle_edge_case_complexity_values(self) -> None:
        """Test: Should handle edge case complexity values"""
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()

        assert analyzer._calculate_complexity_level(0) == "low"
        assert analyzer._calculate_complexity_level(1000) == "critical"
        assert analyzer._calculate_complexity_level(-5) == "low"  # Should handle negative values
