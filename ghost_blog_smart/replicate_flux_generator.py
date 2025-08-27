#!/usr/bin/env python3
"""
Replicate Flux Image Generator
A wrapper around Replicate's Flux-dev model for high-quality image generation.
Provides fallback support for Google Imagen generation.
"""

import os
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplicateFluxGenerator:
    """
    Replicate Flux Image Generator using black-forest-labs/flux-dev model.
    Provides high-quality image generation with fallback to Google Imagen.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "black-forest-labs/flux-dev"):
        """
        Initialize the Replicate Flux generator.
        
        Args:
            api_key: Replicate API key. If None, will try to get from environment
            model_name: Replicate model name (default: black-forest-labs/flux-dev)
        """
        self.api_key = api_key or os.getenv('REPLICATE_API_TOKEN')
        self.model_name = model_name
        self.replicate = None
        
        # Try to import and initialize replicate
        if self.api_key:
            try:
                import replicate
                # Set API token in environment for replicate library
                os.environ['REPLICATE_API_TOKEN'] = self.api_key
                self.replicate = replicate
                logger.info(f"✅ Replicate Flux generator initialized with model: {self.model_name}")
            except ImportError:
                logger.warning("⚠️ Replicate library not installed. Install with: pip install replicate")
                self.replicate = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize Replicate: {str(e)}")
                self.replicate = None
        else:
            logger.info("ℹ️ No Replicate API token provided, Flux generation disabled")
    
    def is_available(self) -> bool:
        """Check if Replicate Flux generation is available."""
        return self.replicate is not None and self.api_key is not None
    
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        number_of_images: int = 1,
        output_directory: str = "./generated_images",
        image_prefix: str = "flux_",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate images using Replicate Flux model.
        
        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Image aspect ratio (default: "16:9")
            number_of_images: Number of images to generate (default: 1)
            output_directory: Directory to save images (default: "./generated_images")
            image_prefix: Prefix for saved image files (default: "flux_")
            **kwargs: Additional Flux-specific parameters
            
        Returns:
            Dict with success status, results list, and metadata
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Replicate Flux generator not available (missing API key or library)',
                'results': [],
                'model': self.model_name,
                'generation_time': 0
            }
        
        start_time = time.time()
        
        try:
            # Ensure output directory exists
            os.makedirs(output_directory, exist_ok=True)
            
            logger.info(f"🎨 Starting Flux generation of {number_of_images} image(s)...")
            logger.info(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            
            results = []
            
            for i in range(number_of_images):
                # Prepare Flux input parameters
                flux_input = {
                    "prompt": prompt,
                    "go_fast": kwargs.get('go_fast', True),
                    "guidance": kwargs.get('guidance', 3.5),
                    "megapixels": kwargs.get('megapixels', "1"),
                    "num_outputs": 1,  # Generate one at a time for better control
                    "aspect_ratio": self._convert_aspect_ratio(aspect_ratio),
                    "output_format": kwargs.get('output_format', 'webp'),
                    "output_quality": kwargs.get('output_quality', 80),
                    "prompt_strength": kwargs.get('prompt_strength', 0.8),
                    "num_inference_steps": kwargs.get('num_inference_steps', 28)
                }
                
                # Generate image with Replicate
                logger.info(f"🚀 Generating image {i+1}/{number_of_images}...")
                output = self.replicate.run(self.model_name, input=flux_input)
                
                if output and len(output) > 0:
                    # Download and save the image
                    image_url = output[0]
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    # Handle different aspect ratios for filename
                    aspect_suffix = aspect_ratio.replace(':', 'x')
                    filename = f"{image_prefix}{timestamp}_{aspect_suffix}.webp"
                    filepath = os.path.join(output_directory, filename)
                    
                    # Download image
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Get image dimensions
                    try:
                        from PIL import Image
                        with Image.open(filepath) as img:
                            width, height = img.size
                    except ImportError:
                        # Fallback if PIL not available
                        width, height = self._estimate_dimensions(aspect_ratio, flux_input['megapixels'])
                    
                    logger.info(f"✅ Image saved: {filename} ({width}x{height})")
                    
                    results.append({
                        'filepath': filepath,
                        'filename': filename,
                        'url': image_url,
                        'width': width,
                        'height': height,
                        'aspect_ratio': aspect_ratio,
                        'prompt': prompt,
                        'model': self.model_name
                    })
                else:
                    logger.error(f"❌ No output received for image {i+1}")
                    return {
                        'success': False,
                        'error': f'No output received from Flux model for image {i+1}',
                        'results': results,
                        'model': self.model_name,
                        'generation_time': time.time() - start_time
                    }
            
            generation_time = time.time() - start_time
            logger.info(f"🎉 Successfully generated {len(results)} image(s) in {generation_time:.1f}s")
            
            return {
                'success': True,
                'results': results,
                'model': self.model_name,
                'generation_time': generation_time,
                'prompt': prompt,
                'total_images': len(results)
            }
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Flux generation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'results': [],
                'model': self.model_name,
                'generation_time': generation_time
            }
    
    def _convert_aspect_ratio(self, aspect_ratio: str) -> str:
        """
        Convert aspect ratio to Flux-compatible format.
        
        Args:
            aspect_ratio: Aspect ratio string (e.g., "16:9", "1:1", "9:16")
            
        Returns:
            Flux-compatible aspect ratio string
        """
        # Flux supports: "1:1", "16:9", "9:16", "2:3", "3:2", "4:5", "5:4"
        flux_ratios = ["1:1", "16:9", "9:16", "2:3", "3:2", "4:5", "5:4"]
        
        if aspect_ratio in flux_ratios:
            return aspect_ratio
        
        # Map common ratios to Flux supported ones
        ratio_mapping = {
            "4:3": "4:5",  # Close approximation
            "3:4": "3:2",  # Close approximation
            "21:9": "16:9",  # Ultra-wide to standard wide
            "1.91:1": "16:9",  # Cinema to standard wide
        }
        
        return ratio_mapping.get(aspect_ratio, "1:1")  # Default to square
    
    def _estimate_dimensions(self, aspect_ratio: str, megapixels: str) -> tuple:
        """
        Estimate image dimensions based on aspect ratio and megapixels.
        
        Args:
            aspect_ratio: Aspect ratio string
            megapixels: Megapixels setting
            
        Returns:
            Tuple of (width, height)
        """
        # Convert megapixels to total pixels
        mp_map = {"0.25": 250000, "1": 1000000, "2": 2000000}
        total_pixels = mp_map.get(megapixels, 1000000)
        
        # Calculate dimensions based on aspect ratio
        try:
            w_ratio, h_ratio = map(int, aspect_ratio.split(':'))
            aspect = w_ratio / h_ratio
            
            height = int((total_pixels / aspect) ** 0.5)
            width = int(height * aspect)
            
            return width, height
        except:
            # Fallback for 1:1
            side = int(total_pixels ** 0.5)
            return side, side
    
    def optimize_prompt(self, prompt: str, target_language: str = "English") -> str:
        """
        Optimize prompt for Flux generation.
        Flux works best with detailed, descriptive prompts.
        
        Args:
            prompt: Original prompt
            target_language: Target language (Flux works best with English)
            
        Returns:
            Optimized prompt string
        """
        # Flux-specific prompt optimization
        # Add style and quality modifiers
        quality_terms = [
            "high quality", "detailed", "professional", "crisp", "sharp focus",
            "8k resolution", "masterpiece", "photorealistic"
        ]
        
        # Check if prompt already has quality terms
        prompt_lower = prompt.lower()
        has_quality = any(term in prompt_lower for term in quality_terms)
        
        if not has_quality:
            # Add quality modifiers
            prompt = f"{prompt}, high quality, detailed, professional photography, sharp focus"
        
        # Add Flux-specific styling if it's an artistic request
        artistic_keywords = ["art", "painting", "drawing", "illustration", "artistic"]
        if any(keyword in prompt_lower for keyword in artistic_keywords):
            if "style" not in prompt_lower:
                prompt += ", digital art style"
        
        return prompt


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Replicate Flux Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = ReplicateFluxGenerator()
    
    if generator.is_available():
        print("✅ Replicate Flux is available")
        
        # Test generation
        test_prompt = "A beautiful sunset over a mountain landscape, golden hour lighting, professional photography"
        
        print(f"🎨 Testing image generation...")
        print(f"📝 Prompt: {test_prompt}")
        
        result = generator.generate_image(
            prompt=test_prompt,
            aspect_ratio="16:9",
            number_of_images=1,
            go_fast=True,
            guidance=3.5
        )
        
        if result['success']:
            print(f"✅ Generation successful!")
            print(f"📁 Saved: {result['results'][0]['filename']}")
            print(f"⏱️ Time: {result['generation_time']:.1f}s")
        else:
            print(f"❌ Generation failed: {result['error']}")
    else:
        print("⚠️ Replicate Flux not available (missing API key or library)")
        print("💡 Set REPLICATE_API_TOKEN environment variable and install: pip install replicate")