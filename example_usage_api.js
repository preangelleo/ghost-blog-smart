#!/usr/bin/env node
/**
 * Ghost Blog Smart API - Node.js Example Usage
 * 
 * A comprehensive Node.js example demonstrating how to interact with all
 * Ghost Blog Smart API endpoints. This example is designed for developers
 * to easily copy and modify for their own applications.
 * 
 * Dependencies:
 * - axios (for HTTP requests)
 * - node (Node.js runtime)
 * 
 * Setup:
 * npm install axios
 * node example_usage_API.js
 */

const axios = require('axios');

// ============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================================================

const CONFIG = {
    // API Configuration
    baseUrl: process.env.API_BASE_URL || 'http://localhost:5000',
    apiKey: process.env.FLASK_API_KEY || 'your_secure_api_key_here',
    
    // Ghost Blog Configuration
    ghostApiKey: process.env.GHOST_ADMIN_API_KEY || 'your_ghost_key_id:your_ghost_secret_key',
    ghostApiUrl: process.env.GHOST_API_URL || 'https://your-ghost-site.com',
    
    // AI Services Configuration
    geminiApiKey: process.env.GEMINI_API_KEY || 'your_gemini_api_key_here',
    replicateApiKey: process.env.REPLICATE_API_TOKEN || 'r8_your_replicate_token_here',
    
    // Test Configuration
    testMode: process.env.TEST_MODE === 'false' ? false : true, // Set to false for actual posting
    timeout: parseInt(process.env.API_TIMEOUT) || 300000, // 5 minutes timeout (300 seconds) - Required for image generation
    imageTimeout: parseInt(process.env.IMAGE_API_TIMEOUT) || 300000, // 5 minutes for image endpoints
    standardTimeout: parseInt(process.env.STANDARD_API_TIMEOUT) || 30000, // 30 seconds for non-image endpoints
    rateLimitDelay: parseInt(process.env.RATE_LIMIT_DELAY) || 1000, // 1 second between requests
};

// ============================================================================
// AXIOS SETUP WITH DEFAULT HEADERS
// ============================================================================

const api = axios.create({
    baseURL: CONFIG.baseUrl,
    timeout: CONFIG.timeout,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': CONFIG.apiKey,
        'X-Ghost-API-Key': CONFIG.ghostApiKey,
        'X-Ghost-API-URL': CONFIG.ghostApiUrl,
        'X-Gemini-API-Key': CONFIG.geminiApiKey,
        'X-Replicate-API-Key': CONFIG.replicateApiKey,
    }
});

// Create separate instance for image generation endpoints with extended timeout
const apiImage = axios.create({
    baseURL: CONFIG.baseUrl,
    timeout: CONFIG.imageTimeout,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': CONFIG.apiKey,
        'X-Ghost-API-Key': CONFIG.ghostApiKey,
        'X-Ghost-API-URL': CONFIG.ghostApiUrl,
        'X-Gemini-API-Key': CONFIG.geminiApiKey,
        'X-Replicate-API-Key': CONFIG.replicateApiKey,
    }
});

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Log API response in a formatted way
 */
function logResponse(label, response) {
    console.log(`\n🔍 ${label}`);
    console.log('=' .repeat(60));
    console.log(`Status: ${response.status} ${response.statusText}`);
    console.log(`Success: ${response.data.success ? '✅ Yes' : '❌ No'}`);
    console.log(`Timestamp: ${response.data.timestamp}`);
    
    if (response.data.data) {
        console.log('Data:', JSON.stringify(response.data.data, null, 2));
    }
    
    if (response.data.error || response.data.message) {
        console.log(`Message: ${response.data.error || response.data.message}`);
    }
}

/**
 * Handle API errors gracefully
 */
function handleError(label, error) {
    console.error(`\n❌ ${label} FAILED`);
    console.error('=' .repeat(60));
    
    if (error.response) {
        console.error(`Status: ${error.response.status} ${error.response.statusText}`);
        console.error('Response:', JSON.stringify(error.response.data, null, 2));
    } else if (error.request) {
        console.error('Network Error: No response received');
        console.error('Request:', error.request);
    } else {
        console.error('Error:', error.message);
    }
    
    return { success: false, error: error.message };
}

/**
 * Sleep function for delays between API calls
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Validate configuration and credentials
 */
function validateConfig() {
    const required = ['baseUrl', 'apiKey', 'ghostApiKey', 'ghostApiUrl'];
    const missing = [];
    
    for (const key of required) {
        if (!CONFIG[key] || CONFIG[key].includes('your_')) {
            missing.push(key);
        }
    }
    
    if (missing.length > 0) {
        console.error('❌ Missing or invalid configuration:');
        missing.forEach(key => console.error(`  - ${key}: ${CONFIG[key]}`));
        console.error('\n💡 Please set environment variables or update CONFIG object.');
        return false;
    }
    
    return true;
}

