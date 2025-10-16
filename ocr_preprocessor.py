"""
OCR preprocessing module for improved text recognition accuracy.

Applies various image processing techniques to enhance OCR results.
"""
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import logging

logger = logging.getLogger('mtgalog')


class OCRPreprocessor:
    """Preprocesses images for better OCR accuracy."""
    
    def __init__(self, threshold=235, denoise=True, enhance_contrast=True, sharpen=True):
        """Initialize OCR preprocessor.
        
        Args:
            threshold: Pixel intensity threshold for binarization
            denoise: Whether to apply denoising
            enhance_contrast: Whether to enhance contrast
            sharpen: Whether to apply sharpening
        """
        self.threshold = threshold
        self.denoise = denoise
        self.enhance_contrast = enhance_contrast
        self.sharpen = sharpen
    
    def preprocess(self, img):
        """Apply preprocessing pipeline to an image.
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image
        """
        try:
            # Convert to grayscale if not already
            if img.mode != 'L':
                img = ImageOps.grayscale(img)
            
            # Step 1: Denoise (optional)
            if self.denoise:
                img = self._denoise(img)
            
            # Step 2: Enhance contrast (optional)
            if self.enhance_contrast:
                img = self._enhance_contrast(img)
            
            # Step 3: Apply filters
            img = img.filter(ImageFilter.SMOOTH)
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            
            # Step 4: Sharpen (optional)
            if self.sharpen:
                img = img.filter(ImageFilter.SHARPEN)
            
            # Step 5: Binarize (threshold)
            img = self._binarize(img, self.threshold)
            
            # Step 6: Final smoothing
            img = img.filter(ImageFilter.SMOOTH)
            img = img.filter(ImageFilter.EDGE_ENHANCE)
            
            return img
        
        except Exception as e:
            logger.error(f"Error in OCR preprocessing: {e}")
            return img
    
    def _denoise(self, img):
        """Apply median filter for denoising.
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Denoised image
        """
        return img.filter(ImageFilter.MedianFilter(size=3))
    
    def _enhance_contrast(self, img):
        """Enhance image contrast.
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Contrast-enhanced image
        """
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(2.0)  # Increase contrast by 2x
    
    def _binarize(self, img, threshold):
        """Convert image to binary (black and white) using threshold.
        
        Args:
            img: PIL Image object in 'L' mode
            threshold: Pixel intensity threshold
            
        Returns:
            PIL Image: Binarized image
        """
        img = img.convert('L')
        width, height = img.size
        
        # Invert pixels since text is white on screen
        # This leaves black text on white background (better for OCR)
        for x in range(width):
            for y in range(height):
                pixel_value = img.getpixel((x, y))
                if pixel_value < threshold:
                    img.putpixel((x, y), 255)  # White background
                else:
                    img.putpixel((x, y), 0)    # Black text
        
        return img
    
    def preprocess_with_adaptive_threshold(self, img):
        """Use adaptive thresholding for better results with varying lighting.
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image with adaptive threshold
        """
        try:
            # Convert to grayscale
            if img.mode != 'L':
                img = ImageOps.grayscale(img)
            
            # Denoise
            if self.denoise:
                img = self._denoise(img)
            
            # Enhance contrast
            if self.enhance_contrast:
                img = self._enhance_contrast(img)
            
            # Calculate adaptive threshold based on image histogram
            histogram = img.histogram()
            pixels = sum(histogram)
            
            # Find threshold using Otsu's method (simplified)
            threshold = self._otsu_threshold(histogram, pixels)
            logger.debug(f"Adaptive threshold calculated: {threshold}")
            
            # Apply threshold
            img = self._binarize(img, threshold)
            
            # Final filtering
            img = img.filter(ImageFilter.SMOOTH)
            
            return img
        
        except Exception as e:
            logger.error(f"Error in adaptive preprocessing: {e}")
            # Fall back to regular preprocessing
            return self.preprocess(img)
    
    def _otsu_threshold(self, histogram, total_pixels):
        """Calculate optimal threshold using Otsu's method.
        
        Args:
            histogram: Image histogram (256 values)
            total_pixels: Total number of pixels
            
        Returns:
            int: Optimal threshold value
        """
        sum_total = sum(i * histogram[i] for i in range(256))
        sum_background = 0
        weight_background = 0
        variance_max = 0
        threshold = 0
        
        for t in range(256):
            weight_background += histogram[t]
            if weight_background == 0:
                continue
            
            weight_foreground = total_pixels - weight_background
            if weight_foreground == 0:
                break
            
            sum_background += t * histogram[t]
            
            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground
            
            # Calculate between-class variance
            variance = (weight_background * weight_foreground *
                       (mean_background - mean_foreground) ** 2)
            
            if variance > variance_max:
                variance_max = variance
                threshold = t
        
        return threshold
    
    def preprocess_for_faint_text(self, img):
        """Specialized preprocessing for faint text (lower threshold).
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image optimized for faint text
        """
        original_threshold = self.threshold
        self.threshold = 75  # Lower threshold for faint text
        result = self.preprocess(img)
        self.threshold = original_threshold
        return result
    
    def preprocess_for_bright_text(self, img):
        """Specialized preprocessing for bright text (higher threshold).
        
        Args:
            img: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image optimized for bright text
        """
        original_threshold = self.threshold
        self.threshold = 238  # Higher threshold for bright text
        result = self.preprocess(img)
        self.threshold = original_threshold
        return result


# Factory functions for common use cases
def create_default_preprocessor():
    """Create a preprocessor with default settings."""
    return OCRPreprocessor(threshold=235, denoise=True, 
                          enhance_contrast=True, sharpen=True)


def create_faint_text_preprocessor():
    """Create a preprocessor optimized for faint text."""
    return OCRPreprocessor(threshold=75, denoise=True,
                          enhance_contrast=True, sharpen=True)


def create_bright_text_preprocessor():
    """Create a preprocessor optimized for bright text."""
    return OCRPreprocessor(threshold=238, denoise=True,
                          enhance_contrast=True, sharpen=False)


# Example usage and testing
if __name__ == "__main__":
    import pytesseract
    from PIL import ImageGrab
    
    print("OCR Preprocessor Test")
    print("-" * 40)
    
    # Test different preprocessing strategies
    preprocessors = {
        "Default": create_default_preprocessor(),
        "Faint Text": create_faint_text_preprocessor(),
        "Bright Text": create_bright_text_preprocessor(),
    }
    
    # Example: capture a region and test preprocessing
    # You would replace this with actual screen coordinates
    test_bbox = (1650, 980, 1830, 1020)
    
    print(f"\nCapturing region: {test_bbox}")
    print("Testing different preprocessors:")
    
    try:
        img = ImageGrab.grab(test_bbox)
        
        for name, preprocessor in preprocessors.items():
            processed_img = preprocessor.preprocess(img)
            print(f"\n{name}:")
            print(f"  Image size: {processed_img.size}")
            print(f"  Mode: {processed_img.mode}")
            
            # Optionally save for inspection
            # processed_img.save(f"test_{name.replace(' ', '_').lower()}.png")
    
    except Exception as e:
        print(f"Error: {e}")
        print("(This is expected if no screen is available)")
    
    print("\n" + "-" * 40)
    print("Preprocessing strategies available:")
    for name in preprocessors:
        print(f"  - {name}")

