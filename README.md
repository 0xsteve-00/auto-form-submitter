# 🚀 Auto Form Submitter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

> Automatically fill and submit web forms at scale — perfect for testnet registrations, waitlists, and airdrop campaigns.

## 🎯 What Is This?

Auto Form Submitter is a tool that automates form submissions on websites. Instead of manually filling out forms one by one, this tool handles everything automatically:

- **Testnet Registration** — Bulk register 50+ wallets for testnet programs
- **Waitlist & Whitelist** — Auto-submit to waitlists with wallet addresses and social handles
- **Batch Operations** — Process hundreds of submissions in one run

## 🤔 Who Needs This?

- **Airdrop farmers** who need to register multiple wallets
- **Community managers** running batch registrations
- **Testnet participants** joining early access programs
- **Anyone** tired of filling out the same form repeatedly

## ⚡ Features

- 🌐 Multi-chain wallet support (EVM, Solana)
- 📝 Smart form field detection
- 🔄 Auto-retry on failure
- 📊 Progress tracking with real-time logs
- 🛡️ Proxy support for rate limit bypass
- 💾 Resume from last checkpoint
- 📦 Batch mode with configurable delays

## 📦 Installation

```bash
git clone https://github.com/0xsteve-00/auto-form-submitter.git
cd auto-form-submitter
pip install -r requirements.txt
```

## 🚀 Quick Start

```bash
# Single form submission
python submitter.py --form https://example.com/form --data config.json

# Batch mode with wallet list
python submitter.py --form https://example.com/form --wallets wallets.txt --batch
```

## 📄 Config Format

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "wallet": "0x1234...abcd",
  "twitter": "@johndoe"
}
```

## 📁 Project Structure

```
auto-form-submitter/
├── submitter.py        # Main submission engine
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
└── README.md           # This file
```

## ⚠️ Disclaimer

This tool is for educational purposes and legitimate use only. Users are responsible for complying with all applicable terms of service and laws.

## 📜 License

MIT License — free to use, modify, and distribute.
