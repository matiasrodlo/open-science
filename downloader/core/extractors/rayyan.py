"""
Rayyan CSV DOI extractor
"""

import csv
import json
from pathlib import Path
from typing import List

from .base import BaseExtractor, ExtractionResult
from ...utils import normalize_doi, validate_doi
from ...config import get_config


class RayyanExtractor(BaseExtractor):
    """Extract DOIs from Rayyan CSV files"""
    
    def extract(self, input_path: Path, output_path: Path) -> ExtractionResult:
        """
        Extract DOIs from a Rayyan CSV file.
        
        Args:
            input_path: Path to Rayyan CSV file
            output_path: Path to output file for DOIs
            
        Returns:
            ExtractionResult with extraction details
        """
        errors = []
        dois = []
        
        # Validate input
        if not self.validate_input(input_path):
            errors.append(f"Invalid or missing Rayyan CSV file: {input_path}")
            return ExtractionResult(
                dois=[], total_found=0, unique_count=0,
                duplicates_removed=0, errors=errors, source_format="Rayyan CSV"
            )
        
        # Read and parse CSV file
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                # Rayyan CSV uses semicolon delimiter
                csv_reader = csv.DictReader(file, delimiter=';')
                
                row_count = 0
                for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                    row_count = row_num - 1
                    try:
                        doi_raw = row.get('doi', '').strip()
                        if doi_raw and doi_raw != '':
                            # Normalize and validate DOI
                            doi = normalize_doi(doi_raw)
                            if validate_doi(doi):
                                dois.append(doi)
                            else:
                                self.logger.warning(f"Invalid DOI format at row {row_num}: {doi_raw}")
                                errors.append(f"Row {row_num}: Invalid DOI format - {doi_raw}")
                    except Exception as e:
                        self.logger.error(f"Error processing row {row_num}: {e}")
                        errors.append(f"Row {row_num}: Processing error - {e}")
                        
        except Exception as e:
            self.logger.error(f"Error reading {input_path}: {e}")
            errors.append(f"Failed to read CSV file: {e}")
            return ExtractionResult(
                dois=[], total_found=0, unique_count=0,
                duplicates_removed=0, errors=errors, source_format="Rayyan CSV"
            )
        
        if not dois:
            self.logger.warning("No valid DOIs found in Rayyan CSV file")
            errors.append("No valid DOI entries were found in the Rayyan CSV file")
        
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
            duplicates_removed=duplicates_removed, errors=errors, source_format="Rayyan CSV"
        )
        self._save_summary(result, row_count)
        
        self.logger.info(f"Extracted {len(unique_dois)} unique DOIs from {len(dois)} total DOIs in Rayyan CSV")
        
        return result
    
    def validate_input(self, input_path: Path) -> bool:
        """
        Validate Rayyan CSV file format.
        
        Args:
            input_path: Path to CSV file
            
        Returns:
            True if valid CSV file, False otherwise
        """
        if not input_path.exists() or not input_path.is_file():
            return False
        
        # Check file extension
        if input_path.suffix.lower() != '.csv':
            self.logger.warning(f"File {input_path} doesn't have .csv extension")
        
        # Check if file contains CSV-like content with semicolon delimiter
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                # Read first few lines to check format
                first_line = f.readline().strip()
                if ';' in first_line and 'doi' in first_line.lower():
                    return True
                else:
                    self.logger.warning(f"File {input_path} doesn't appear to be a Rayyan CSV with 'doi' column")
                    return False
        except Exception as e:
            self.logger.error(f"Error validating {input_path}: {e}")
            return False
    
    def _save_summary(self, result: ExtractionResult, total_records: int = 0):
        """Save extraction summary to JSON file"""
        try:
            config = get_config()
            summary_path = config.extraction_summary_file
            
            # Add Rayyan-specific information
            summary_data = result.to_dict()
            summary_data["total_records_processed"] = total_records
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2)
            
            self.logger.info(f"Extraction summary saved to {summary_path}")
        except Exception as e:
            self.logger.error(f"Error saving extraction summary: {e}")


# Convenience function for backward compatibility
def extract_dois_from_rayyan_csv(csv_path: str, output_path: str) -> int:
    """
    Legacy function for backward compatibility.
    
    Args:
        csv_path: Path to Rayyan CSV file
        output_path: Path to output file
        
    Returns:
        Number of DOIs extracted
    """
    extractor = RayyanExtractor()
    result = extractor.extract(Path(csv_path), Path(output_path))
    return result.unique_count 