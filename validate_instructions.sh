#!/bin/bash
# Comprehensive validation of copilot-instructions.md commands
echo 'Validating all documented commands...'

# Test 1: Project structure
echo '1. Checking project structure...'
ls -la | grep -E '(LICENSE|README|appinfo.json|resources|src)' || echo 'Missing expected files'

# Test 2: JSON validation
echo '2. Validating appinfo.json...'
cat appinfo.json | python3 -m json.tool > /dev/null && echo 'JSON: VALID' || echo 'JSON: INVALID'

# Test 3: JavaScript syntax
echo '3. Checking JavaScript syntax...'
node -c src/app.js && echo 'JS Syntax: VALID' || echo 'JS Syntax: INVALID'

# Test 4: JSHint (if available)
echo '4. Running JSHint...'
if command -v npx >/dev/null 2>&1; then
    npx jshint src/app.js && echo 'JSHint: PASSED' || echo 'JSHint: Found issues (expected)'
else
    echo 'JSHint: NOT AVAILABLE'
fi

# Test 5: Resource files
echo '5. Checking resources...'
ls -la resources/images/ | grep bus.png && echo 'Required resource: PRESENT' || echo 'Required resource: MISSING'

# Test 6: File exploration
echo '6. Testing file commands...'
find . -name '*.js' -o -name '*.json' | wc -l | xargs echo 'Found files:'

echo 'Validation complete!'