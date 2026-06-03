# 🚀 Auto Form Submitter

Automate web form submissions for testnets, waitlists, and registrations using Playwright.

## 🎯 Apa Ini?

**Auto Form Submitter** adalah tool untuk mengisi dan mengirim form web secara otomatis. Sangat berguna untuk:

- **Airdrop Hunter** — daftar testnet dalam jumlah besar (50-100 wallet sekaligus)
- **Waitlist Join** — auto-join waitlist project crypto
- **Batch Registration** — register banyak akun sekaligus
- **Daily Check-in** — auto check-in harian di platform testnet
- **Form Testing** — test form web untuk bug/validasi

**Masalah yang diselesaikan:**
Manual daftar testnet dengan 50 wallet = 2-3 jam. Dengan tool ini = 10 menit.

## Features

- ✅ Auto-fill and submit web forms
- ✅ Multi-wallet batch support (EVM + Solana)
- ✅ Stealth mode (anti-bot detection bypass)
- ✅ Proxy support (HTTP/SOCKS5)
- ✅ Custom field mapping via YAML config
- ✅ Human-like typing delays
- ✅ Akamai/Cloudflare challenge handling
- ✅ Success/failure logging
- ✅ CSV/JSON wallet import

## Installation

```bash
git clone https://github.com/0xsteve-00/auto-form-submitter.git
cd auto-form-submitter
pip install -r requirements.txt
playwright install chromium
```

## Quick Start

```bash
# Single submission
python submit.py --config config.yaml

# Batch with wallets
python submit.py --config config.yaml --wallets wallets.csv --batch 10

# With proxy
python submit.py --config config.yaml --proxy socks5://127.0.0.1:1080
```

## Config Example (config.yaml)

```yaml
url: "https://example.com/waitlist"
fields:
  - selector: "input[name='email']"
    value: "{email}"
  - selector: "input[name='name']"
    value: "{name}"
  - selector: "select[name='country']"
    value: "United States"
    type: "select"
checkboxes:
  - "input[type='checkbox']"
submit: "button[type='submit']"
wait_for: 10  # seconds after submit
success_check: "thank"  # keyword in body text
```

## Wallets CSV

```csv
email,name,wallet_address
alice@gmail.com,Alice,0x1234...
bob@gmail.com,Bob,0x5678...
```

## Use Cases

- 🎯 Testnet registrations (airdrops, waitlists)
- 📝 Batch form submissions
- 🔄 Daily check-in automation
- 🏗️ Multi-account setups

## Tech Stack

- Python 3.10+
- Playwright (Chromium)
- PyYAML
- CSV/JSON support

## Disclaimer

For educational purposes only. Use responsibly and respect ToS of target platforms.

## License

MIT
