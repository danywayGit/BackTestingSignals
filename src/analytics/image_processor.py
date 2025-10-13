"""
Image Processing for Algo Version Extraction

This module handles OCR and image processing to extract Algo version
information from Discord message attachments.
"""

import os
import requests
from typing import List, Dict, Any, Optional
import logging
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re
from io import BytesIO

logger = logging.getLogger(__name__)


class AlgoVersionExtractor:
    """Extract Algo version information from images using OCR"""
    
    def __init__(self, download_dir: str = "data/images"):
        """
        Initialize the extractor
        
        Args:
            download_dir: Directory to save downloaded images
        """
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
        # Patterns to match Algo version information
        self.algo_patterns = [
            r'(?:Algo|Algorithm)\s*[Vv]?(?:ersion)?\s*[:\-]?\s*([A-Za-z0-9\.\-_]+)',
            r'[Vv](?:ersion)?\s*([0-9]+(?:\.[0-9]+)*)',
            r'(?:AI|ML)\s*[Vv]?(?:ersion)?\s*[:\-]?\s*([A-Za-z0-9\.\-_]+)',
            r'(?:Model|Bot)\s*[Vv]?(?:ersion)?\s*[:\-]?\s*([A-Za-z0-9\.\-_]+)',
        ]
    
    def download_image(self, url: str, filename: str) -> Optional[str]:
        """
        Download image from URL
        
        Args:
            url: Image URL
            filename: Local filename to save
            
        Returns:
            Local file path if successful, None otherwise
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            # Try with original image first
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, config='--psm 6')
            
            # If not much text found, try with preprocessed image
            if len(text.strip()) < 10:
                processed_img = self.preprocess_image(image_path)
                pil_img = Image.fromarray(processed_img)
                text = pytesseract.image_to_string(pil_img, config='--psm 6')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image {image_path}: {e}")
            return ""
    
    def extract_algo_version(self, text: str) -> Optional[str]:
        """
        Extract Algo version from text using regex patterns
        
        Args:
            text: Text to search for Algo version
            
        Returns:
            Extracted Algo version or None
        """
        for pattern in self.algo_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                version = match.group(1).strip()
                logger.info(f"Found Algo version: {version}")
                return version
        
        return None
    
    def process_attachments(self, attachments: List[Dict[str, Any]], 
                          message_id: str) -> Dict[str, Any]:
        """
        Process all attachments from a Discord message
        
        Args:
            attachments: List of attachment dictionaries
            message_id: Discord message ID for unique filenames
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'processed_count': 0,
            'algo_versions': [],
            'extracted_texts': [],
            'downloaded_files': [],
            'errors': []
        }
        
        for i, attachment in enumerate(attachments):
            try:
                filename = attachment.get('filename', '')
                url = attachment.get('url', '')
                
                # Check if it's an image file
                if not self._is_image_file(filename):
                    continue
                
                # Create unique filename
                unique_filename = f"{message_id}_{i}_{filename}"
                
                # Download image
                local_path = self.download_image(url, unique_filename)
                if not local_path:
                    continue
                
                results['downloaded_files'].append(local_path)
                
                # Extract text from image
                extracted_text = self.extract_text_from_image(local_path)
                results['extracted_texts'].append({
                    'filename': filename,
                    'text': extracted_text
                })
                
                # Extract Algo version
                algo_version = self.extract_algo_version(extracted_text)
                if algo_version:
                    results['algo_versions'].append({
                        'filename': filename,
                        'version': algo_version,
                        'full_text': extracted_text
                    })
                
                results['processed_count'] += 1
                
            except Exception as e:
                error_msg = f"Error processing attachment {filename}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    def _is_image_file(self, filename: str) -> bool:
        """Check if file is an image based on extension"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']
        return any(filename.lower().endswith(ext) for ext in image_extensions)
    
    def batch_process_signals(self, signals_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch process all signals with attachments
        
        Args:
            signals_data: List of signal data dictionaries
            
        Returns:
            Summary of batch processing results
        """
        batch_results = {
            'total_messages': len(signals_data),
            'messages_with_attachments': 0,
            'total_images_processed': 0,
            'algo_versions_found': 0,
            'processing_errors': [],
            'results_by_message': {}
        }
        
        for msg_data in signals_data:
            message_id = msg_data.get('message_id', 'unknown')
            attachments = msg_data.get('attachments', [])
            
            if not attachments:
                continue
            
            batch_results['messages_with_attachments'] += 1
            
            # Process attachments for this message
            processing_result = self.process_attachments(attachments, message_id)
            
            batch_results['total_images_processed'] += processing_result['processed_count']
            batch_results['algo_versions_found'] += len(processing_result['algo_versions'])
            batch_results['processing_errors'].extend(processing_result['errors'])
            
            batch_results['results_by_message'][message_id] = processing_result
        
        return batch_results


def setup_tesseract():
    """
    Setup Tesseract OCR engine
    This function provides instructions for installing Tesseract
    """
    try:
        # Test if tesseract is available
        pytesseract.get_tesseract_version()
        logger.info("Tesseract OCR is available")
        return True
    except Exception:
        logger.error("Tesseract OCR not found!")
        print("\n🚨 TESSERACT OCR REQUIRED:")
        print("Tesseract OCR is required for image processing.")
        print("\nInstallation instructions:")
        print("1. Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - Install the .exe file")
        print("   - Add tesseract to your PATH")
        print("2. Mac: brew install tesseract")
        print("3. Linux: sudo apt-get install tesseract-ocr")
        print("\nAfter installation, you may need to specify the path:")
        print("pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        return False


if __name__ == "__main__":
    # Test the extractor
    setup_tesseract()
    
    extractor = AlgoVersionExtractor()
    
    # Test with sample text
    sample_text = "Algorithm Version: 2.1.5\nModel: Advanced AI Trading Bot"
    version = extractor.extract_algo_version(sample_text)
    print(f"Extracted version: {version}")