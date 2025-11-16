#!/usr/bin/env python3
"""
Expert Knowledge RAG System for ASP AI Agent
Indexes and retrieves expert corrections, exemplar responses, and teaching patterns
Complements the literature RAG with pedagogical expertise
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


@dataclass
class ExpertCorrection:
    """Represents an expert correction of AI feedback"""
    correction_id: str
    module_id: str
    scenario_id: str
    difficulty_level: str
    competency_area: str
    user_response: str
    ai_feedback_original: str
    expert_correction: str
    expert_reasoning: str
    expert_name: str = "Unknown"
    what_ai_missed: List[str] = None
    what_ai_did_well: List[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.what_ai_missed is None:
            self.what_ai_missed = []
        if self.what_ai_did_well is None:
            self.what_ai_did_well = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ExpertExemplar:
    """Represents a gold standard exemplar response"""
    exemplar_id: str
    module_id: str
    scenario_id: str
    difficulty_level: str
    mastery_level: str  # 'emerging', 'developing', 'proficient', 'exemplary'
    response_text: str
    expert_commentary: str
    what_makes_it_good: List[str] = None
    what_would_improve: List[str] = None
    competency_scores: Dict[str, int] = None
    expert_name: str = "Unknown"
    created_at: datetime = None

    def __post_init__(self):
        if self.what_makes_it_good is None:
            self.what_makes_it_good = []
        if self.what_would_improve is None:
            self.what_would_improve = []
        if self.competency_scores is None:
            self.competency_scores = {}
        if self.created_at is None:
            self.created_at = datetime.now()


class ExpertKnowledgeRAG:
    """
    RAG system for expert knowledge (corrections, exemplars, patterns)
    Complements the literature RAG with expert-generated content
    """

    def __init__(
        self,
        db_path: str = None,
        embeddings_dir: str = None,
        embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO"
    ):
        """
        Initialize Expert Knowledge RAG system

        Args:
            db_path: Path to SQLite database (default: asp_expert_knowledge.db)
            embeddings_dir: Directory for ChromaDB embeddings (default: asp_literature/expert_embeddings/)
            embedding_model: Sentence transformer model (same as literature RAG for consistency)
        """
        # Set default paths
        project_root = Path(__file__).parent
        self.db_path = db_path or str(project_root / "asp_expert_knowledge.db")
        self.embeddings_dir = Path(embeddings_dir) if embeddings_dir else project_root / "asp_literature" / "expert_embeddings"

        # Ensure directories exist
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

        print(f"🎓 Initializing Expert Knowledge RAG System")
        print(f"   Database: {self.db_path}")
        print(f"   Embeddings: {self.embeddings_dir}")

        # Initialize database
        self._init_database()

        # Initialize embedding model (same as literature RAG for consistency)
        print(f"   Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        self.embedding_dimension = self.encoder.get_sentence_embedding_dimension()
        print(f"   ✓ Model loaded (embedding dim: {self.embedding_dimension})")

        # Initialize ChromaDB for vector search
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.embeddings_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Collections for different knowledge types
        self.corrections_collection = self.chroma_client.get_or_create_collection(
            name="expert_corrections",
            metadata={"description": "Expert corrections of AI feedback"}
        )

        self.exemplars_collection = self.chroma_client.get_or_create_collection(
            name="exemplar_responses",
            metadata={"description": "Gold standard responses at different mastery levels"}
        )

        print(f"✓ Expert Knowledge RAG initialized")
        print(f"  - Corrections indexed: {self.corrections_collection.count()}")
        print(f"  - Exemplars indexed: {self.exemplars_collection.count()}")

    def _init_database(self):
        """Initialize SQLite database with expert knowledge schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Expert corrections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_corrections (
                correction_id TEXT PRIMARY KEY,
                module_id TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                difficulty_level TEXT NOT NULL,
                competency_area TEXT NOT NULL,
                user_response TEXT NOT NULL,
                ai_feedback_original TEXT NOT NULL,
                expert_correction TEXT NOT NULL,
                expert_reasoning TEXT,
                expert_name TEXT,
                what_ai_missed TEXT,  -- JSON array
                what_ai_did_well TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Exemplar responses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_exemplars (
                exemplar_id TEXT PRIMARY KEY,
                module_id TEXT NOT NULL,
                scenario_id TEXT NOT NULL,
                difficulty_level TEXT NOT NULL,
                mastery_level TEXT NOT NULL,
                response_text TEXT NOT NULL,
                expert_commentary TEXT,
                what_makes_it_good TEXT,  -- JSON array
                what_would_improve TEXT,  -- JSON array
                competency_scores TEXT,  -- JSON object
                expert_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_corrections_scenario
            ON expert_corrections(scenario_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_corrections_competency
            ON expert_corrections(competency_area)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exemplars_scenario
            ON expert_exemplars(scenario_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_exemplars_mastery
            ON expert_exemplars(mastery_level)
        """)

        conn.commit()
        conn.close()
        print(f"   ✓ Database initialized")

    # ============================================================================
    # INDEXING METHODS
    # ============================================================================

    def add_correction(self, correction: ExpertCorrection) -> str:
        """
        Add an expert correction to the knowledge base

        Args:
            correction: ExpertCorrection object

        Returns:
            correction_id
        """
        # 1. Store in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expert_corrections (
                correction_id, module_id, scenario_id, difficulty_level, competency_area,
                user_response, ai_feedback_original, expert_correction, expert_reasoning,
                expert_name, what_ai_missed, what_ai_did_well
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            correction.correction_id,
            correction.module_id,
            correction.scenario_id,
            correction.difficulty_level,
            correction.competency_area,
            correction.user_response,
            correction.ai_feedback_original,
            correction.expert_correction,
            correction.expert_reasoning,
            correction.expert_name,
            json.dumps(correction.what_ai_missed),
            json.dumps(correction.what_ai_did_well)
        ))

        conn.commit()
        conn.close()

        # 2. Create searchable text for embedding
        searchable_text = self._create_correction_search_text(correction)

        # 3. Generate embedding
        embedding = self.encoder.encode(searchable_text)

        # 4. Store in ChromaDB for vector search
        self.corrections_collection.add(
            ids=[correction.correction_id],
            embeddings=[embedding.tolist()],
            metadatas=[{
                'module_id': correction.module_id,
                'scenario_id': correction.scenario_id,
                'difficulty_level': correction.difficulty_level,
                'competency_area': correction.competency_area,
                'expert_name': correction.expert_name
            }],
            documents=[searchable_text]
        )

        print(f"✓ Added correction {correction.correction_id}")
        return correction.correction_id

    def add_exemplar(self, exemplar: ExpertExemplar) -> str:
        """
        Add an exemplar response to the knowledge base

        Args:
            exemplar: ExpertExemplar object

        Returns:
            exemplar_id
        """
        # 1. Store in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expert_exemplars (
                exemplar_id, module_id, scenario_id, difficulty_level, mastery_level,
                response_text, expert_commentary, what_makes_it_good, what_would_improve,
                competency_scores, expert_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exemplar.exemplar_id,
            exemplar.module_id,
            exemplar.scenario_id,
            exemplar.difficulty_level,
            exemplar.mastery_level,
            exemplar.response_text,
            exemplar.expert_commentary,
            json.dumps(exemplar.what_makes_it_good),
            json.dumps(exemplar.what_would_improve),
            json.dumps(exemplar.competency_scores),
            exemplar.expert_name
        ))

        conn.commit()
        conn.close()

        # 2. Create searchable text
        searchable_text = f"""
Scenario: {exemplar.scenario_id}
Mastery Level: {exemplar.mastery_level}
Response: {exemplar.response_text}
Commentary: {exemplar.expert_commentary}
        """

        # 3. Generate embedding
        embedding = self.encoder.encode(searchable_text)

        # 4. Store in ChromaDB
        self.exemplars_collection.add(
            ids=[exemplar.exemplar_id],
            embeddings=[embedding.tolist()],
            metadatas=[{
                'module_id': exemplar.module_id,
                'scenario_id': exemplar.scenario_id,
                'mastery_level': exemplar.mastery_level,
                'difficulty_level': exemplar.difficulty_level
            }],
            documents=[searchable_text]
        )

        print(f"✓ Added exemplar {exemplar.exemplar_id} ({exemplar.mastery_level})")
        return exemplar.exemplar_id

    # ============================================================================
    # RETRIEVAL METHODS
    # ============================================================================

    def retrieve_corrections(
        self,
        scenario_id: str,
        user_response: str,
        competency_area: str = None,
        difficulty_level: str = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Retrieve expert corrections relevant to current evaluation context

        Args:
            scenario_id: Current scenario
            user_response: Fellow's response to evaluate
            competency_area: Filter by specific competency (optional)
            difficulty_level: Filter by difficulty (optional)
            n_results: Number of corrections to retrieve

        Returns:
            List of relevant expert corrections with context
        """
        # Build search query
        query_text = f"Scenario: {scenario_id}\nUser Response: {user_response}"
        if competency_area:
            query_text += f"\nCompetency: {competency_area}"

        # Generate query embedding
        query_embedding = self.encoder.encode(query_text)

        # Build filter
        where_filter = {}
        if competency_area:
            where_filter['competency_area'] = competency_area
        if difficulty_level:
            where_filter['difficulty_level'] = difficulty_level

        # Search ChromaDB
        results = self.corrections_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_filter if where_filter else None
        )

        # Fetch full details from SQLite
        corrections = []
        if results['ids'] and results['ids'][0]:
            correction_ids = results['ids'][0]

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(correction_ids))
            cursor.execute(f"""
                SELECT * FROM expert_corrections
                WHERE correction_id IN ({placeholders})
            """, correction_ids)

            for row in cursor.fetchall():
                correction_dict = dict(row)
                # Parse JSON fields
                correction_dict['what_ai_missed'] = json.loads(correction_dict['what_ai_missed'])
                correction_dict['what_ai_did_well'] = json.loads(correction_dict['what_ai_did_well'])
                corrections.append(correction_dict)

            conn.close()

        return corrections

    def retrieve_exemplars(
        self,
        scenario_id: str,
        mastery_level: str = None,
        n_results: int = 3
    ) -> List[Dict]:
        """
        Retrieve exemplar responses for a specific mastery level

        Args:
            scenario_id: Which scenario
            mastery_level: 'emerging', 'developing', 'proficient', 'exemplary' (optional)
            n_results: How many examples

        Returns:
            List of exemplar responses
        """
        query_text = f"Scenario: {scenario_id}"
        query_embedding = self.encoder.encode(query_text)

        where_filter = {}
        if mastery_level:
            where_filter['mastery_level'] = mastery_level

        results = self.exemplars_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_filter if where_filter else None
        )

        # Fetch full details
        exemplars = []
        if results['ids'] and results['ids'][0]:
            exemplar_ids = results['ids'][0]

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(exemplar_ids))
            cursor.execute(f"""
                SELECT * FROM expert_exemplars
                WHERE exemplar_id IN ({placeholders})
            """, exemplar_ids)

            for row in cursor.fetchall():
                exemplar_dict = dict(row)
                # Parse JSON fields
                exemplar_dict['what_makes_it_good'] = json.loads(exemplar_dict['what_makes_it_good'])
                exemplar_dict['what_would_improve'] = json.loads(exemplar_dict['what_would_improve'])
                exemplar_dict['competency_scores'] = json.loads(exemplar_dict['competency_scores'])
                exemplars.append(exemplar_dict)

            conn.close()

        return exemplars

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _create_correction_search_text(self, correction: ExpertCorrection) -> str:
        """Create optimized searchable text from correction"""
        text_parts = [
            f"Scenario: {correction.scenario_id}",
            f"Competency: {correction.competency_area}",
            f"Difficulty: {correction.difficulty_level}",
            f"\nUser Response: {correction.user_response}"
        ]

        if correction.expert_reasoning:
            text_parts.append(f"\nExpert Reasoning: {correction.expert_reasoning}")

        if correction.what_ai_missed:
            text_parts.append(f"\nWhat AI Missed: {'; '.join(correction.what_ai_missed)}")

        return '\n'.join(text_parts)

    def get_statistics(self) -> Dict:
        """Get statistics about indexed expert knowledge"""
        return {
            'corrections_count': self.corrections_collection.count(),
            'exemplars_count': self.exemplars_collection.count(),
            'embedding_model': 'PubMedBERT',
            'embedding_dimension': self.embedding_dimension
        }


