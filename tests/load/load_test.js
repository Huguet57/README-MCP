/**
 * k6 Load Testing Script for README-MCP
 * 
 * This script simulates 500 rps and ensures p95 latency < 200ms
 * 
 * Usage:
 *   k6 run --vus 50 --duration 30s tests/load/load_test.js
 *   k6 run --vus 100 --duration 60s tests/load/load_test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 300 }, // Ramp up to 300 users
    { duration: '5m', target: 300 }, // Stay at 300 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests must complete below 200ms
    http_req_failed: ['rate<0.01'],   // Error rate must be below 1%
    errors: ['rate<0.01'],            // Custom error rate must be below 1%
  },
};

// Base URL for the service
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test data - real public repositories
const TEST_REPOS = [
  {
    repo_url: 'https://github.com/pallets/flask',
    files: ['pyproject.toml', 'LICENSE.txt', 'CHANGES.rst'],
    directories: ['src', 'tests', 'docs'],
  },
  {
    repo_url: 'https://github.com/microsoft/vscode',
    files: ['package.json', 'README.md', 'LICENSE.txt'],
    directories: ['src', 'extensions', 'build'],
  },
  {
    repo_url: 'https://github.com/nodejs/node',
    files: ['package.json', 'README.md', 'LICENSE'],
    directories: ['src', 'test', 'lib'],
  },
];

/**
 * Get a random repository configuration
 */
function getRandomRepo() {
  return TEST_REPOS[Math.floor(Math.random() * TEST_REPOS.length)];
}

/**
 * Get a random file from a repository
 */
function getRandomFile(repo) {
  return repo.files[Math.floor(Math.random() * repo.files.length)];
}

/**
 * Get a random directory from a repository
 */
function getRandomDirectory(repo) {
  return repo.directories[Math.floor(Math.random() * repo.directories.length)];
}

/**
 * Test README endpoint
 */
function testReadmeEndpoint() {
  const repo = getRandomRepo();
  
  const payload = JSON.stringify({
    repo_url: repo.repo_url,
    ref: 'main',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { endpoint: 'readme' },
  };

  const response = http.post(`${BASE_URL}/readme`, payload, params);
  
  const success = check(response, {
    'README status is 200': (r) => r.status === 200,
    'README response has content': (r) => {
      if (r.status === 200) {
        const data = JSON.parse(r.body);
        return data.content && data.content.length > 0;
      }
      return true; // Don't fail check if status isn't 200
    },
    'README response time < 200ms': (r) => r.timings.duration < 200,
  });

  errorRate.add(!success);
  return response;
}

/**
 * Test file endpoint
 */
function testFileEndpoint() {
  const repo = getRandomRepo();
  const file = getRandomFile(repo);
  
  const payload = JSON.stringify({
    repo_url: repo.repo_url,
    path: file,
    ref: 'main',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { endpoint: 'file' },
  };

  const response = http.post(`${BASE_URL}/file`, payload, params);
  
  const success = check(response, {
    'File status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    'File response has content when successful': (r) => {
      if (r.status === 200) {
        const data = JSON.parse(r.body);
        return data.content && data.name === file;
      }
      return true; // Don't fail check if status isn't 200
    },
    'File response time < 200ms': (r) => r.timings.duration < 200,
  });

  errorRate.add(!success);
  return response;
}

/**
 * Test directory listing endpoint
 */
function testDirectoryEndpoint() {
  const repo = getRandomRepo();
  const useSubdir = Math.random() > 0.5;
  const dir = useSubdir ? getRandomDirectory(repo) : '';
  
  const payload = JSON.stringify({
    repo_url: repo.repo_url,
    dir: dir,
    ref: 'main',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { endpoint: 'directory' },
  };

  const response = http.post(`${BASE_URL}/ls`, payload, params);
  
  const success = check(response, {
    'Directory status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    'Directory response has entries when successful': (r) => {
      if (r.status === 200) {
        const data = JSON.parse(r.body);
        return Array.isArray(data.entries) && data.total_count >= 0;
      }
      return true; // Don't fail check if status isn't 200
    },
    'Directory response time < 200ms': (r) => r.timings.duration < 200,
  });

  errorRate.add(!success);
  return response;
}

/**
 * Test health check endpoint
 */
function testHealthEndpoint() {
  const response = http.get(`${BASE_URL}/health`, {
    tags: { endpoint: 'health' },
  });
  
  const success = check(response, {
    'Health status is 200': (r) => r.status === 200,
    'Health response time < 50ms': (r) => r.timings.duration < 50,
  });

  errorRate.add(!success);
  return response;
}

/**
 * Main test function - randomly chooses which endpoint to test
 */
export default function () {
  // Randomly distribute load across endpoints
  const rand = Math.random();
  
  if (rand < 0.4) {
    // 40% README requests
    testReadmeEndpoint();
  } else if (rand < 0.7) {
    // 30% file requests
    testFileEndpoint();
  } else if (rand < 0.95) {
    // 25% directory requests
    testDirectoryEndpoint();
  } else {
    // 5% health check requests
    testHealthEndpoint();
  }

  // Brief pause between requests to simulate realistic usage
  sleep(Math.random() * 0.5 + 0.1); // Random sleep between 0.1-0.6 seconds
}

/**
 * Setup function - runs once before the test starts
 */
export function setup() {
  console.log('Starting load test...');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Test repositories: ${TEST_REPOS.length}`);
  
  // Test that the service is accessible
  const response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    throw new Error(`Service health check failed: ${response.status}`);
  }
  
  console.log('Service is healthy, starting load test');
}

/**
 * Teardown function - runs once after the test completes
 */
export function teardown(data) {
  console.log('Load test completed');
}