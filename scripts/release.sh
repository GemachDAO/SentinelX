#!/bin/bash
# SentinelX Release and Distribution Script
# Builds packages, runs tests, and prepares for PyPI distribution

set -e  # Exit on any error

echo "🚀 SentinelX Release Pipeline Starting..."

# Configuration
VERSION=$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")
PACKAGE_NAME="sentinelx"
DIST_DIR="dist"
DOCS_DIR="docs"

echo "📦 Building SentinelX v${VERSION}..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Install build dependencies
echo "🔧 Installing build dependencies..."
pip install build twine pytest pytest-cov black flake8 mypy

# Code quality checks
echo "🔍 Running code quality checks..."

echo "  ├── Black formatting check..."
black --check --diff sentinelx/ || {
    echo "❌ Code formatting issues found. Run 'black sentinelx/' to fix."
    exit 1
}

echo "  ├── Flake8 linting..."
flake8 sentinelx/ --max-line-length=88 --extend-ignore=E203,W503 || {
    echo "❌ Linting issues found. Please fix before releasing."
    exit 1
}

echo "  └── MyPy type checking..."
mypy sentinelx/ --ignore-missing-imports || {
    echo "⚠️  Type checking issues found (continuing anyway)"
}

# Run tests
echo "🧪 Running test suite..."
python -m pytest tests/ -v --cov=sentinelx --cov-report=html --cov-report=term-missing || {
    echo "❌ Tests failed. Please fix before releasing."
    exit 1
}

# Build documentation (if available)
if [ -d "$DOCS_DIR" ]; then
    echo "📚 Building documentation..."
    cd docs/
    make html || echo "⚠️  Documentation build failed (continuing anyway)"
    cd ..
fi

# Build package
echo "🏗️  Building Python package..."
python -m build

# Verify build
echo "🔍 Verifying package build..."
twine check dist/*

# Package information
echo "📋 Package Information:"
echo "  ├── Name: ${PACKAGE_NAME}"
echo "  ├── Version: ${VERSION}"
echo "  ├── Files:"
ls -la dist/
echo "  └── Package size: $(du -sh dist/ | cut -f1)"

# Docker build (if Dockerfile exists)
if [ -f "Dockerfile" ]; then
    echo "🐳 Building Docker images..."
    
    echo "  ├── Building main image..."
    docker build -t sentinelx:${VERSION} -t sentinelx:latest .
    
    echo "  ├── Building sandbox image..."
    docker build -f Dockerfile.sandbox -t sentinelx:${VERSION}-sandbox -t sentinelx:sandbox .
    
    echo "  └── Docker images built successfully!"
    docker images | grep sentinelx
fi

# Generate release notes
echo "📝 Generating release notes..."
cat > RELEASE_NOTES.md << EOF
# SentinelX v${VERSION} Release Notes

## 🎉 What's New

### Phase 4: Advanced Features & Production Polish
- ✅ **Advanced Reporting Engine**: Professional reports in HTML, PDF, JSON, Markdown
- ✅ **Docker Support**: Containerized execution and sandboxing
- ✅ **Performance Optimization**: Profiling, benchmarking, and optimization tools
- ✅ **PyPI Distribution**: Production-ready packaging and distribution

### Core Features
- 🛡️  **20 Security Tasks**: Complete coverage across audit, exploit, forensics, red team, AI, and blockchain
- 🔄 **Workflow Orchestration**: Chain tasks with dependency resolution and error handling
- 🐳 **Docker Integration**: Sandboxed execution environment
- 📊 **Advanced Reporting**: Multi-format report generation with charts and analysis
- ⚡ **Performance Tools**: Built-in profiling and optimization capabilities

## 📦 Installation

\`\`\`bash
# From PyPI (recommended)
pip install sentinelx

# From source
git clone https://github.com/sentinelx/sentinelx
cd sentinelx
pip install -e .

# Docker
docker pull sentinelx:${VERSION}
\`\`\`

## 🚀 Quick Start

\`\`\`bash
# List all available tasks
sentinelx list

# Run a security audit
sentinelx run slither --target ./contracts

# Execute a workflow
sentinelx workflow run ./workflows/comprehensive_audit.yaml

# Generate performance report
sentinelx benchmark --tasks slither,mythril --iterations 10
\`\`\`

## 🔧 Docker Usage

\`\`\`bash
# Run in Docker
docker run -v \$(pwd):/workspace sentinelx:${VERSION} list

# Use Docker Compose
docker-compose up sentinelx
\`\`\`

## 📈 Performance Improvements
- Optimized task execution pipeline
- Memory usage optimization
- Concurrent task execution
- Performance profiling and benchmarking tools

## 🛠️ Breaking Changes
None - this is a production-stable release with full backward compatibility.

## 🐛 Bug Fixes
- Improved error handling across all modules
- Enhanced logging and debugging capabilities
- Fixed edge cases in workflow execution

## 📚 Documentation
- Comprehensive API documentation
- Updated usage examples
- Docker deployment guide
- Performance optimization guide

---
Generated on $(date)
EOF

echo "✅ Release preparation complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Review RELEASE_NOTES.md"
echo "  2. Test the built packages: pip install dist/sentinelx-${VERSION}-py3-none-any.whl"
echo "  3. Upload to PyPI: twine upload dist/*"
echo "  4. Push Docker images: docker push sentinelx:${VERSION}"
echo "  5. Create GitHub release with RELEASE_NOTES.md"
echo ""
echo "🎉 SentinelX v${VERSION} is ready for release!"
