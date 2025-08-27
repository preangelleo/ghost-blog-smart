#!/usr/bin/env python3
"""
🎨 Hybrid Image Generator - Google Imagen + Replicate Flux
Clean implementation with automatic fallback between providers
"""

import os
import time
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path
import sys

from google import genai
from google.genai import types
from PIL import Image
import io
from dotenv import load_dotenv

# Import blog to image prompt (also works for general image optimization)
from .blog_to_image_prompt import BLOG_TO_IMAGE_SYSTEM_PROMPT
# Import Replicate Flux generator for fallback
from .replicate_flux_generator import ReplicateFluxGenerator

# Model configuration constants
IMAGE_MODEL = "imagen-4.0-generate-001"  # Latest stable Imagen model
TEXT_MODEL = "gemini-2.5-flash"  # Model for prompt optimization


class CleanImagenGenerator:
    """
    Hybrid Image Generator with Google Imagen and Replicate Flux support
    Automatically falls back between providers for reliability
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, replicate_api_key: Optional[str] = None):
        """
        Initialize the hybrid image generator
        
        Args:
            api_key: Gemini API Key
            model_name: Optional custom model name (defaults to IMAGE_MODEL)
            replicate_api_key: Optional Replicate API key for Flux model fallback
        """
        load_dotenv()
        
        # Basic configuration
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Initialize Replicate Flux generator (optional)
        self.replicate_api_key = replicate_api_key or os.getenv('REPLICATE_API_TOKEN')
        self.flux_generator = ReplicateFluxGenerator(api_key=self.replicate_api_key) if self.replicate_api_key else None
        
        # Initialize client
        self.client = genai.Client(api_key=self.api_key)
        
        # Use specified model or default
        self.model_name = model_name or IMAGE_MODEL
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.default_config = {
            'output_directory': './generated_images',
            'save_metadata': True,
            'image_prefix': 'imagen_'
        }
        
        # Statistics
        self.generation_count = 0
        
        self.logger.info(f"✅ Initialized with model: {self.model_name}")
    
    def optimize_prompt(self, prompt: str) -> str:
        """
        Optimize prompt using blog to image system prompt
        
        Args:
            prompt: Original prompt
            
        Returns:
            Optimized prompt
        """
        try:
            # Use blog to image prompt for optimization
            full_instruction = BLOG_TO_IMAGE_SYSTEM_PROMPT + f"\n\nBlog Title: Image Generation\n\nBlog Content:\n{prompt}"
            
            response = self.client.models.generate_content(
                model=TEXT_MODEL,
                contents=full_instruction
            )
            
            optimized = response.candidates[0].content.parts[0].text.strip()
            self.logger.info(f"🔧 Prompt optimized: {prompt[:30]}... -> {optimized[:50]}...")
            return optimized
            
        except Exception as e:
            self.logger.warning(f"Prompt optimization failed: {e}, using original prompt")
            return prompt
    
    def generate_image(self, 
                      prompt: str,
                      aspect_ratio: str = "16:9",
                      number_of_images: int = 1,
                      person_generation: str = "allow_adult",
                      optimize_prompt: bool = True,
                      output_directory: Optional[str] = None,
                      image_prefix: str = "blog_feature_",
                      prefer_flux: bool = False) -> Dict[str, Any]:
        """
        Generate images with hybrid Google Imagen + Replicate Flux support
        
        Args:
            prompt: Image description
            aspect_ratio: Aspect ratio ("1:1", "3:4", "4:3", "9:16", "16:9")
            number_of_images: Number of images (1-4)
            person_generation: Person generation ("dont_allow", "allow_adult", "allow_all") 
            optimize_prompt: Whether to optimize prompt with AI
            output_directory: Output directory
            image_prefix: Filename prefix
            prefer_flux: Whether to prefer Replicate Flux over Google Imagen (when available)
            
        Returns:
            Generation result dictionary with provider information
        """
        
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Parameter validation
        valid_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"aspect_ratio must be one of: {valid_ratios}")
            
        if not 1 <= number_of_images <= 4:
            raise ValueError("number_of_images must be between 1-4")
        
        # Use configuration
        output_dir = output_directory or self.default_config['output_directory']
        os.makedirs(output_dir, exist_ok=True)
        
        # Optimize prompt if requested
        final_prompt = self.optimize_prompt(prompt) if optimize_prompt else prompt
        
        # Determine generation strategy
        use_flux_first = prefer_flux and self.flux_generator and self.flux_generator.is_available()
        
        # Try Replicate Flux first if preferred and available
        if use_flux_first:
            self.logger.info("🚀 Trying Replicate Flux first (user preference)...")
            flux_result = self._generate_with_flux(final_prompt, aspect_ratio, number_of_images, output_dir, image_prefix)
            if flux_result['success']:
                return flux_result
            else:
                self.logger.warning(f"⚠️ Flux generation failed: {flux_result['error']}")
                self.logger.info("🔄 Falling back to Google Imagen...")
        
        # Try Google Imagen
        imagen_result = self._generate_with_imagen(final_prompt, aspect_ratio, number_of_images, person_generation, output_dir, image_prefix, prompt)
        if imagen_result['success']:
            return imagen_result
        
        # If Imagen fails and we haven't tried Flux yet, try Flux as fallback
        if not use_flux_first and self.flux_generator and self.flux_generator.is_available():
            self.logger.warning(f"⚠️ Google Imagen failed: {imagen_result['error']}")
            self.logger.info("🔄 Falling back to Replicate Flux...")
            flux_result = self._generate_with_flux(final_prompt, aspect_ratio, number_of_images, output_dir, image_prefix)
            if flux_result['success']:
                return flux_result
        
        # Both failed or Flux not available
        return {
            'success': False,
            'error': f"All generation methods failed. Google Imagen: {imagen_result['error']}" + 
                    (f", Replicate Flux: Not available" if not self.flux_generator else ""),
            'prompt': prompt
        }
    
    def _generate_with_imagen(self, final_prompt: str, aspect_ratio: str, number_of_images: int, 
                            person_generation: str, output_dir: str, image_prefix: str, original_prompt: str) -> Dict[str, Any]:
        """Generate images using Google Imagen"""
        try:
            start_time = time.time()
            self.logger.info(f"🎨 Starting Google Imagen generation of {number_of_images} image(s)...")
            
            # Validate person generation for Imagen
            valid_person_gen = ["dont_allow", "allow_adult", "allow_all"]
            if person_generation not in valid_person_gen:
                person_generation = "allow_adult"  # Default fallback
            
            # Call Imagen API
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=final_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=number_of_images,
                    aspect_ratio=aspect_ratio,
                    person_generation=person_generation
                )
            )
            
            # Process results
            results = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, generated_image in enumerate(response.generated_images):
                # Open image
                image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                
                # Generate filename
                if number_of_images > 1:
                    filename = f"{image_prefix}{timestamp}_{i+1:03d}.png"
                else:
                    filename = f"{image_prefix}{timestamp}.png"
                
                filepath = os.path.abspath(os.path.join(output_dir, filename))
                
                # Save image
                image.save(filepath)
                
                # Result information
                result = {
                    'filepath': filepath,
                    'filename': filename,
                    'original_prompt': original_prompt,
                    'final_prompt': final_prompt,
                    'image_size': image.size,
                    'width': image.size[0],
                    'height': image.size[1],
                    'aspect_ratio': aspect_ratio,
                    'generation_time': time.time() - start_time,
                    'model': self.model_name,
                    'provider': 'Google Imagen'
                }
                
                # Save metadata
                if self.default_config['save_metadata']:
                    metadata_path = filepath.replace('.png', '_metadata.json')
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
                results.append(result)
                self.logger.info(f"✅ Image saved: {filename} ({image.size[0]}x{image.size[1]})")
            
            generation_time = time.time() - start_time
            self.generation_count += len(results)
            
            self.logger.info(f"🎉 Successfully generated {len(results)} image(s) with Google Imagen in {generation_time:.1f}s")
            
            return {
                'success': True,
                'results': results,
                'generation_time': generation_time,
                'total_images': len(results),
                'provider': 'Google Imagen'
            }
            
        except Exception as e:
            self.logger.error(f"Google Imagen generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'Google Imagen'
            }
    
    def _generate_with_flux(self, final_prompt: str, aspect_ratio: str, number_of_images: int, 
                           output_dir: str, image_prefix: str) -> Dict[str, Any]:
        """Generate images using Replicate Flux"""
        try:
            flux_result = self.flux_generator.generate_image(
                prompt=final_prompt,
                aspect_ratio=aspect_ratio,
                number_of_images=number_of_images,
                output_directory=output_dir,
                image_prefix=image_prefix
            )
            
            if flux_result['success']:
                # Update generation count
                self.generation_count += len(flux_result['results'])
                
                # Add provider information
                flux_result['provider'] = 'Replicate Flux'
                for result in flux_result['results']:
                    result['provider'] = 'Replicate Flux'
                
                self.logger.info(f"🎉 Successfully generated {flux_result['total_images']} image(s) with Replicate Flux")
            
            return flux_result
            
        except Exception as e:
            self.logger.error(f"Replicate Flux generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'Replicate Flux'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'total_generated': self.generation_count,
            'model_used': self.model_name
        }


def main():
    """Usage example"""
    
    # Initialize generator
    generator = CleanImagenGenerator()
    
    # Generate example
    result = generator.generate_image(
        prompt="A cute robot working in a candy factory",
        aspect_ratio="16:9",
        number_of_images=2,
        optimize_prompt=True
    )
    
    if result['success']:
        print(f"✅ Successfully generated {result['total_images']} image(s)")
        for img in result['results']:
            print(f"📁 {img['filename']} - {img['image_size']}")
    else:
        print(f"❌ Failed: {result['error']}")


if __name__ == "__main__":
    main()