/**
 * Clean up large response objects to prevent memory issues
 */
function cleanupResponse(response) {
    if (response && response.data && typeof response.data === 'object') {
        // Keep only essential data, remove large content fields
        const cleaned = { ...response };
        if (cleaned.data.content && cleaned.data.content.length > 1000) {
            cleaned.data.content = cleaned.data.content.substring(0, 1000) + '... [truncated]';
        }
        return cleaned;
    }
    return response;
}

/**
 * Validate command line arguments
 */
function validateCliArgs(args) {
    const validTests = ['health', 'info', 'create', 'smart', 'get', 'search', 'summary', 'date'];
    const validOptions = ['--help', '-h', '--production', '--baseurl', '--timeout'];
    
    for (const arg of args) {
        if (arg.startsWith('--')) {
            if (!validOptions.includes(arg) && !arg.startsWith('--baseurl') && !arg.startsWith('--timeout')) {
                console.error(`❌ Invalid option: ${arg}`);
                return false;
            }
        } else if (!validTests.includes(arg) && !arg.match(/^https?:\/\/.+/) && !arg.match(/^\d+$/)) {
            console.error(`❌ Invalid test name: ${arg}`);
            console.error(`Valid tests: ${validTests.join(', ')}`);
            return false;
        }
    }
    
    return true;
}

// ============================================================================
// API ENDPOINT EXAMPLES
// ============================================================================

/**
 * 1. Health Check - Test API connectivity
 */
async function testHealthCheck() {
    try {
        const response = await api.get('/health');
        logResponse('HEALTH CHECK', response);
        return response.data;
    } catch (error) {
        return handleError('HEALTH CHECK', error);
    }
}

/**
 * 2. Get API Information
 */
async function testApiInfo() {
    try {
        const response = await api.get('/');
        logResponse('API INFO', response);
        return response.data;
    } catch (error) {
        return handleError('API INFO', error);
    }
}

/**
 * 3. Create Basic Blog Post
 */
async function testCreatePost() {
    const postData = {
        title: "Node.js API Test Post",
        content: `# Welcome to Ghost Blog Smart API Testing

This post was created using the Node.js example API client.

## Features Tested
- ✅ Basic post creation
- ✅ Markdown content formatting  
- ✅ Tag assignment
- ✅ Status management

## Technical Details
- Created via REST API
- Uses authentication headers
- Supports dual image generation
- Full CRUD operations available

## Next Steps
Test all other API endpoints to ensure full functionality.`,
        excerpt: "A test post created via Node.js API client to verify functionality",
        tags: ["Test", "Node.js", "API", "Automation"],
        status: "draft",
        use_generated_feature_image: true,
        prefer_flux: true,
        image_aspect_ratio: "16:9",
        is_test: CONFIG.testMode
    };
    
    try {
        // Use image API client for posts with image generation
        const apiClient = postData.use_generated_feature_image ? apiImage : api;
        console.log(`⏱️ Using ${postData.use_generated_feature_image ? 'extended (5min)' : 'standard (30s)'} timeout for this request...`);
        
        const response = await apiClient.post('/api/posts', postData);
        logResponse('CREATE POST', response);
        return response.data;
    } catch (error) {
        return handleError('CREATE POST', error);
    }
}

/**
 * 4. Smart Create Blog Post (AI-Enhanced)
 */
async function testSmartCreate() {
    const smartData = {
        user_input: `JavaScript testing frameworks comparison:
        
        Jest:
        - Popular, easy setup
        - Great mocking capabilities
        - Snapshot testing
        - Built-in assertions
        
        Mocha:
        - Flexible, minimalist
        - Choose your own assertion library
        - Great for async testing
        - Good ecosystem
        
        Cypress:
        - E2E testing focus
        - Real browser testing
        - Time-travel debugging
        - Visual testing
        
        Compare these for a new Node.js project`,
        status: "draft",
        preferred_language: "English",
        is_test: CONFIG.testMode
    };
    
    try {
        const response = await api.post('/api/smart-create', smartData);
        logResponse('SMART CREATE', response);
        return response.data;
    } catch (error) {
        return handleError('SMART CREATE', error);
    }
}

/**
 * 5. Get Blog Posts (with filters)
 */
