"""
Test Suite 1: Legislative Knowledge Base Engine Tests

Tests for document ingestion, versioning, search, and retrieval.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, "/home/ubuntu/repos/g3ti-rtcc-platform/backend")

from app.city_governance.legislative_kb import (
    get_legislative_kb,
    LegislativeKnowledgeBase,
    LegalDocument,
    LegalSource,
    LegalCategory,
    DocumentVersion,
)


class TestLegalDocument:
    """Tests for LegalDocument model."""

    def test_legal_document_creation(self):
        """Test creating a legal document."""
        doc = LegalDocument(
            document_id="doc-001",
            title="Test Document",
            source=LegalSource.FLORIDA_STATUTE,
            category=LegalCategory.SURVEILLANCE,
            content="Test content for surveillance regulations.",
            effective_date=datetime.now(),
            version="1.0",
            jurisdiction="Florida",
            citations=["F.S. 934.50"],
        )
        assert doc.document_id == "doc-001"
        assert doc.source == LegalSource.FLORIDA_STATUTE
        assert doc.category == LegalCategory.SURVEILLANCE
        assert "surveillance" in doc.content.lower()

    def test_legal_document_with_all_sources(self):
        """Test creating documents with all legal sources."""
        sources = [
            LegalSource.US_CONSTITUTION,
            LegalSource.FLORIDA_CONSTITUTION,
            LegalSource.FLORIDA_STATUTE,
            LegalSource.RIVIERA_BEACH_CODE,
            LegalSource.FEDERAL_FRAMEWORK,
            LegalSource.AGENCY_SOP,
            LegalSource.EMERGENCY_ORDINANCE,
        ]
        for source in sources:
            doc = LegalDocument(
                document_id=f"doc-{source.value}",
                title=f"Test {source.value}",
                source=source,
                category=LegalCategory.PUBLIC_SAFETY,
                content="Test content",
                effective_date=datetime.now(),
                version="1.0",
                jurisdiction="Test",
                citations=[],
            )
            assert doc.source == source

    def test_legal_document_with_all_categories(self):
        """Test creating documents with all legal categories."""
        categories = [
            LegalCategory.CIVIL_RIGHTS,
            LegalCategory.PUBLIC_SAFETY,
            LegalCategory.EMERGENCY_POWERS,
            LegalCategory.CITY_AUTHORITY,
            LegalCategory.AUTONOMY_LIMITS,
            LegalCategory.PRIVACY,
            LegalCategory.SURVEILLANCE,
            LegalCategory.USE_OF_FORCE,
            LegalCategory.TRAFFIC,
            LegalCategory.FIRE_EMS,
            LegalCategory.PROPERTY_RIGHTS,
            LegalCategory.DATA_PROTECTION,
        ]
        for category in categories:
            doc = LegalDocument(
                document_id=f"doc-{category.value}",
                title=f"Test {category.value}",
                source=LegalSource.FLORIDA_STATUTE,
                category=category,
                content="Test content",
                effective_date=datetime.now(),
                version="1.0",
                jurisdiction="Test",
                citations=[],
            )
            assert doc.category == category


class TestDocumentVersion:
    """Tests for DocumentVersion model."""

    def test_document_version_creation(self):
        """Test creating a document version."""
        version = DocumentVersion(
            version_id="ver-001",
            document_id="doc-001",
            version_number="1.0",
            content="Original content",
            effective_date=datetime.now(),
            supersedes=None,
            change_summary="Initial version",
        )
        assert version.version_id == "ver-001"
        assert version.version_number == "1.0"
        assert version.supersedes is None

    def test_document_version_chain(self):
        """Test creating a version chain."""
        v1 = DocumentVersion(
            version_id="ver-001",
            document_id="doc-001",
            version_number="1.0",
            content="Original content",
            effective_date=datetime.now() - timedelta(days=365),
            supersedes=None,
            change_summary="Initial version",
        )
        v2 = DocumentVersion(
            version_id="ver-002",
            document_id="doc-001",
            version_number="2.0",
            content="Updated content",
            effective_date=datetime.now(),
            supersedes="ver-001",
            change_summary="Updated regulations",
        )
        assert v2.supersedes == v1.version_id


class TestLegislativeKnowledgeBase:
    """Tests for LegislativeKnowledgeBase singleton."""

    def test_singleton_pattern(self):
        """Test that get_legislative_kb returns singleton."""
        kb1 = get_legislative_kb()
        kb2 = get_legislative_kb()
        assert kb1 is kb2

    def test_get_all_documents(self):
        """Test retrieving all documents."""
        kb = get_legislative_kb()
        docs = kb.get_all_documents()
        assert isinstance(docs, list)
        assert len(docs) >= 20  # Should have at least 20 pre-loaded documents

    def test_get_document_by_id(self):
        """Test retrieving document by ID."""
        kb = get_legislative_kb()
        docs = kb.get_all_documents()
        if docs:
            doc = kb.get_document_by_id(docs[0].document_id)
            assert doc is not None
            assert doc.document_id == docs[0].document_id

    def test_get_document_by_invalid_id(self):
        """Test retrieving document with invalid ID."""
        kb = get_legislative_kb()
        doc = kb.get_document_by_id("invalid-id-12345")
        assert doc is None

    def test_get_documents_by_source(self):
        """Test filtering documents by source."""
        kb = get_legislative_kb()
        for source in LegalSource:
            docs = kb.get_documents_by_source(source)
            assert isinstance(docs, list)
            for doc in docs:
                assert doc.source == source

    def test_get_documents_by_category(self):
        """Test filtering documents by category."""
        kb = get_legislative_kb()
        for category in LegalCategory:
            docs = kb.get_documents_by_category(category)
            assert isinstance(docs, list)
            for doc in docs:
                assert doc.category == category

    def test_search_documents(self):
        """Test searching documents by keyword."""
        kb = get_legislative_kb()
        # Search for common legal terms
        results = kb.search_documents("warrant")
        assert isinstance(results, list)
        # Results should contain documents mentioning warrant
        for doc in results:
            assert "warrant" in doc.content.lower() or "warrant" in doc.title.lower()

    def test_search_documents_empty_query(self):
        """Test searching with empty query."""
        kb = get_legislative_kb()
        results = kb.search_documents("")
        assert isinstance(results, list)

    def test_ingest_document(self):
        """Test ingesting a new document."""
        kb = get_legislative_kb()
        initial_count = len(kb.get_all_documents())
        
        new_doc = LegalDocument(
            document_id=f"test-doc-{datetime.now().timestamp()}",
            title="Test Ingested Document",
            source=LegalSource.AGENCY_SOP,
            category=LegalCategory.PUBLIC_SAFETY,
            content="Test content for ingestion.",
            effective_date=datetime.now(),
            version="1.0",
            jurisdiction="Riviera Beach",
            citations=[],
        )
        
        result = kb.ingest_document(new_doc)
        assert result is True
        
        # Verify document was added
        retrieved = kb.get_document_by_id(new_doc.document_id)
        assert retrieved is not None
        assert retrieved.title == new_doc.title

    def test_get_document_versions(self):
        """Test retrieving document versions."""
        kb = get_legislative_kb()
        docs = kb.get_all_documents()
        if docs:
            versions = kb.get_document_versions(docs[0].document_id)
            assert isinstance(versions, list)

    def test_get_effective_document(self):
        """Test retrieving effective document at a date."""
        kb = get_legislative_kb()
        docs = kb.get_all_documents()
        if docs:
            effective = kb.get_effective_document(docs[0].document_id, datetime.now())
            assert effective is not None


class TestLegalSourceHierarchy:
    """Tests for legal source hierarchy and precedence."""

    def test_federal_sources_highest_priority(self):
        """Test that federal sources have highest priority."""
        kb = get_legislative_kb()
        federal_docs = kb.get_documents_by_source(LegalSource.US_CONSTITUTION)
        assert len(federal_docs) > 0
        # Federal constitutional documents should exist

    def test_state_sources_second_priority(self):
        """Test that state sources have second priority."""
        kb = get_legislative_kb()
        state_docs = kb.get_documents_by_source(LegalSource.FLORIDA_CONSTITUTION)
        assert len(state_docs) > 0

    def test_local_sources_lower_priority(self):
        """Test that local sources have lower priority."""
        kb = get_legislative_kb()
        local_docs = kb.get_documents_by_source(LegalSource.RIVIERA_BEACH_CODE)
        assert len(local_docs) > 0


class TestDocumentCitations:
    """Tests for document citation handling."""

    def test_document_with_citations(self):
        """Test document with multiple citations."""
        doc = LegalDocument(
            document_id="doc-citations",
            title="Document with Citations",
            source=LegalSource.FLORIDA_STATUTE,
            category=LegalCategory.SURVEILLANCE,
            content="Test content",
            effective_date=datetime.now(),
            version="1.0",
            jurisdiction="Florida",
            citations=["F.S. 934.50", "F.S. 943.0585", "4th Amendment"],
        )
        assert len(doc.citations) == 3
        assert "F.S. 934.50" in doc.citations

    def test_document_without_citations(self):
        """Test document without citations."""
        doc = LegalDocument(
            document_id="doc-no-citations",
            title="Document without Citations",
            source=LegalSource.AGENCY_SOP,
            category=LegalCategory.PUBLIC_SAFETY,
            content="Test content",
            effective_date=datetime.now(),
            version="1.0",
            jurisdiction="Riviera Beach",
            citations=[],
        )
        assert len(doc.citations) == 0


class TestRivieraBeachSpecific:
    """Tests for Riviera Beach-specific documents."""

    def test_riviera_beach_documents_exist(self):
        """Test that Riviera Beach-specific documents exist."""
        kb = get_legislative_kb()
        rb_docs = kb.get_documents_by_source(LegalSource.RIVIERA_BEACH_CODE)
        assert len(rb_docs) > 0

    def test_riviera_beach_jurisdiction(self):
        """Test Riviera Beach jurisdiction in documents."""
        kb = get_legislative_kb()
        rb_docs = kb.get_documents_by_source(LegalSource.RIVIERA_BEACH_CODE)
        for doc in rb_docs:
            assert "Riviera Beach" in doc.jurisdiction or "Palm Beach" in doc.jurisdiction
