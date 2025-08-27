#!/usr/bin/env python3
"""
Ghost Blog Smart API - Complete Usage Examples

A powerful Python API for creating Ghost CMS blog posts with AI-powered features.

Supports both Class-based and Function-based approaches:

🏛️ CLASS-BASED APPROACH (Recommended):
   from ghost_blog_smart import GhostBlogSmart
   client = GhostBlogSmart()
   result = client.create_post(title="My Post", content="Content...")

⚙️ FUNCTION-BASED APPROACH:
   from ghost_blog_smart import create_ghost_blog_post
   result = create_ghost_blog_post(title="My Post", content="Content...")

🎨 DUAL IMAGE GENERATION:
   - Google Imagen-4: Professional quality, advanced prompt understanding
   - Replicate Flux-dev: Ultra-fast (3-7s), photorealistic images
   - Automatic fallback between providers for maximum reliability
"""

import os
from datetime import datetime, timedelta

# Method 1: Class-based imports (NEW - recommended for code assistants)
from ghost_blog_smart import GhostBlogSmart, create_client

# Method 2: Function-based imports (EXISTING - still supported)
from ghost_blog_smart import (
    # Core functions
    create_ghost_blog_post,
    get_ghost_posts,
    update_ghost_post,
    update_ghost_post_image,
    delete_ghost_post,
    
    # Smart Gateway
    smart_blog_gateway,
    
    # Advanced functions
    get_ghost_posts_advanced,
    get_ghost_post_details,
    get_posts_summary,
    batch_get_post_details,
    find_posts_by_date_pattern
)

# Configuration - Override these with your actual values
DEFAULT_CONFIG = {
    'ghost_admin_api_key': 'your_ghost_admin_api_key_here',
    'ghost_api_url': 'https://your-ghost-site.com',
    'gemini_api_key': 'your_gemini_api_key_here',
    'replicate_api_key': 'r8_your_replicate_api_token_here',  # For Flux generation
    'is_test': True  # Set to False for real posting
}

# ============================================================================
# USAGE PATTERN COMPARISON - Class-based vs Function-based
# ============================================================================

def compare_both_approaches():
    """
    Demonstrate both class-based and function-based approaches side by side.
    This shows that both methods produce identical results.
    """
    print("🔄 COMPARING BOTH APPROACHES")
    print("=" * 60)
    
    # ========== CLASS-BASED APPROACH ==========
    print("\n🏛️ CLASS-BASED APPROACH:")
    print("-" * 30)
    
    try:
        # Create client instance
        client = GhostBlogSmart(
            ghost_url=DEFAULT_CONFIG['ghost_api_url'],
            ghost_api_key=DEFAULT_CONFIG['ghost_admin_api_key'],
            gemini_api_key=DEFAULT_CONFIG['gemini_api_key']
        )
        
        print(f"✅ Client created: {client}")
        
        # Create a post using class method
        class_result = client.create_post(
            title="Class-Based Example Post",
            content="This post was created using the class-based approach.",
            tags=["Class-Based", "Example"],
            status="draft",
            is_test=True
        )
        
        print(f"Class result: {class_result['success']} - {class_result.get('message', '')}")
        
    except Exception as e:
        print(f"❌ Class approach error: {e}")
        class_result = {'success': False}
    
    # ========== FUNCTION-BASED APPROACH ==========
    print("\n⚙️ FUNCTION-BASED APPROACH:")
    print("-" * 30)
    
    try:
        # Create post using direct function call
        function_result = create_ghost_blog_post(
            title="Function-Based Example Post",
            content="This post was created using the function-based approach.",
            tags=["Function-Based", "Example"],
            status="draft",
            **DEFAULT_CONFIG
        )
        
        print(f"Function result: {function_result['success']} - {function_result.get('message', '')}")
        
    except Exception as e:
        print(f"❌ Function approach error: {e}")
        function_result = {'success': False}
    
    # ========== COMPARISON ==========
    print("\n📊 COMPARISON:")
    print("-" * 30)
    
    if class_result['success'] == function_result['success']:
        print("✅ Both approaches returned same success status")
    else:
        print("⚠️ Different success status between approaches")
    
    print(f"Class-based:    {'✅ Success' if class_result['success'] else '❌ Failed'}")
    print(f"Function-based: {'✅ Success' if function_result['success'] else '❌ Failed'}")
    
    print("\n💡 KEY INSIGHT: Both approaches use the same underlying functions!")
    print("   Choose the one that fits your coding style or framework requirements.")