async function testGetPosts() {
    const params = {
        limit: 10,
        status: 'all',
        featured: false
    };
    
    try {
        const response = await api.get('/api/posts', { params });
        logResponse('GET POSTS', response);
        return response.data;
    } catch (error) {
        return handleError('GET POSTS', error);
    }
}

/**
 * 6. Advanced Posts Search
 */
async function testAdvancedSearch() {
    const params = {
        search: 'API',
        tag: 'Test',
        limit: 5,
        status: 'all'
    };
    
    try {
        const response = await api.get('/api/posts/advanced', { params });
        logResponse('ADVANCED SEARCH', response);
        return response.data;
    } catch (error) {
        return handleError('ADVANCED SEARCH', error);
    }
}

/**
 * 7. Get Post Details (requires post ID)
 */
async function testGetPostDetails(postId) {
    if (!postId) {
        console.log('\n⚠️  Skipping GET POST DETAILS - No post ID provided');
        return { success: false, error: 'No post ID provided' };
    }
    
    try {
        const response = await api.get(`/api/posts/${postId}`);
        logResponse('GET POST DETAILS', response);
        return response.data;
    } catch (error) {
        return handleError('GET POST DETAILS', error);
    }
}

/**
 * 8. Update Post (requires post ID)
 */
async function testUpdatePost(postId) {
    if (!postId) {
        console.log('\n⚠️  Skipping UPDATE POST - No post ID provided');
        return { success: false, error: 'No post ID provided' };
    }
    
    const updateData = {
        title: "Updated Node.js API Test Post",
        excerpt: "Updated excerpt - demonstrating API update functionality",
        featured: true,
        tags: ["Updated", "Node.js", "API", "Featured"]
    };
    
    try {
        const response = await api.put(`/api/posts/${postId}`, updateData);
        logResponse('UPDATE POST', response);
        return response.data;
    } catch (error) {
        return handleError('UPDATE POST', error);
    }
}

/**
 * 9. Update Post Image (requires post ID)
 */
async function testUpdatePostImage(postId) {
    if (!postId) {
        console.log('\n⚠️  Skipping UPDATE POST IMAGE - No post ID provided');
        return { success: false, error: 'No post ID provided' };
    }
    
    const imageData = {
        use_generated_feature_image: true,
        prefer_imagen: true, // Use Google Imagen instead of Flux
        image_aspect_ratio: "1:1"
    };
    
    try {
        console.log(`⏱️ Using extended timeout (5min) for image generation...`);
        // Always use image API client for image generation endpoints
        const response = await apiImage.put(`/api/posts/${postId}/image`, imageData);
        logResponse('UPDATE POST IMAGE', response);
        return response.data;
    } catch (error) {
        return handleError('UPDATE POST IMAGE', error);
    }
}

/**
 * 10. Get Posts Summary
 */
async function testPostsSummary() {
    const params = {
        days: 30
    };
    
    try {
        const response = await api.get('/api/posts/summary', { params });
        logResponse('POSTS SUMMARY', response);
        return response.data;
    } catch (error) {
        return handleError('POSTS SUMMARY', error);
    }
}

/**
 * 11. Batch Get Post Details
 */
async function testBatchGetDetails(postIds = []) {
    if (postIds.length === 0) {
        console.log('\n⚠️  Skipping BATCH GET DETAILS - No post IDs provided');
        return { success: false, error: 'No post IDs provided' };
    }
    
    const batchData = {
        post_ids: postIds
    };
    
    try {
        const response = await api.post('/api/posts/batch-details', batchData);
        logResponse('BATCH GET DETAILS', response);
        return response.data;
    } catch (error) {
        return handleError('BATCH GET DETAILS', error);
    }
}

/**
 * 12. Search by Date Pattern
 */
async function testDatePatternSearch() {
    const params = {
        pattern: '2024',
        limit: 5
    };
    
    try {
        const response = await api.get('/api/posts/search/by-date-pattern', { params });
        logResponse('DATE PATTERN SEARCH', response);
        return response.data;
    } catch (error) {
        return handleError('DATE PATTERN SEARCH', error);
    }
}

/**
 * 13. Delete Post (requires post ID)
 */
async function testDeletePost(postId) {
    if (!postId || CONFIG.testMode) {
        console.log('\n⚠️  Skipping DELETE POST - Test mode enabled or no post ID');
        return { success: false, error: 'Test mode enabled or no post ID' };
    }
    
    try {
        const response = await api.delete(`/api/posts/${postId}`);
        logResponse('DELETE POST', response);
        return response.data;
    } catch (error) {
        return handleError('DELETE POST', error);
    }
}

// ============================================================================
// COMPREHENSIVE TEST RUNNER
// ============================================================================

