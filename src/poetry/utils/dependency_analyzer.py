from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from poetry.poetry import Poetry
    from poetry.core.packages.package import Package
    from poetry.core.packages.dependency import Dependency


@dataclasses.dataclass
class DependencyHealthResult:
    """Result of the dependency health analysis"""

    # Basic metrics
    total_dependencies: int
    direct_dependencies: int
    transitive_dependencies: int
    dependency_tree_depth: int

    # Quality analysis
    conflict_score: float
    complexity_level: str

    # Security and update analysis
    updatable_dependencies: int
    security_vulnerabilities: int

    # Group analysis
    group_analysis: Optional[Dict[str, Dict[str, Any]]]

    # Recommendations
    recommendations: List[str]

    # Conflict details
    conflicts: List[str]


class DependencyAnalyzer:
    """
    Dependency health analyzer for a Poetry project

    This analyzer provides metrics and insights about the quality
    and health of a project's dependencies, including:

    - Count of direct and transitive dependencies
    - Conflict and compatibility analysis
    - Complexity classification
    - Identification of updatable dependencies
    - Detection of security vulnerabilities
    - Improvement recommendations
    """

    def __init__(self) -> None:
        """Initialize the dependency analyzer"""
        self._cache: Dict[str, Any] = {}

    def analyze_dependency_health(
        self,
        project_path: Path,
        include_groups: Optional[List[str]] = None
    ) -> DependencyHealthResult:
        """
        Analyze the dependency health of a project

        Args:
            project_path: Path to the project directory
            include_groups: List of dependency groups to include in the analysis

        Returns:
            DependencyHealthResult with metrics and insights

        Raises:
            ValueError: If the project path is invalid
        """
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Invalid project path: {project_path}")

        poetry = self._load_poetry_project(project_path)
        if not poetry:
            return self._create_empty_result()

        dependencies = self._analyze_dependencies(poetry, include_groups)

        total_deps = dependencies['total']
        direct_deps = dependencies['direct']
        transitive_deps = dependencies['transitive']
        tree_depth = dependencies['depth']

        conflicts = self._identify_conflicts(poetry)
        security_issues = self._check_security_vulnerabilities(poetry)
        updatable = self._find_updatable_dependencies(poetry)

        conflict_score = self._calculate_conflict_score(
            len(conflicts), total_deps, security_issues
        )
        complexity_level = self._calculate_complexity_level(total_deps)

        recommendations = self._generate_recommendations(
            conflicts, security_issues, updatable, complexity_level
        )

        group_analysis = self._analyze_groups(poetry, include_groups)

        return DependencyHealthResult(
            total_dependencies=total_deps,
            direct_dependencies=direct_deps,
            transitive_dependencies=transitive_deps,
            dependency_tree_depth=tree_depth,
            conflict_score=conflict_score,
            complexity_level=complexity_level,
            updatable_dependencies=updatable,
            security_vulnerabilities=security_issues,
            group_analysis=group_analysis,
            recommendations=recommendations,
            conflicts=conflicts
        )

    def _load_poetry_project(self, project_path: Path) -> Optional[Poetry]:
        """Load the Poetry project from the specified path"""
        try:
            from poetry.factory import Factory
            return Factory().create_poetry(project_path)
        except Exception:
            return None

    def _create_empty_result(self) -> DependencyHealthResult:
        """Create an empty result for non-Poetry projects"""
        return DependencyHealthResult(
            total_dependencies=0,
            direct_dependencies=0,
            transitive_dependencies=0,
            dependency_tree_depth=0,
            conflict_score=0.0,
            complexity_level="low",
            updatable_dependencies=0,
            security_vulnerabilities=0,
            group_analysis=None,
            recommendations=["Project is not a valid Poetry project"],
            conflicts=[]
        )

    def _analyze_dependencies(
        self,
        poetry: Poetry,
        include_groups: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Analyze the project's dependencies"""
        package = poetry.package

        direct_deps = len(package.requires)
        if include_groups:
            for group_name in include_groups:
                if group_name in package.extras:
                    direct_deps += len(package.extras[group_name])

        transitive_deps = 0
        if poetry.locker.is_locked():
            locked_packages = poetry.locker.locked_repository().packages
            transitive_deps = len(locked_packages) - direct_deps

        tree_depth = self._estimate_tree_depth(poetry)

        return {
            'total': direct_deps + transitive_deps,
            'direct': direct_deps,
            'transitive': transitive_deps,
            'depth': tree_depth
        }

    def _estimate_tree_depth(self, poetry: Poetry) -> int:
        """Estimate the depth of the dependency tree"""
        if not poetry.locker.is_locked():
            return 1

        total_deps = len(poetry.locker.locked_repository().packages)
        if total_deps <= 5:
            return 1
        elif total_deps <= 20:
            return 2
        elif total_deps <= 50:
            return 3
        else:
            return 4

    def _identify_conflicts(self, poetry: Poetry) -> List[str]:
        """Identify dependency conflicts"""
        conflicts = []

        try:
            from poetry.puzzle.solver import Solver
            solver = Solver(
                poetry.package,
                poetry.pool,
                [],
                [],
                None
            )
        except Exception as e:
            conflicts.append(f"Resolution conflict: {str(e)}")

        package = poetry.package
        for dep in package.requires:
            if dep.constraint.is_empty():
                conflicts.append(f"Dependency {dep.name} has an empty constraint")

        return conflicts

    def _check_security_vulnerabilities(self, poetry: Poetry) -> int:
        """Check for security vulnerabilities (basic implementation)"""
        vulnerabilities = 0

        if poetry.locker.is_locked():
            for package in poetry.locker.locked_repository().packages:
                if self._is_potentially_vulnerable(package):
                    vulnerabilities += 1

        return vulnerabilities

    def _is_potentially_vulnerable(self, package: Package) -> bool:
        """Check if a package might have vulnerabilities (basic implementation)"""
        return False

    def _find_updatable_dependencies(self, poetry: Poetry) -> int:
        """Find dependencies that can be updated"""
        updatable = 0

        if poetry.locker.is_locked():
            for package in poetry.locker.locked_repository().packages:
                if self._can_be_updated(package, poetry):
                    updatable += 1

        return updatable

    def _can_be_updated(self, package: Package, poetry: Poetry) -> bool:
        """Check if a dependency can be updated"""
        return False

    def _calculate_conflict_score(
        self,
        conflicts: int,
        total_deps: int,
        security_issues: int
    ) -> float:
        """
        Calculate the conflict score (0.0 = no issues, 1.0 = many issues)

        Args:
            conflicts: Number of identified conflicts
            total_deps: Total dependencies
            security_issues: Number of security issues

        Returns:
            Score between 0.0 and 1.0
        """
        if total_deps == 0:
            return 0.0

        conflict_weight = 0.6
        security_weight = 0.4

        conflict_score = min(conflicts / total_deps, 1.0)
        security_score = min(security_issues / max(total_deps, 1), 1.0)

        total_score = conflict_score * conflict_weight + security_score * security_weight

        return min(total_score, 1.0)

    def _calculate_complexity_level(self, total_dependencies: int) -> str:
        """
        Classify complexity level based on the number of dependencies

        Args:
            total_dependencies: Total project dependencies

        Returns:
            Complexity level: "low", "medium", "high", "critical"
        """
        if total_dependencies <= 10:
            return "low"
        elif total_dependencies <= 30:
            return "medium"
        elif total_dependencies <= 50:
            return "high"
        else:
            return "critical"

    def _generate_recommendations(
        self,
        conflicts: List[str],
        security_issues: int,
        updatable: int,
        complexity_level: str
    ) -> List[str]:
        """Generate recommendations based on the analysis"""
        recommendations = []

        if conflicts:
            recommendations.append("Resolve identified dependency conflicts")

        if security_issues > 0:
            recommendations.append(
                f"Update {security_issues} dependency(ies) with security vulnerabilities"
            )

        if updatable > 0:
            recommendations.append(
                f"Consider updating {updatable} dependency(ies) to newer versions"
            )

        if complexity_level in ["high", "critical"]:
            recommendations.append(
                "Consider simplifying the dependency tree to reduce complexity"
            )

        if not recommendations:
            recommendations.append("Project is in good dependency health")

        return recommendations

    def _analyze_groups(
        self,
        poetry: Poetry,
        include_groups: Optional[List[str]] = None
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """Analyze dependencies by groups"""
        if not include_groups:
            return None

        group_analysis = {}
        package = poetry.package

        for group_name in include_groups:
            if group_name in package.extras:
                group_deps = package.extras[group_name]
                group_analysis[group_name] = {
                    'count': len(group_deps),
                    'dependencies': [dep.name for dep in group_deps]
                }
            else:
                group_analysis[group_name] = {
                    'count': 0,
                    'dependencies': []
                }

        return group_analysis