def quick_start_examples():
    """
    Quick start examples for both approaches
    """
    print("\n🚀 QUICK START EXAMPLES")
    print("=" * 60)
    
    print("\n1️⃣ CLASS-BASED QUICK START:")
    print("""
    from ghost_blog_smart import GhostBlogSmart
    
    # Option A: Use environment variables (recommended)
    client = GhostBlogSmart()
    
    # Option B: Pass credentials explicitly  
    client = GhostBlogSmart(
        ghost_url="https://your-blog.com",
        ghost_api_key="your_api_key",
        gemini_api_key="your_gemini_key"
    )
    
    # Create a post
    result = client.create_post(
        title="My First Post",
        content="Hello world from the class-based approach!",
        tags=["First Post", "Hello World"]
    )
    
    # Use AI-powered smart creation
    result = client.smart_create_post(
        "Write a blog post about the benefits of Python for beginners"
    )
    
    # Get posts
    posts = client.get_posts(limit=5)
    
    # Update a post
    client.update_post(post_id="123", featured=True)
    """)
    
    print("\n2️⃣ FUNCTION-BASED QUICK START:")
    print("""
    from ghost_blog_smart import create_ghost_blog_post, smart_blog_gateway, get_ghost_posts
    
    # Create a post
    result = create_ghost_blog_post(
        title="My First Post",
        content="Hello world from the function-based approach!",
        tags=["First Post", "Hello World"],
        ghost_api_url="https://your-blog.com",
        ghost_admin_api_key="your_api_key"
    )
    
    # Use AI-powered smart creation
    result = smart_blog_gateway(
        "Write a blog post about the benefits of Python for beginners",
        ghost_api_url="https://your-blog.com",
        ghost_admin_api_key="your_api_key"
    )
    
    # Get posts
    posts = get_ghost_posts(
        limit=5,
        ghost_api_url="https://your-blog.com", 
        ghost_admin_api_key="your_api_key"
    )
    """)
    
    print("\n💡 RECOMMENDATION:")
    print("   - Use CLASS-BASED approach if you're building applications or using with code assistants")
    print("   - Use FUNCTION-BASED approach for scripts, notebooks, or when you need granular control")

