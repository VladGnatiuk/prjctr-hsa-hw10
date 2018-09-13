#!/bin/bash

# Configuration
HOST="host.docker.internal:8000"
REQUESTS=1000
CONCURRENCY=10
RESULTS_DIR="/results"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Starting load tests..."

# Test /health/elastic endpoint
echo -e "${GREEN}Testing /health/elastic endpoint${NC}"
ab -n $REQUESTS -c $CONCURRENCY "http://$HOST/health/elastic" > "$RESULTS_DIR/elastic_results.txt"
echo "Results saved to elastic_results.txt"
echo

# Test /health/mongo endpoint
echo -e "${GREEN}Testing /health/mongo endpoint${NC}"
ab -n $REQUESTS -c $CONCURRENCY "http://$HOST/health/mongo" > "$RESULTS_DIR/mongo_results.txt"
echo "Results saved to mongo_results.txt"
echo

# Test /constant endpoint
echo -e "${GREEN}Testing /constant endpoint${NC}"
ab -n $REQUESTS -c $CONCURRENCY "http://$HOST/constant" > "$RESULTS_DIR/constant_results.txt"
echo "Results saved to constant_results.txt"
echo

echo "Load testing completed. Check the results directory for detailed results."
 