/**
 * Run all API endpoint tests in sequence
 */
async function runAllTests() {
    console.log('🚀 GHOST BLOG SMART API - NODE.JS COMPREHENSIVE TESTING');
    console.log('=' .repeat(80));
    console.log(`Base URL: ${CONFIG.baseUrl}`);
    console.log(`Test Mode: ${CONFIG.testMode ? '✅ Enabled' : '❌ Disabled'}`);
    console.log(`Standard Timeout: ${CONFIG.standardTimeout}ms`);
    console.log(`Image Generation Timeout: ${CONFIG.imageTimeout}ms`);
    console.log('📝 Image generation endpoints use extended timeout for reliability');
    console.log('=' .repeat(80));

    const results = {};
    let postId = null;
    let postIds = [];

    // Test sequence with dependencies
    const tests = [
        { name: 'Health Check', fn: testHealthCheck },
        { name: 'API Info', fn: testApiInfo },
        { name: 'Create Post', fn: testCreatePost },
        { name: 'Smart Create', fn: testSmartCreate },
        { name: 'Get Posts', fn: testGetPosts },
        { name: 'Advanced Search', fn: testAdvancedSearch },
        { name: 'Posts Summary', fn: testPostsSummary },
        { name: 'Date Pattern Search', fn: testDatePatternSearch },
    ];

    // Run initial tests
    for (const test of tests) {
        console.log(`\n🧪 Running: ${test.name}`);
        
        try {
            const result = await test.fn();
            results[test.name] = result;
            
            // Extract post ID for dependent tests
            if (test.name === 'Create Post' && result.success && result.data) {
                postId = result.data.post_id;
                console.log(`📝 Extracted Post ID: ${postId}`);
            }
            
            // Clean up large response objects
            results[test.name] = cleanupResponse(result);
            
            // Extract post IDs from get posts for batch operations
            if (test.name === 'Get Posts' && result.success && result.data && result.data.posts) {
                postIds = result.data.posts.slice(0, 3).map(p => p.id);
                console.log(`📝 Extracted Post IDs for batch: ${postIds.join(', ')}`);
            }
            
        } catch (error) {
            results[test.name] = { success: false, error: error.message };
        }
        
        // Small delay between requests
        await sleep(CONFIG.rateLimitDelay);
    }

    // Run tests that depend on post ID
    if (postId) {
        const dependentTests = [
            { name: 'Get Post Details', fn: () => testGetPostDetails(postId) },
            { name: 'Update Post', fn: () => testUpdatePost(postId) },
            { name: 'Update Post Image', fn: () => testUpdatePostImage(postId) },
        ];
        
        for (const test of dependentTests) {
            console.log(`\n🧪 Running: ${test.name}`);
            
            try {
                const result = await test.fn();
                results[test.name] = result;
            } catch (error) {
                results[test.name] = { success: false, error: error.message };
            }
            
            await sleep(CONFIG.rateLimitDelay);
        }
    }

    // Run batch tests
    if (postIds.length > 0) {
        console.log(`\n🧪 Running: Batch Get Details`);
        
        try {
            const result = await testBatchGetDetails(postIds);
            results['Batch Get Details'] = result;
        } catch (error) {
            results['Batch Get Details'] = { success: false, error: error.message };
        }
        
        await sleep(CONFIG.rateLimitDelay);
    }

    // Final cleanup (only in non-test mode)
    if (postId && !CONFIG.testMode) {
        console.log(`\n🧪 Running: Delete Post (Cleanup)`);
        
        try {
            const result = await testDeletePost(postId);
            results['Delete Post'] = result;
        } catch (error) {
            results['Delete Post'] = { success: false, error: error.message };
        }
    }

    // Generate final report
    generateTestReport(results);
    
    return results;
}

/**
 * Generate a comprehensive test report
 */