def example_1_basic_post():
    """Example 1: Create a basic blog post"""
    print("=" * 50)
    print("EXAMPLE 1: Basic Blog Post")
    print("=" * 50)
    
    result = create_ghost_blog_post(
        title="Welcome to My Blog - Test Post",
        content="This is my first post using Ghost Blog Smart API. It demonstrates the basic functionality.",
        excerpt="Introduction to my blog",
        tags=["Welcome", "Test"],
        status="draft",  # Use draft for testing
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Post created successfully!")
        print(f"URL: {result['url']}")
        print(f"Post ID: {result['post_id']}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_2_smart_gateway_basic():
    """Example 2: Smart Gateway with basic input"""
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Smart Gateway - Basic Usage")
    print("=" * 50)
    
    result = smart_blog_gateway(
        user_input="Write about the benefits of remote work and its challenges",
        status="draft",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Smart Gateway post created!")
        print(f"URL: {result['url']}")
        print(f"Response: {result['response']}")
    else:
        print(f"❌ Failed: {result['response']}")
    
    return result

def example_3_smart_gateway_scattered_ideas():
    """Example 3: Smart Gateway with scattered ideas"""
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Smart Gateway - Transform Scattered Ideas")
    print("=" * 50)
    
    scattered_ideas = """
    AI in healthcare benefits:
    - Better diagnosis accuracy
    - Personalized treatment plans
    - Drug discovery acceleration
    - Medical imaging analysis
    
    Challenges:
    - Data privacy concerns
    - Integration with existing systems
    - Training medical staff
    - Cost of implementation
    """
    
    result = smart_blog_gateway(
        user_input=scattered_ideas,
        status="draft",
        preferred_language="English",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Scattered ideas transformed into structured post!")
        print(f"URL: {result['url']}")
    else:
        print(f"❌ Failed: {result['response']}")
    
    return result

def example_4_flux_image_generation():
    """Example 4: Post with Replicate Flux image generation (Ultra-fast)"""
    print("\n" + "=" * 50)
    print("EXAMPLE 4: Replicate Flux Image Generation")
    print("=" * 50)
    
    result = create_ghost_blog_post(
        title="AI Revolution in Photography",
        content="""
        # The Future of AI Photography
        
        Artificial intelligence is transforming how we create and edit photographs. 
        From automatic scene detection to intelligent composition suggestions, 
        AI tools are becoming indispensable for both professional and amateur photographers.
        
        ## Key Technologies
        
        - **Neural Style Transfer**: Apply artistic styles automatically
        - **Smart Object Removal**: Remove unwanted elements seamlessly  
        - **Intelligent Upscaling**: Enhance resolution without artifacts
        - **Auto Color Grading**: Professional color correction with AI
        
        The future of photography is here, and it's powered by artificial intelligence.
        """,
        excerpt="Discover how AI is revolutionizing photography with smart tools and techniques that enhance creativity and productivity.",
        tags=["AI", "Photography", "Technology", "Digital Art"],
        use_generated_feature_image=True,
        prefer_flux=True,  # Prefer ultra-fast Flux generation
        image_aspect_ratio="16:9",
        status="draft",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Post with Flux image created! (3-7s generation time)")
        print(f"URL: {result['url']}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_5_imagen_generation():
    """Example 5: Post with Google Imagen generation (Professional quality)"""
    print("\n" + "=" * 50)
    print("EXAMPLE 5: Google Imagen Generation")
    print("=" * 50)
    
    result = create_ghost_blog_post(
        title="Digital Art Mastery Guide",
        content="""
        # Creating Stunning Digital Art
        
        Digital art has evolved from simple pixel manipulation to sophisticated 
        AI-assisted creation. Modern artists combine traditional techniques 
        with cutting-edge technology to produce breathtaking visual experiences.
        
        ## Essential Tools
        
        - **Digital Painting Software**: Photoshop, Procreate, Clip Studio Paint
        - **3D Modeling**: Blender, Maya, Cinema 4D  
        - **AI Art Generators**: Midjourney, DALL-E, Stable Diffusion
        - **Vector Graphics**: Illustrator, Figma, Inkscape
        
        The key is finding the right balance between human creativity and AI assistance.
        """,
        excerpt="Master digital art creation with the perfect blend of traditional techniques and AI-powered tools.",
        tags=["Digital Art", "Creative Tools", "AI Art", "Design"],
        use_generated_feature_image=True,
        prefer_imagen=True,  # Prefer Google Imagen for artistic content
        image_aspect_ratio="16:9",
        status="draft",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Post with Imagen created! (Professional quality)")
        print(f"URL: {result['url']}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_6_auto_fallback_generation():
    """Example 6: Auto-fallback between Flux and Imagen"""
    print("\n" + "=" * 50)
    print("EXAMPLE 6: Auto-Fallback Image Generation")
    print("=" * 50)
    
    result = create_ghost_blog_post(
        title="Tech Innovation Landscape",
        content="""
        # The Innovation Ecosystem
        
        Today's technology landscape is more dynamic than ever. Startups are disrupting 
        traditional industries while established companies are racing to innovate.
        
        ## Key Innovation Areas
        
        - **Artificial Intelligence**: Machine learning, natural language processing
        - **Blockchain**: Decentralized applications, smart contracts
        - **IoT**: Connected devices, smart cities
        - **Quantum Computing**: Next-generation processing power
        
        Understanding these trends is crucial for staying competitive in the digital age.
        """,
        excerpt="Navigate the complex world of tech innovation with insights into key trends and emerging technologies.",
        tags=["Innovation", "Technology", "Startups", "Digital Transformation"],
        use_generated_feature_image=True,
        # No preference specified - will try Flux first, fallback to Imagen if needed
        image_aspect_ratio="16:9",
        status="draft",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Post with auto-fallback image created!")
        print(f"URL: {result['url']}")
        print(f"💡 Check logs to see which provider (Flux/Imagen) was used")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_7_smart_gateway_with_flux():
    """Example 7: Smart Gateway with Flux image generation"""
    print("\n" + "=" * 50)
    print("EXAMPLE 7: Smart Gateway + Flux Integration")
    print("=" * 50)
    
    # Raw content that needs AI enhancement
    raw_content = """
    machine learning healthcare diagnosis
    
    - AI can analyze medical images faster than doctors
    - Pattern recognition in X-rays, MRIs, CT scans
    - Early detection of cancer, heart disease
    - Reduce human error in diagnosis
    - 24/7 availability for remote areas
    - Cost reduction for healthcare systems
    
    challenges: data privacy, regulatory approval, doctor training
    """
    
    result = smart_blog_gateway(
        raw_content,
        status="draft",
        preferred_language="English",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Smart Gateway + Flux processed content successfully!")
        print(f"URL: {result['url']}")
        print(f"📝 Generated Title: {result.get('generated_title', 'None')}")
        print(f"🏷️ Generated Tags: {result.get('generated_tags', 'None')}")
        print(f"📄 Generated Excerpt: {result.get('generated_excerpt', 'None')}")
    else:
        print(f"❌ Failed: {result.get('response', 'No error message')}")
    
    return result

def example_8_youtube_video_post():
    """Example 5: Post with YouTube video"""
    print("\n" + "=" * 50)
    print("EXAMPLE 7: YouTube Video Post")
    print("=" * 50)
    
    result = create_ghost_blog_post(
        title="Amazing AI Tutorial Video",
        content="""
        # Check Out This Amazing AI Tutorial
        
        I found this incredible tutorial that explains machine learning concepts in a very clear way.
        The video covers everything from basic concepts to advanced applications.
        
        ## What You'll Learn:
        - Basic ML concepts
        - Popular algorithms
        - Real-world applications
        - Hands-on examples
        """,
        excerpt="A comprehensive AI tutorial video",
        youtube_video_id="dQw4w9WgXcQ",  # This becomes the slug
        use_generated_feature_image=True,
        tags=["Video", "Tutorial", "AI"],
        status="draft",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ YouTube video post created!")
        print(f"URL: {result['url']}")
        print(f"Slug from YouTube ID: dQw4w9WgXcQ")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_9_language_translation():
    """Example 6: Auto-translate content"""
    print("\n" + "=" * 50)
    print("EXAMPLE 9: Language Translation")
    print("=" * 50)
    
    result = create_ghost_blog_post(
        title="科技的未来",
        content="人工智能正在改变世界。医疗诊断更加准确，自动驾驶汽车即将成为现实，个性化教育正在成为可能。",
        excerpt="探索科技如何改变我们的生活",
        target_language="English",  # Translate to English
        tags=["科技", "AI", "未来"],
        status="draft",
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Translated post created!")
        print(f"URL: {result['url']}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_10_get_posts():
    """Example 7: Get and manage posts"""
    print("\n" + "=" * 50)
    print("EXAMPLE 10: Get Posts")
    print("=" * 50)
    
    result = get_ghost_posts(
        limit=5,
        status='all',
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Retrieved {len(result['posts'])} posts")
        for post in result['posts'][:3]:  # Show first 3
            print(f"- {post['title']} (Status: {post['status']})")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
    
    return result

def example_11_advanced_post_search():
    """Example 8: Advanced post search and filtering"""
    print("\n" + "=" * 50)
    print("EXAMPLE 11: Advanced Post Search")
    print("=" * 50)
    
    # Search for AI-related posts
    result = get_ghost_posts_advanced(
        search='AI',
        status='all',
        limit=5,
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Found {len(result['posts'])} AI-related posts")
        for post in result['posts']:
            print(f"- {post['title']}")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
    
    return result

def example_12_update_post():
    """Example 9: Update post properties (requires existing post)"""
    print("\n" + "=" * 50)
    print("EXAMPLE 12: Update Post Properties")
    print("=" * 50)
    
    # First get a post to update
    posts_result = get_ghost_posts(limit=1, **DEFAULT_CONFIG)
    
    if not posts_result['success'] or not posts_result['posts']:
        print("❌ No posts available to update. Create a post first.")
        return None
    
    post_id = posts_result['posts'][0]['id']
    print(f"Updating post: {posts_result['posts'][0]['title']}")
    
    result = update_ghost_post(
        post_id=post_id,
        excerpt="Updated excerpt - demonstrating update functionality",
        featured=True,
        tags=["Updated", "Featured"],
        **DEFAULT_CONFIG
    )
    
    if result['success']:
        print(f"✅ Post updated successfully!")
        print(f"Updates made: {result['updates']}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    return result

def example_13_test_mode():
    """Example 10: Demonstrate test mode (no actual posting)"""
    print("\n" + "=" * 50)
    print("EXAMPLE 13: Test Mode Demonstration")
    print("=" * 50)
    
    config_with_test = DEFAULT_CONFIG.copy()
    config_with_test['is_test'] = True
    
    result = create_ghost_blog_post(
        title="Test Mode Post - Should Not Actually Create",
        content="This demonstrates test mode functionality. No actual post will be created.",
        excerpt="Testing the test mode",
        tags=["Test"],
        status="published",  # Even with published, won't actually create
        **config_with_test
    )
    
    if result['success']:
        print(f"✅ Test mode working correctly!")
        print(f"Mock URL: {result['url']}")
        print(f"Mock Post ID: {result['post_id']}")
        print("Note: No actual post was created")
    else:
        print(f"❌ Test mode failed: {result['message']}")
    
    return result

def run_all_examples():
    """Run all examples in sequence"""
    print("🚀 GHOST BLOG SMART API - COMPLETE EXAMPLES")
    print("Dual image generation with Google Imagen + Replicate Flux")
    print("\n" + "=" * 80)
    
    # Check configuration
    if DEFAULT_CONFIG['is_test']:
        print("⚠️  RUNNING IN TEST MODE - No actual posts will be created")
    else:
        print("🔥 RUNNING IN PRODUCTION MODE - Posts will be created!")
    
    print(f"Ghost URL: {DEFAULT_CONFIG['ghost_api_url']}")
    print("=" * 80)
    
    # First show the usage pattern comparison
    compare_both_approaches()
    quick_start_examples()
    
    examples = [
        example_1_basic_post,
        example_2_smart_gateway_basic,
        example_3_smart_gateway_scattered_ideas,
        example_4_flux_image_generation,
        example_5_imagen_generation,
        example_6_auto_fallback_generation,
        example_7_smart_gateway_with_flux,
        example_8_youtube_video_post,
        example_9_language_translation,
        example_10_get_posts,
        example_11_advanced_post_search,
        example_12_update_post,
        example_13_test_mode
    ]
    
    results = []
    successful = 0
    
    for example in examples:
        try:
            result = example()
            results.append(result)
            if result and result.get('success'):
                successful += 1
            
            # Small delay between examples
            import time
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Exception in {example.__name__}: {str(e)}")
            results.append(None)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {successful}/{len(examples)} examples completed successfully")
    print("=" * 60)
    
    if successful == len(examples):
        print("🎉 All examples completed successfully!")
        print("✅ Ghost Blog Smart API is working perfectly!")
    else:
        print(f"⚠️  {len(examples) - successful} examples had issues.")
        print("Check the output above for details.")
    
    return results

if __name__ == "__main__":
    # You can run individual examples or all at once
    
    # To run all examples:
    run_all_examples()
    
    # To run individual examples, uncomment the ones you want:
    # example_1_basic_post()
    # example_2_smart_gateway_basic()
    # example_3_smart_gateway_scattered_ideas()
    # example_4_ai_image_generation()
    # example_5_youtube_video_post()
    # example_6_language_translation()
    # example_7_get_posts()
    # example_8_advanced_post_search()
    # example_9_update_post()
    # example_10_test_mode()