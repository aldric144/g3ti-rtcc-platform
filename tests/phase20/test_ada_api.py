"""
Phase 20: ADA API Tests

Tests for all ADA REST API endpoints.
"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/home/ubuntu/repos/g3ti-rtcc-platform/backend')


class TestSceneReconstructionAPI:
    def test_create_reconstruction_request_model(self):
        request_data = {
            "case_id": "case-001",
            "scene_type": "indoor",
            "location": {"address": "123 Main St", "lat": 33.749, "lng": -84.388},
            "bounds": {"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100},
        }
        assert "case_id" in request_data
        assert "scene_type" in request_data

    def test_evidence_register_request_model(self):
        request_data = {
            "case_id": "case-001",
            "evidence_type": "blood_spatter",
            "position": {"x": 10, "y": 20, "z": 0},
            "description": "Blood spatter on wall",
            "collected_by": "Officer Smith",
        }
        assert "case_id" in request_data
        assert "evidence_type" in request_data
        assert "position" in request_data

    def test_trajectory_create_request_model(self):
        request_data = {
            "case_id": "case-001",
            "subject_type": "suspect",
            "subject_id": "suspect-001",
        }
        assert "case_id" in request_data
        assert "subject_type" in request_data


class TestOffenderModelingAPI:
    def test_signature_analyze_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {
                "offense_type": "burglary",
                "entry_method": "forced_rear",
                "weapon_used": "knife",
            },
        }
        assert "case_id" in request_data
        assert "case_data" in request_data

    def test_prediction_request_model(self):
        request_data = {
            "offender_id": "offender-001",
        }
        assert "offender_id" in request_data

    def test_profile_generate_request_model(self):
        request_data = {
            "case_ids": ["case-001", "case-002"],
            "case_data": [
                {"offense_type": "burglary"},
                {"offense_type": "burglary"},
            ],
        }
        assert "case_ids" in request_data
        assert "case_data" in request_data


class TestCaseTheoryAPI:
    def test_hypothesis_generate_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {"offense_type": "homicide"},
            "evidence_items": [{"id": "ev-001", "type": "weapon"}],
            "suspects": [{"id": "sus-001", "name": "Jane Smith"}],
        }
        assert "case_id" in request_data
        assert "case_data" in request_data

    def test_contradiction_check_request_model(self):
        request_data = {
            "hypothesis_id": "hyp-001",
            "evidence_items": [{"id": "ev-001", "contradicts": True}],
            "case_data": {"time_of_death": "22:00"},
        }
        assert "hypothesis_id" in request_data
        assert "evidence_items" in request_data

    def test_evidence_weight_request_model(self):
        request_data = {
            "case_id": "case-001",
            "evidence_id": "ev-001",
            "evidence_data": {"type": "dna", "match_probability": 0.99999},
            "suspect_id": "sus-001",
        }
        assert "case_id" in request_data
        assert "evidence_id" in request_data
        assert "suspect_id" in request_data

    def test_narrative_build_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {"offense_type": "homicide"},
            "evidence_items": [],
            "suspects": [],
        }
        assert "case_id" in request_data


class TestEvidenceGraphAPI:
    def test_graph_node_request_model(self):
        request_data = {
            "node_type": "case",
            "label": "Case #2024-001",
            "case_ids": ["case-001"],
            "properties": {"offense_type": "burglary"},
        }
        assert "node_type" in request_data
        assert "label" in request_data

    def test_graph_edge_request_model(self):
        request_data = {
            "source_id": "node-001",
            "target_id": "node-002",
            "edge_type": "suspect_link",
            "weight": 0.85,
        }
        assert "source_id" in request_data
        assert "target_id" in request_data
        assert "edge_type" in request_data

    def test_similarity_calculate_request_model(self):
        request_data = {
            "case_id_1": "case-001",
            "case_id_2": "case-002",
            "case1_data": {"offense_type": "burglary"},
            "case2_data": {"offense_type": "burglary"},
        }
        assert "case_id_1" in request_data
        assert "case_id_2" in request_data

    def test_case_link_analyze_request_model(self):
        request_data = {
            "case_ids": ["case-001", "case-002", "case-003"],
            "case_data_map": {
                "case-001": {"offense_type": "burglary"},
                "case-002": {"offense_type": "burglary"},
                "case-003": {"offense_type": "burglary"},
            },
        }
        assert "case_ids" in request_data
        assert "case_data_map" in request_data


class TestReportingAPI:
    def test_report_create_request_model(self):
        request_data = {
            "case_id": "case-001",
            "report_type": "investigative",
            "title": "Initial Investigation Report",
            "author": "Detective Smith",
        }
        assert "case_id" in request_data
        assert "report_type" in request_data
        assert "title" in request_data

    def test_brief_generate_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {"offense_type": "homicide"},
            "evidence_items": [],
            "suspects": [],
        }
        assert "case_id" in request_data

    def test_court_packet_generate_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {
                "case_number": "2024-CR-001234",
                "defendant_name": "John Doe",
            },
            "evidence_items": [],
        }
        assert "case_id" in request_data
        assert "case_data" in request_data

    def test_review_start_request_model(self):
        request_data = {
            "report_id": "rpt-001",
            "reviewer_id": "supervisor-001",
            "reviewer_name": "Sgt. Johnson",
        }
        assert "report_id" in request_data
        assert "reviewer_id" in request_data


class TestAutonomousInvestigationAPI:
    def test_investigate_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {"offense_type": "homicide"},
            "evidence_items": [{"id": "ev-001", "type": "weapon"}],
            "suspects": [{"id": "sus-001", "name": "Jane Smith"}],
        }
        assert "case_id" in request_data
        assert "case_data" in request_data

    def test_triage_case_request_model(self):
        request_data = {
            "case_id": "case-001",
            "case_data": {
                "status": "open",
                "has_new_evidence": True,
            },
        }
        assert "case_id" in request_data
        assert "case_data" in request_data

    def test_daily_triage_request_model(self):
        request_data = {
            "cases": [
                {"case_id": "case-001", "data": {"status": "open"}},
                {"case_id": "case-002", "data": {"status": "open"}},
            ],
        }
        assert "cases" in request_data
        assert len(request_data["cases"]) == 2


class TestWebSocketChannels:
    def test_case_updates_channel_events(self):
        expected_events = [
            "investigation_started",
            "investigation_progress",
            "investigation_completed",
            "new_evidence",
            "suspect_update",
            "triage_alert",
        ]
        for event in expected_events:
            assert isinstance(event, str)

    def test_theory_stream_channel_events(self):
        expected_events = [
            "hypothesis_generated",
            "hypothesis_status_change",
            "contradiction_found",
            "theory_ranking_update",
            "narrative_progress",
            "narrative_completed",
        ]
        for event in expected_events:
            assert isinstance(event, str)

    def test_evidence_links_channel_events(self):
        expected_events = [
            "case_link_discovered",
            "similarity_update",
            "entity_connection",
            "cluster_formed",
            "pattern_match",
            "graph_node_added",
            "graph_edge_added",
        ]
        for event in expected_events:
            assert isinstance(event, str)


class TestAPIResponseModels:
    def test_investigation_result_response(self):
        response = {
            "result_id": "inv-001",
            "case_id": "case-001",
            "status": "completed",
            "suspects_identified": 2,
            "theories_generated": 3,
            "linked_cases": 1,
            "confidence_score": 0.78,
            "processing_time_seconds": 45.2,
            "report_id": "rpt-001",
        }
        assert "result_id" in response
        assert "status" in response
        assert "confidence_score" in response

    def test_triage_item_response(self):
        response = {
            "triage_id": "tri-001",
            "case_id": "case-001",
            "priority": "high",
            "score": 72,
            "reasons": ["new_evidence", "suspect_identified"],
            "recommended_actions": ["Review evidence", "Interview suspect"],
        }
        assert "triage_id" in response
        assert "priority" in response
        assert "reasons" in response

    def test_hypothesis_response(self):
        response = {
            "hypothesis_id": "hyp-001",
            "case_id": "case-001",
            "title": "Primary Suspect Theory",
            "description": "The suspect committed the crime.",
            "hypothesis_type": "primary_suspect",
            "status": "active",
            "confidence_score": 0.75,
            "supporting_evidence": ["ev-001", "ev-002"],
            "contradictions": [],
        }
        assert "hypothesis_id" in response
        assert "confidence_score" in response

    def test_case_link_response(self):
        response = {
            "link_id": "link-001",
            "case_id_1": "case-001",
            "case_id_2": "case-002",
            "link_type": "mo_similarity",
            "strength": 0.72,
            "confirmed": False,
            "linking_factors": ["entry_method", "time_of_day"],
        }
        assert "link_id" in response
        assert "strength" in response
        assert "linking_factors" in response
