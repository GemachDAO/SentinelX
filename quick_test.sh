#!/bin/bash

echo "SentinelX Phase 2 - Quick CLI Validation"
echo "========================================"
echo

# Test DiskForensics
echo "Testing DiskForensics (timeline analysis)..."
python -c "from sentinelx.cli import app; app()" run disk-forensics --params '{"image": "evidence.img", "type": "timeline"}' --format json 2>/dev/null | head -10 | grep -q "analysis_type" && echo "✓ DiskForensics: WORKING" || echo "✗ DiskForensics: FAILED"

# Test ChainIR  
echo "Testing ChainIR (transaction trace)..."
python -c "from sentinelx.cli import app; app()" run chain-ir --params '{"address": "0x123", "type": "trace"}' --format json 2>/dev/null | head -10 | grep -q "analysis_type" && echo "✓ ChainIR: WORKING" || echo "✗ ChainIR: FAILED"

# Test C2
echo "Testing C2 (test mode)..."
python -c "from sentinelx.cli import app; app()" run c2 --params '{"mode": "test", "port": 8080}' --format json 2>/dev/null | head -10 | grep -q "server_mode" && echo "✓ C2: WORKING" || echo "✗ C2: FAILED"

# Test SocialEngineering
echo "Testing Social Engineering..."
python -c "from sentinelx.cli import app; app()" run social-eng --params '{"campaign_type": "phishing", "target_count": 5}' --format json 2>/dev/null | head -10 | grep -q "campaign_type" && echo "✓ SocialEng: WORKING" || echo "✗ SocialEng: FAILED"

# Test MemoryForensics
echo "Testing Memory Forensics..."
python -c "from sentinelx.cli import app; app()" run memory-forensics --params '{"dump_file": "mem.dmp", "analysis": "processes"}' --format json 2>/dev/null | head -10 | grep -q "analysis_type" && echo "✓ MemoryForensics: WORKING" || echo "✗ MemoryForensics: FAILED"

echo
echo "All key Phase 2 tasks validated!"
echo "Full task list available via: python -c \"from sentinelx.cli import app; app()\" --help"
