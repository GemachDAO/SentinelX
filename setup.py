from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sentinelx",
    version="0.2.0",
    author="SentinelX Team",
    description="Modular Python framework for offensive and defensive security operations across Web2 and Web3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "PyYAML>=6.0.0",
        "aiohttp>=3.8.0",
        "requests>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
        "graphviz>=0.20.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
    ],
    extras_require={
        "security": [
            "slither-analyzer>=0.10.0",
            "mythril>=0.24.0", 
            "pwntools>=4.14.0",
        ],
        "advanced": [
            "angr>=9.2.0",
            "scapy>=2.5.0",
        ],
        "all": [
            "slither-analyzer>=0.10.0",
            "mythril>=0.24.0",
            "pwntools>=4.14.0",
            "angr>=9.2.0", 
            "scapy>=2.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sentinelx=sentinelx.cli:main",
        ],
        "sentinelx.tasks": [
            "slither=sentinelx.audit.smart_contract:SlitherScan",
            "mythril=sentinelx.audit.smart_contract:MythrilScan",
            "cvss=sentinelx.audit.cvss:CVSSCalculator",
            "web2-static=sentinelx.audit.web2_static:Web2Static",
            "fuzzer=sentinelx.exploit.fuzzing:Fuzzer",
            "shellcode=sentinelx.exploit.shellcode:ShellcodeGen",
            "autopwn=sentinelx.exploit.exploit_gen:AutoPwn",
            "chain-monitor=sentinelx.blockchain.monitor:ChainMonitor",
            "tx-replay=sentinelx.blockchain.replay:TxReplay",
            "rwa-scan=sentinelx.blockchain.rwascan:RwaScan",
            "llm-assist=sentinelx.ai.llm_assist:LLMAssist",
            "prompt-injection=sentinelx.ai.adversarial:PromptInjection",
            "c2=sentinelx.redteam.c2:C2Server",
            "lateral-move=sentinelx.redteam.lateral_move:LateralMove",
            "social-eng=sentinelx.redteam.social_eng:SocialEngineering",
            "memory-forensics=sentinelx.forensic.memory:MemoryForensics",
            "disk-forensics=sentinelx.forensic.disk:DiskForensics",
            "chain-ir=sentinelx.forensic.chain_ir:ChainIR",
        ],
    },
    keywords="security, pentesting, blockchain, web3, static-analysis, fuzzing, exploit-development",
    project_urls={
        "Bug Reports": "https://github.com/sentinelx/sentinelx/issues",
        "Source": "https://github.com/sentinelx/sentinelx",
    },
)
