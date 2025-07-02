"""
Scopus BibTeX DOI extractor
"""

import re
import json
from pathlib import Path
from typing import List

from .base import BaseExtractor, ExtractionResult
from ...utils import normalize_doi, validate_doi
from ...config import get_config


class ScopusExtractor(BaseExtractor):
    """Extract DOIs from Scopus BibTeX files"""
    
    def extract(self, input_path: Path, output_path: Path) -> ExtractionResult:
        """
        Extract DOIs from a Scopus BibTeX file.
        
        Args:
            input_path: Path to Scopus BibTeX file
            output_path: Path to output file for DOIs
            
        Returns:
            ExtractionResult with extraction details
        """
        errors = []
        dois = []
        
        # Validate input
        if not self.validate_input(input_path):
            errors.append(f"Invalid or missing Scopus BibTeX file: {input_path}")
            return ExtractionResult(
                dois=[], total_found=0, unique_count=0, 
                duplicates_removed=0, errors=errors, source_format="Scopus BibTeX"
            )
        
        # Read and parse BibTeX file
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            self.logger.error(f"Error reading {input_path}: {e}")
            errors.append(f"Error reading file: {e}")
            return ExtractionResult(
                dois=[], total_found=0, unique_count=0,
                duplicates_removed=0, errors=errors, source_format="Scopus BibTeX"
            )
        
        # Extract DOIs using regex
        # Match entries like DOI = {value} or DOI = "value"
        # Scopus may also use different field names
        doi_patterns = [
            r'DOI\s*=\s*[{"]([^}"]+)[}"]',  # Standard DOI field
            r'doi\s*=\s*[{"]([^}"]+)[}"]',  # Lowercase DOI
            r'url\s*=\s*[{"]https?://(?:dx\.)?doi\.org/([^}"]+)[}"]',  # DOI in URL field
        ]
        
        # Process all patterns
        for pattern in doi_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for doi_raw in matches:
                doi = normalize_doi(doi_raw)
                if validate_doi(doi):
                    dois.append(doi)
                else:
                    self.logger.warning(f"Invalid DOI format: {doi_raw}")
                    errors.append(f"Invalid DOI format: {doi_raw}")
        
        if not dois:
            self.logger.warning("No valid DOIs found in Scopus BibTeX file")
            errors.append("No valid DOI entries were found in the Scopus BibTeX file")
        
        # Remove duplicates
        unique_dois = self._remove_duplicates(dois)
        duplicates_removed = len(dois) - len(unique_dois)
        
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate DOIs")
        
        # Save DOIs to output file
        if unique_dois and not self._save_dois(unique_dois, output_path):
            errors.append("Failed to save DOIs to output file")
        
        # Save extraction summary
        result = ExtractionResult(
            dois=unique_dois, total_found=len(dois), unique_count=len(unique_dois),
            duplicates_removed=duplicates_removed, errors=errors, source_format="Scopus BibTeX"
        )
        self._save_summary(result)
        
        self.logger.info(f"Extracted {len(unique_dois)} unique DOIs from {len(dois)} total DOIs in Scopus BibTeX file")
        
        return result
    
    def validate_input(self, input_path: Path) -> bool:
        """
        Validate Scopus BibTeX file format.
        
        Args:
            input_path: Path to BibTeX file
            
        Returns:
            True if valid BibTeX file, False otherwise
        """
        if not input_path.exists() or not input_path.is_file():
            return False
        
        # Check file extension
        if input_path.suffix.lower() not in ['.bib', '.bibtex']:
            self.logger.warning(f"File {input_path} doesn't have .bib or .bibtex extension")
        
        # Check if file contains BibTeX-like content
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
                # Look for BibTeX entry patterns
                if '@' in content and '{' in content:
                    return True
                else:
                    self.logger.warning(f"File {input_path} doesn't appear to contain BibTeX entries")
                    return False
        except Exception as e:
            self.logger.error(f"Error validating {input_path}: {e}")
            return False
    
    def _save_summary(self, result: ExtractionResult):
        """Save extraction summary to JSON file"""
        try:
            config = get_config()
            summary_path = config.extraction_summary_file
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2)
            
            self.logger.info(f"Extraction summary saved to {summary_path}")
        except Exception as e:
            self.logger.error(f"Error saving extraction summary: {e}")


# Convenience function for backward compatibility
def extract_dois_from_scopus_bibtex(bibtex_path: str, output_path: str) -> int:
    """
    Legacy function for backward compatibility.
    
    Args:
        bibtex_path: Path to Scopus BibTeX file
        output_path: Path to output file
        
    Returns:
        Number of DOIs extracted
    """
    extractor = ScopusExtractor()
    result = extractor.extract(Path(bibtex_path), Path(output_path))
    return result.unique_count 