def test_expert_rag():
    """Test the Expert Knowledge RAG system"""
    print("=" * 80)
    print("Expert Knowledge RAG - Test")
    print("=" * 80)

    # Initialize
    expert_rag = ExpertKnowledgeRAG()

    # Test 1: Add a sample correction
    print("\n" + "=" * 80)
    print("TEST 1: Adding sample expert correction")
    print("=" * 80)

    sample_correction = ExpertCorrection(
        correction_id=str(uuid.uuid4()),
        module_id='cicu_prolonged_antibiotics',
        scenario_id='cicu_beginner_data_analysis',
        difficulty_level='beginner',
        competency_area='data_analysis',
        user_response='We should reduce antibiotic use in the CICU by calculating DOT and comparing to benchmarks.',
        ai_feedback_original='Your approach is good. You mentioned calculating DOT and comparing to benchmarks, which is appropriate.',
        expert_correction='You identified the problem but didn\'t specify HOW you\'d calculate DOT. Show me the actual formula: DOT/1000 patient-days = (total antibiotic days / total patient days) × 1000. Also, what specific benchmark would you use? NHSN? SHARPS? Be concrete.',
        expert_reasoning='Fellows need concrete formulas, not just concepts. Vague statements don\'t demonstrate mastery of data analysis.',
        expert_name='Dr. Sarah Martinez',
        what_ai_missed=[
            'Requiring specific DOT calculation formula',
            'Asking which benchmark source',
            'Challenging vagueness with concrete examples'
        ],
        what_ai_did_well=['Acknowledged the general approach was correct']
    )

    correction_id = expert_rag.add_correction(sample_correction)
    print(f"✓ Added correction: {correction_id}")

    # Test 2: Retrieve relevant corrections
    print("\n" + "=" * 80)
    print("TEST 2: Retrieving relevant corrections")
    print("=" * 80)

    test_response = "I would calculate DOT for the CICU and see if it's higher than it should be."
    corrections = expert_rag.retrieve_corrections(
        scenario_id='cicu_beginner_data_analysis',
        user_response=test_response,
        competency_area='data_analysis',
        n_results=3
    )

    print(f"\nFound {len(corrections)} relevant corrections:")
    for i, corr in enumerate(corrections, 1):
        print(f"\n{i}. Expert {corr['expert_name']} said:")
        print(f"   What AI missed: {corr['what_ai_missed']}")
        print(f"   {corr['expert_correction'][:150]}...")

    # Test 3: Statistics
    print("\n" + "=" * 80)
    print("TEST 3: System statistics")
    print("=" * 80)

    stats = expert_rag.get_statistics()
    print(f"\nExpert Knowledge RAG Statistics:")
    print(f" - Corrections indexed: {stats['corrections_count']}")
    print(f" - Exemplars indexed: {stats['exemplars_count']}")
    print(f" - Embedding model: {stats['embedding_model']}")

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_expert_rag()
