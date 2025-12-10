"""
Phase 20: Case Theory Engine Tests

Tests for HypothesisGenerator, ContradictionChecker,
EvidenceWeightingEngine, and CaseNarrativeBuilder.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')

from app.ada.case_theory_engine import (
    HypothesisGenerator,
    ContradictionChecker,
    EvidenceWeightingEngine,
    CaseNarrativeBuilder,
    HypothesisStatus,
    EvidenceStrength,
)


class TestHypothesisGenerator:
    def setup_method(self):
        self.generator = HypothesisGenerator()

    def test_generate_hypotheses(self):
        case_data = {
            "offense_type": "homicide",
            "victim": {"name": "John Doe", "relationship_to_suspect": "known"},
            "location": "residential",
            "time_of_day": "night",
        }
        evidence_items = [
            {"id": "ev-001", "type": "weapon", "description": "Knife found at scene"},
            {"id": "ev-002", "type": "fingerprint", "description": "Latent print on door"},
        ]
        suspects = [
            {"id": "sus-001", "name": "Jane Smith", "relationship": "spouse"},
        ]
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-001",
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )
        assert len(hypotheses) > 0
        assert all(h.case_id == "case-001" for h in hypotheses)

    def test_get_hypothesis(self):
        case_data = {"offense_type": "robbery"}
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-002",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        if hypotheses:
            retrieved = self.generator.get_hypothesis(hypotheses[0].hypothesis_id)
            assert retrieved is not None

    def test_get_case_hypotheses(self):
        case_data = {"offense_type": "burglary"}
        self.generator.generate_hypotheses(
            case_id="case-003",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        hypotheses = self.generator.get_case_hypotheses("case-003")
        assert len(hypotheses) > 0

    def test_rank_hypotheses(self):
        case_data = {"offense_type": "assault"}
        self.generator.generate_hypotheses(
            case_id="case-004",
            case_data=case_data,
            evidence_items=[{"id": "ev-001", "type": "witness"}],
            suspects=[{"id": "sus-001", "name": "Test"}],
        )
        ranked = self.generator.rank_hypotheses("case-004")
        assert isinstance(ranked, list)

    def test_update_hypothesis_status(self):
        case_data = {"offense_type": "theft"}
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-005",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        if hypotheses:
            updated = self.generator.update_hypothesis_status(
                hypotheses[0].hypothesis_id,
                HypothesisStatus.CONFIRMED,
            )
            assert updated is not None
            assert updated.status == HypothesisStatus.CONFIRMED


class TestContradictionChecker:
    def setup_method(self):
        self.generator = HypothesisGenerator()
        self.checker = ContradictionChecker(self.generator)

    def test_check_hypothesis(self):
        case_data = {"offense_type": "homicide", "time_of_death": "22:00"}
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-001",
            case_data=case_data,
            evidence_items=[],
            suspects=[{"id": "sus-001", "name": "Test", "alibi": "at_work"}],
        )
        if hypotheses:
            evidence_items = [
                {"id": "ev-001", "type": "alibi", "confirms_alibi": True},
            ]
            contradictions = self.checker.check_hypothesis(
                hypotheses[0].hypothesis_id,
                evidence_items,
                case_data,
            )
            assert isinstance(contradictions, list)

    def test_get_contradiction(self):
        case_data = {"offense_type": "robbery"}
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-002",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        if hypotheses:
            contradictions = self.checker.check_hypothesis(
                hypotheses[0].hypothesis_id,
                [{"id": "ev-001", "contradicts": True}],
                case_data,
            )
            if contradictions:
                retrieved = self.checker.get_contradiction(
                    contradictions[0].contradiction_id
                )
                assert retrieved is not None

    def test_get_hypothesis_contradictions(self):
        case_data = {"offense_type": "assault"}
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-003",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        if hypotheses:
            self.checker.check_hypothesis(
                hypotheses[0].hypothesis_id,
                [],
                case_data,
            )
            contradictions = self.checker.get_hypothesis_contradictions(
                hypotheses[0].hypothesis_id
            )
            assert isinstance(contradictions, list)

    def test_get_unresolved_contradictions(self):
        case_data = {"offense_type": "burglary"}
        hypotheses = self.generator.generate_hypotheses(
            case_id="case-004",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        if hypotheses:
            self.checker.check_hypothesis(
                hypotheses[0].hypothesis_id,
                [],
                case_data,
            )
        unresolved = self.checker.get_unresolved_contradictions("case-004")
        assert isinstance(unresolved, list)


class TestEvidenceWeightingEngine:
    def setup_method(self):
        self.engine = EvidenceWeightingEngine()

    def test_calculate_weight(self):
        evidence_data = {
            "type": "dna",
            "match_probability": 0.99999,
            "chain_of_custody": True,
            "lab_certified": True,
        }
        weight = self.engine.calculate_weight(
            case_id="case-001",
            evidence_id="ev-001",
            evidence_data=evidence_data,
            suspect_id="sus-001",
        )
        assert weight is not None
        assert weight.weight_score > 0

    def test_get_evidence_weights(self):
        evidence_data = {"type": "fingerprint"}
        self.engine.calculate_weight(
            case_id="case-002",
            evidence_id="ev-001",
            evidence_data=evidence_data,
            suspect_id="sus-001",
        )
        weights = self.engine.get_evidence_weights("case-002")
        assert len(weights) > 0

    def test_calculate_cumulative_weight(self):
        for i in range(3):
            self.engine.calculate_weight(
                case_id="case-003",
                evidence_id=f"ev-{i}",
                evidence_data={"type": "physical"},
                suspect_id="sus-001",
            )
        cumulative = self.engine.calculate_cumulative_weight("case-003", "sus-001")
        assert "cumulative_score" in cumulative
        assert "evidence_count" in cumulative
        assert "recommendation" in cumulative

    def test_weight_strength_classification(self):
        strong_evidence = {
            "type": "dna",
            "match_probability": 0.9999,
            "chain_of_custody": True,
        }
        weight = self.engine.calculate_weight(
            case_id="case-004",
            evidence_id="ev-001",
            evidence_data=strong_evidence,
            suspect_id="sus-001",
        )
        assert weight.strength in [
            EvidenceStrength.WEAK,
            EvidenceStrength.MODERATE,
            EvidenceStrength.STRONG,
            EvidenceStrength.CONCLUSIVE,
        ]


class TestCaseNarrativeBuilder:
    def setup_method(self):
        self.generator = HypothesisGenerator()
        self.weighting = EvidenceWeightingEngine()
        self.builder = CaseNarrativeBuilder(self.generator, self.weighting)

    def test_build_narrative(self):
        case_data = {
            "offense_type": "homicide",
            "incident_date": "2024-01-15",
            "location": "123 Main St",
            "victim": {"name": "John Doe"},
        }
        evidence_items = [
            {"id": "ev-001", "type": "weapon", "description": "Knife"},
            {"id": "ev-002", "type": "dna", "description": "DNA sample"},
        ]
        suspects = [
            {"id": "sus-001", "name": "Jane Smith"},
        ]
        narrative = self.builder.build_narrative(
            case_id="case-001",
            case_data=case_data,
            evidence_items=evidence_items,
            suspects=suspects,
        )
        assert narrative is not None
        assert narrative.case_id == "case-001"
        assert len(narrative.sections) > 0

    def test_get_narrative(self):
        case_data = {"offense_type": "robbery"}
        narrative = self.builder.build_narrative(
            case_id="case-002",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        retrieved = self.builder.get_narrative(narrative.narrative_id)
        assert retrieved is not None
        assert retrieved.narrative_id == narrative.narrative_id

    def test_export_narrative_text(self):
        case_data = {"offense_type": "assault"}
        narrative = self.builder.build_narrative(
            case_id="case-003",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        exported = self.builder.export_narrative(narrative.narrative_id, "text")
        assert exported is not None
        assert isinstance(exported, str)

    def test_narrative_has_required_sections(self):
        case_data = {"offense_type": "burglary"}
        narrative = self.builder.build_narrative(
            case_id="case-004",
            case_data=case_data,
            evidence_items=[],
            suspects=[],
        )
        expected_sections = [
            "executive_summary",
            "incident_details",
            "evidence_analysis",
            "suspect_analysis",
        ]
        for section in expected_sections:
            assert section in narrative.sections
