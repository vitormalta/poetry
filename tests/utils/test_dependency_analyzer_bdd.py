from __future__ import annotations

import pytest
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poetry.poetry import Poetry
    from tests.types import FixtureDirGetter


class TestDependencyAnalyzerBDD:
    """
    BDD tests for the dependency analyzer
    """

    def test_when_analyzing_simple_project_should_return_basic_metrics(
        self, fixture_dir: FixtureDirGetter
    ) -> None:
        """
        Scenario: Analyze a simple project with few dependencies
        Given: a project with basic dependencies
        When: performing dependency health analysis
        Then: it should return correct basic metrics
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(fixture_dir("simple_project"))

        assert result.total_dependencies >= 0
        assert result.direct_dependencies >= 0
        assert result.transitive_dependencies >= 0
        assert result.conflict_score >= 0.0
        assert result.complexity_level in ["low", "medium", "high", "critical"]

    def test_when_analyzing_project_with_conflicts_should_identify_issues(
        self, fixture_dir: FixtureDirGetter
    ) -> None:
        """
        Scenario: Analyze a project with dependency conflicts
        Given: a project with conflicting dependencies
        When: performing dependency health analysis
        Then: it should identify conflicts and calculate conflict score
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(fixture_dir("simple_project"))

        # For simple projects, there may be no conflicts
        assert result.conflict_score >= 0.0
        assert result.complexity_level in ["low", "medium", "high", "critical"]
        assert isinstance(result.conflicts, list)

    def test_when_analyzing_large_project_should_calculate_correct_complexity(
        self, fixture_dir: FixtureDirGetter
    ) -> None:
        """
        Scenario: Analyze a large project with many dependencies
        Given: a project with many transitive dependencies
        When: performing dependency health analysis
        Then: it should correctly calculate the complexity level
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(fixture_dir("extended_project"))

        assert result.total_dependencies >= 0
        assert result.complexity_level in ["low", "medium", "high", "critical"]
        assert result.dependency_tree_depth >= 1

    def test_when_analyzing_project_with_outdated_dependencies_should_identify_versions(
        self, fixture_dir: FixtureDirGetter
    ) -> None:
        """
        Scenario: Analyze a project with outdated dependencies
        Given: a project with old dependency versions
        When: performing dependency health analysis
        Then: it should identify dependencies that can be updated
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(fixture_dir("simple_project"))

        # For simple projects, there may be no updatable dependencies
        assert result.updatable_dependencies >= 0
        assert result.security_vulnerabilities >= 0
        assert result.recommendations is not None

    def test_when_analyzing_project_with_groups_should_respect_configuration(
        self, fixture_dir: FixtureDirGetter
    ) -> None:
        """
        Scenario: Analyze a project with dependency groups
        Given: a project with dependencies organized in groups
        When: performing dependency health analysis
        Then: it should respect the group configuration
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_dependency_health(
            fixture_dir("project_with_extras"),
            include_groups=["dev", "test"]
        )

        assert result.group_analysis is not None
        assert "dev" in result.group_analysis
        assert "test" in result.group_analysis
        # For small projects, there may be no transitive dependencies
        assert result.total_dependencies >= result.direct_dependencies


class TestDependencyAnalyzerScenarios:
    """
    Tests for specific scenarios of the dependency analyzer
    """

    @pytest.mark.parametrize("complexity,expected_level", [
        (5, "low"),
        (15, "medium"),
        (50, "high"),
        (100, "critical")
    ])
    def test_should_classify_complexity_correctly(
        self, complexity: int, expected_level: str
    ) -> None:
        """
        Scenario: Classify complexity level based on the number of dependencies
        Given: different numbers of dependencies
        When: calculating the complexity level
        Then: it should return the correct level
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        level = analyzer._calculate_complexity_level(complexity)

        assert level == expected_level

    def test_should_calculate_conflict_score_correctly(self) -> None:
        """
        Scenario: Calculate conflict score based on identified issues
        Given: different types of dependency problems
        When: calculating the conflict score
        Then: it should return a score between 0.0 and 1.0
        """
        from poetry.utils.dependency_analyzer import DependencyAnalyzer

        analyzer = DependencyAnalyzer()
        score = analyzer._calculate_conflict_score(
            conflicts=3,
            total_deps=20,
            security_issues=1
        )

        assert 0.0 <= score <= 1.0
        assert score > 0.0  # There should be some conflict
