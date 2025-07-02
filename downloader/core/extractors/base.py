"""
Abstract base class for DOI extractors
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from ...utils import get_logger


@dataclass
class ExtractionResult:
    """Result of a DOI extraction operation"""
    dois: List[str]
    total_found: int
    unique_count: int
    duplicates_removed: int
    errors: List[str]
    source_format: str
    
    @property
    def success(self) -> bool:
        """Whether the extraction was successful"""
        return len(self.dois) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "source_format": self.source_format,
            "total_found": self.total_found,
            "unique_count": self.unique_count,
            "duplicates_removed": self.duplicates_removed,
            "total_errors": len(self.errors),
            "success": self.success,
            "errors": self.errors
        }


class BaseExtractor(ABC):
    """Abstract base class for DOI extractors"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def extract(self, input_path: Path, output_path: Path) -> ExtractionResult:
        """
        Extract DOIs from input file and save to output file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file for DOIs
            
        Returns:
            ExtractionResult with details about the extraction
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_path: Path) -> bool:
        """
        Validate that the input file is in the correct format.
        
        Args:
            input_path: Path to input file
            
        Returns:
            True if file format is valid, False otherwise
        """
        pass
    
    def _save_dois(self, dois: List[str], output_path: Path) -> bool:
        """
        Save DOIs to output file.
        
        Args:
            dois: List of DOI strings
            output_path: Path to output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                for doi in dois:
                    f.write(doi.strip() + "\n")
            self.logger.info(f"Saved {len(dois)} DOIs to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving DOIs to {output_path}: {e}")
            return False
    
    def _remove_duplicates(self, dois: List[str]) -> List[str]:
        """
        Remove duplicates while preserving order.
        
        Args:
            dois: List of DOI strings
            
        Returns:
            List with duplicates removed
        """
        seen = set()
        unique_dois = []
        for doi in dois:
            if doi not in seen:
                seen.add(doi)
                unique_dois.append(doi)
        return unique_dois 