function generateTestReport(results) {
    console.log('\n📊 COMPREHENSIVE TEST REPORT');
    console.log('=' .repeat(80));
    
    let passed = 0;
    let failed = 0;
    let skipped = 0;
    
    for (const [testName, result] of Object.entries(results)) {
        if (!result || result.error === 'No post ID provided' || result.error === 'Test mode enabled or no post ID') {
            console.log(`⏭️  ${testName}: SKIPPED`);
            skipped++;
        } else if (result.success) {
            console.log(`✅ ${testName}: PASSED`);
            passed++;
        } else {
            console.log(`❌ ${testName}: FAILED - ${result.error || 'Unknown error'}`);
            failed++;
        }
    }
    
    console.log('=' .repeat(80));
    console.log(`📈 SUMMARY: ${passed} passed, ${failed} failed, ${skipped} skipped`);
    console.log(`📊 SUCCESS RATE: ${Math.round((passed / (passed + failed)) * 100)}%`);
    
    if (failed === 0) {
        console.log('\n🎉 ALL TESTS PASSED! Ghost Blog Smart API is working perfectly!');
        console.log('✨ Ready for production deployment and usage!');
    } else {
        console.log(`\n⚠️  ${failed} test(s) failed. Check the logs above for details.`);
        console.log('🔧 Review configuration and API connectivity.');
    }
    
    console.log('\n💡 NEXT STEPS:');
    console.log('1. Review any failed tests and fix issues');
    console.log('2. Test with real credentials (set testMode: false)');
    console.log('3. Deploy Docker container for production use');
    console.log('4. Integrate with your Node.js application');
    
    return { passed, failed, skipped };
}

// ============================================================================
// MAIN EXECUTION
// ============================================================================

/**
 * Main execution function
 */
async function main() {
    try {
        // Add command line argument support
        const args = process.argv.slice(2);
        
        // Validate command line arguments
        if (!validateCliArgs(args)) {
            process.exit(1);
        }
        
        // Validate configuration
        if (!validateConfig()) {
            process.exit(1);
        }
        
        if (args.includes('--help') || args.includes('-h')) {
            console.log(`
🚀 Ghost Blog Smart API - Node.js Test Client

Usage:
  node example_usage_API.js [options] [test-name]

Options:
  --help, -h          Show this help message
  --production        Run in production mode (actual posting)
  --baseurl <url>     Override base URL (default: http://localhost:5000)
  --timeout <ms>      Override timeout (default: 30000)

Individual Tests:
  health              Test health check endpoint
  info                Test API info endpoint
  create              Test create post endpoint
  smart               Test smart create endpoint
  get                 Test get posts endpoint
  search              Test advanced search endpoint
  summary             Test posts summary endpoint
  date                Test date pattern search endpoint

Examples:
  node example_usage_API.js                    # Run all tests
  node example_usage_API.js health             # Run only health check
  node example_usage_API.js --production       # Run in production mode
  node example_usage_API.js --baseurl http://api.example.com:8080

Configuration:
  Update the CONFIG object at the top of this file with your credentials.
            `);
            return;
        }
        
        // Override config based on command line arguments
        if (args.includes('--production')) {
            CONFIG.testMode = false;
            console.log('🔥 Running in PRODUCTION mode - posts will be created!');
        }
        
        const baseurlIndex = args.indexOf('--baseurl');
        if (baseurlIndex !== -1 && args[baseurlIndex + 1]) {
            CONFIG.baseUrl = args[baseurlIndex + 1];
            api.defaults.baseURL = CONFIG.baseUrl;
            console.log(`🔗 Using custom base URL: ${CONFIG.baseUrl}`);
        }
        
        const timeoutIndex = args.indexOf('--timeout');
        if (timeoutIndex !== -1 && args[timeoutIndex + 1]) {
            CONFIG.timeout = parseInt(args[timeoutIndex + 1]);
            api.defaults.timeout = CONFIG.timeout;
            console.log(`⏱️  Using custom timeout: ${CONFIG.timeout}ms`);
        }
        
        // Run individual test if specified
        const testMap = {
            health: testHealthCheck,
            info: testApiInfo,
            create: testCreatePost,
            smart: testSmartCreate,
            get: testGetPosts,
            search: testAdvancedSearch,
            summary: testPostsSummary,
            date: testDatePatternSearch
        };
        
        const individualTest = args.find(arg => testMap[arg]);
        if (individualTest) {
            console.log(`🧪 Running individual test: ${individualTest}`);
            const result = await testMap[individualTest]();
            console.log(`\n${result.success ? '✅ SUCCESS' : '❌ FAILURE'}`);
            return;
        }
        
        // Run comprehensive test suite
        await runAllTests();
        
    } catch (error) {
        console.error('\n💥 CRITICAL ERROR:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Run if this file is executed directly
if (require.main === module) {
    main().catch(error => {
        console.error('💥 Unhandled error:', error);
        process.exit(1);
    });
}

// Export for use as a module
module.exports = {
    CONFIG,
    api,
    testHealthCheck,
    testApiInfo,
    testCreatePost,
    testSmartCreate,
    testGetPosts,
    testAdvancedSearch,
    testGetPostDetails,
    testUpdatePost,
    testUpdatePostImage,
    testPostsSummary,
    testBatchGetDetails,
    testDatePatternSearch,
    testDeletePost,
    runAllTests,
    generateTestReport
};