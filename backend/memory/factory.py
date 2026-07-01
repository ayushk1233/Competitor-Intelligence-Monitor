from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any

from backend.models.schemas import CompetitorAnalysis, ComparisonResult, IntelligenceReport
from backend.memory.document import MemoryDocument
from backend.database.models import EmbeddingSourceType, ChunkType


class MemoryDocumentFactory:
    """
    Anti-Corruption Layer (ACL) that translates Analysis domain objects
    into Memory domain objects (MemoryDocument).
    """

    @staticmethod
    def _dict_to_prose(data: Dict[str, Any]) -> str:
        """
        Convert a dictionary into human-readable prose.
        Format:
        Key:
        Value
        """
        lines = []
        for key, value in data.items():
            if not value and value != 0 and value is not False:
                continue
                
            clean_key = str(key).replace("_", " ").title()
            
            if isinstance(value, list):
                if not value:
                    continue
                val_str = "\n".join(f"- {v}" for v in value)
            elif isinstance(value, dict):
                val_str = MemoryDocumentFactory._dict_to_prose(value)
            else:
                val_str = str(value)
                
            if not val_str.strip():
                continue
                
            lines.append(f"{clean_key}:\n{val_str}\n")
            
        return "\n".join(lines).strip()

    @staticmethod
    def from_competitor_analysis(
        analysis: CompetitorAnalysis,
        *,
        organization_id: UUID,
        run_id: str,
        analyzed_at: datetime,
    ) -> List[MemoryDocument]:
        documents = []
        company_name = analysis.name

        base_metadata = {
            "generator": "memory_factory",
            "analysis_version": 1,
            "source_model": "CompetitorAnalysis"
        }

        # Document 1: EXECUTIVE_BRIEFING
        if analysis.analyst_note and analysis.analyst_note.strip():
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.ANALYSIS,
                source_id=analysis.name,
                chunk_type=ChunkType.EXECUTIVE_BRIEFING,
                text=analysis.analyst_note.strip(),
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        # Document 2: STRUCTURED_SUMMARIES
        structured_fields = {
            "Core Offering": analysis.core_offering,
            "ICP": analysis.icp,
            "Messaging Tone": analysis.messaging_tone,
            "Pricing": analysis.pricing_signals,
            "Hiring": analysis.hiring_signals,
            "Momentum Score": analysis.momentum_score,
            "Growth Signals": analysis.growth_signals,
            "Risk Flags": analysis.risk_flags,
        }
        
        structured_prose = MemoryDocumentFactory._dict_to_prose(structured_fields)
        if structured_prose:
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.ANALYSIS,
                source_id=analysis.name,
                chunk_type=ChunkType.STRUCTURED_SUMMARIES,
                text=structured_prose,
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        # Document 3: strategic_interpretation
        if analysis.strategic_interpretation:
            strategic_prose = MemoryDocumentFactory._dict_to_prose(analysis.strategic_interpretation)
            if strategic_prose:
                documents.append(MemoryDocument(
                    organization_id=organization_id,
                    run_id=run_id,
                    company_name=company_name,
                    source_type=EmbeddingSourceType.ANALYSIS,
                    source_id=analysis.name,
                    chunk_type=ChunkType.STRUCTURED_SUMMARIES,
                    text=strategic_prose,
                    analyzed_at=analyzed_at,
                    metadata=base_metadata
                ))
                
        # Document 4: competitor_dna
        if analysis.competitor_dna:
            dna_prose = MemoryDocumentFactory._dict_to_prose(analysis.competitor_dna)
            if dna_prose:
                documents.append(MemoryDocument(
                    organization_id=organization_id,
                    run_id=run_id,
                    company_name=company_name,
                    source_type=EmbeddingSourceType.ANALYSIS,
                    source_id=analysis.name,
                    chunk_type=ChunkType.STRUCTURED_SUMMARIES,
                    text=dna_prose,
                    analyzed_at=analyzed_at,
                    metadata=base_metadata
                ))

        return documents

    @staticmethod
    def from_comparison_result(
        comparison: ComparisonResult,
        *,
        organization_id: UUID,
        run_id: str,
        analyzed_at: datetime,
    ) -> List[MemoryDocument]:
        documents = []
        company_name = "Comparison" 

        base_metadata = {
            "generator": "memory_factory",
            "analysis_version": 1,
            "source_model": "ComparisonResult"
        }

        # Document: executive_briefing
        if comparison.executive_briefing and comparison.executive_briefing.strip():
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.COMPARISON_BRIEF,
                source_id="comparison",
                chunk_type=ChunkType.EXECUTIVE_BRIEFING,
                text=comparison.executive_briefing.strip(),
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        # Document: messaging_gaps
        if comparison.messaging_gaps and comparison.messaging_gaps.strip():
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.COMPARISON_BRIEF,
                source_id="comparison",
                chunk_type=ChunkType.COMPARISON_SUMMARY,
                text=f"Messaging Gaps:\n{comparison.messaging_gaps.strip()}",
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        # Document: threat_ranking
        if comparison.threat_ranking:
            threats = []
            reasons = comparison.threat_ranking_reasons or []
            
            for i, t in enumerate(comparison.threat_ranking):
                r = reasons[i] if i < len(reasons) else ""
                threats.append(f"{t}: {r}".strip())
                
            text = "Threat Ranking:\n" + "\n".join(f"- {t}" for t in threats)
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.COMPARISON_BRIEF,
                source_id="comparison",
                chunk_type=ChunkType.COMPARISON_SUMMARY,
                text=text,
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        # Document: market_leader_reason
        if comparison.market_leader and comparison.market_leader_reason:
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.COMPARISON_BRIEF,
                source_id="comparison",
                chunk_type=ChunkType.COMPARISON_SUMMARY,
                text=f"Market Leader: {comparison.market_leader}\nReason:\n{comparison.market_leader_reason.strip()}",
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        # Document: fastest_mover_reason
        if comparison.fastest_mover and comparison.fastest_mover_reason:
            documents.append(MemoryDocument(
                organization_id=organization_id,
                run_id=run_id,
                company_name=company_name,
                source_type=EmbeddingSourceType.COMPARISON_BRIEF,
                source_id="comparison",
                chunk_type=ChunkType.COMPARISON_SUMMARY,
                text=f"Fastest Mover: {comparison.fastest_mover}\nReason:\n{comparison.fastest_mover_reason.strip()}",
                analyzed_at=analyzed_at,
                metadata=base_metadata
            ))

        return documents

    @staticmethod
    def from_report(
        report: IntelligenceReport,
        *,
        organization_id: UUID,
        run_id: str,
        analyzed_at: datetime,
    ) -> List[MemoryDocument]:
        documents = []
        for competitor in report.competitors:
            documents.extend(
                MemoryDocumentFactory.from_competitor_analysis(
                    competitor,
                    organization_id=organization_id,
                    run_id=run_id,
                    analyzed_at=analyzed_at,
                )
            )
        
        if report.comparison:
            documents.extend(
                MemoryDocumentFactory.from_comparison_result(
                    report.comparison,
                    organization_id=organization_id,
                    run_id=run_id,
                    analyzed_at=analyzed_at,
                )
            )
            
        return documents
