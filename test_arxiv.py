#!/usr/bin/env python3
"""
Quick test for arXiv integration
"""

import requests
import xml.etree.ElementTree as ET

def test_arxiv_api():
    """Test arXiv API with a known DOI"""
    
    # Test with a known arXiv paper DOI
    test_doi = "10.48550/arXiv.2301.07041"  # This should definitely be in arXiv
    
    # Search arXiv - try both DOI and arXiv ID
    params = {
        'search_query': f'doi:{test_doi} OR id:2301.07041',
        'start': 0,
        'max_results': 1
    }
    
    try:
        response = requests.get(
            "https://export.arxiv.org/api/query",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        
        print(f"Testing arXiv API with DOI: {test_doi}")
        print(f"Found {len(entries)} entries")
        
        if entries:
            entry = entries[0]
            
            # Extract info
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            title = title_elem.text.strip() if title_elem is not None else 'unknown'
            
            id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
            arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else 'unknown'
            
            # Find PDF link
            pdf_link = None
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('type') == 'application/pdf':
                    pdf_link = link.get('href')
                    break
            
            print(f"Title: {title}")
            print(f"arXiv ID: {arxiv_id}")
            print(f"PDF Link: {pdf_link}")
            
            if pdf_link:
                print("✅ arXiv integration should work!")
                return True
            else:
                print("❌ No PDF link found")
                return False
        else:
            print("❌ No entries found in arXiv")
            return False
            
    except Exception as e:
        print(f"❌ Error testing arXiv API: {e}")
        return False

if __name__ == "__main__":
    test_arxiv_api() 