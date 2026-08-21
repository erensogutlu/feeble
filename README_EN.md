# FEEBLE -- Web Vulnerability Scanner

```
  _____ _____ _____ ____  _     _____
 |  ___| ____| ____| __ )| |   | ____|
 | |_  |  _| |  _| |  _ \| |   |  _|  
 |  _| | |___| |___| |_) | |___| |___ 
 |_|   |_____|_____|____/|_____|_____|
```

A modular web security scanner written in Python. Detects common web application vulnerabilities including SQL Injection, XSS, LFI, Open Redirect, CSRF, missing security headers, BOLA/IDOR, and custom YAML templates. Compatible with Kali Linux and Windows.

[Türkçe README (Turkish Documentation)](README.md)

---

## Features

| Feature | Description |
|---|---|
| **SQL Injection** | Error-based, Boolean-based, and Time-based blind SQLi detection |
| **XSS** | Reflected and DOM-based Cross-Site Scripting detection |
| **LFI** | Local File Inclusion and Path Traversal detection |
| **Open Redirect** | Unvalidated redirect vulnerability detection |
| **CSRF** | CSRF token missing and active validation testing |
| **Security Headers** | Missing or misconfigured HTTP security headers & CORS checks |
| **BOLA / IDOR** | Broken Object Level Authorization testing with dual-session tokens |
| **WAF Evasion** | Adaptive WAF mutation and character fuzzing engine |
| **JS Crawler** | Headless JavaScript & SPA crawler for single page applications |
| **OOB Engine** | Out-of-band interaction client for blind vulnerability detection |
| **YAML Engine** | Nuclei-style YAML vulnerability template runner |
| **Crawler** | Automated page, link, and form discovery engine |
| **Reporting** | Sleek HTML, JSON, and terminal console reporting |
| **Parallel Scanning** | Multithreaded execution using ThreadPoolExecutor |
| **Proxy Support** | Seamless integration with Burp Suite / OWASP ZAP |

---

## Installation

### Kali Linux / Linux (Recommended)

```bash
git clone https://github.com/erensogutlu/feeble.git
cd feeble
pip3 install -r requirements.txt
```

### Windows

```bash
pip install -r requirements.txt
```

### Development Mode (Optional)

```bash
pip install -e .
```

### Python Version Compatibility

| Python Version | Status |
|---|---|
| Python 3.8 | Supported |
| Python 3.9 | Supported |
| Python 3.10 | Supported |
| Python 3.11 | Supported |
| Python 3.12+ | Supported |

---

## Usage -- Step-by-Step Guide

There are **2 fundamental concepts** to know before running Feeble:

1. **Target URL** - The web application URL you wish to scan (e.g., `https://example.com`)
2. **Scan Mode** - Whether you want a full scan with all modules or targeted module execution.

---

### 1. Listing Available Modules

To display all available security scanning modules:

```bash
python ana.py -u https://example.com --modul-listesi
```

**Example output:**
```
[*] Available modules:
  sql             -- SQL Injection (Error/Boolean/Time-based)
  xss             -- Cross-Site Scripting (Reflected/Stored)
  lfi             -- Local File Inclusion / Path Traversal
  yonlendirme     -- Open Redirect
  csrf            -- CSRF Token Missing / Validation
  baslik          -- HTTP Security Headers & CORS
  bola            -- BOLA / IDOR Authorization Testing
```

---

### 2. Full Scan (All Modules)

Scans the target URL using **all available modules**. First runs the web crawler to discover forms and URLs, then tests each target point against all security checks.

```bash
python ana.py -u https://example.com --tam-tarama
```

**Command parameters breakdown:**

| Parameter | Value | Description |
|---|---|---|
| `-u` | `https://example.com` | Target website URL |
| `--tam-tarama` | (flag) | Execute all modules |

---

### 3. Scanning with Specific Modules

Run only selected modules to speed up scanning or target specific vulnerability types:

```bash
python ana.py -u https://example.com -m sql,xss
```

**Examples:**
```bash
# SQL Injection only
python ana.py -u https://example.com -m sql

# Security headers check only
python ana.py -u https://example.com -m baslik

# LFI and Open Redirect
python ana.py -u https://example.com -m lfi,yonlendirme

# BOLA / IDOR test with dual session cookies
python ana.py -u https://example.com -m bola --cerez "session=userA" --cerez-b "session=userB"
```

---

### 4. Advanced Engine Flags (WAF, JS, YAML)

```bash
# Enable adaptive WAF mutation engine
python ana.py -u https://example.com --tam-tarama --waf-bypass

# Enable Headless JavaScript & SPA crawler
python ana.py -u https://example.com --tam-tarama --js-surungan

# Run custom YAML vulnerability templates
python ana.py -u https://example.com --sablonlar sablonlar/

# Add inter-request delay (seconds)
python ana.py -u https://example.com --tam-tarama --gecikme 0.5
```

---

### 5. Report Generation (JSON & HTML)

Save scan findings into machine-readable JSON or visual HTML reports:

**a) JSON Report:**
```bash
python ana.py -u https://example.com --tam-tarama -c json -d report.json
```

**b) HTML Report (Dark Theme Visual Dashboard):**
```bash
python ana.py -u https://example.com --tam-tarama -c html -d report.html
```

---

### 6. Proxy Integration (Burp Suite / OWASP ZAP)

Route all HTTP/HTTPS scanner traffic through an interception proxy:

```bash
python ana.py -u https://example.com --tam-tarama --proxy http://127.0.0.1:8080
```

---

### 7. Authenticated Scanning (Cookies)

Supply session cookies to scan authenticated areas behind login forms:

```bash
python ana.py -u https://example.com --tam-tarama --cerez "PHPSESSID=abc123; token=xyz789"
```

---

## All CLI Parameters (Reference Table)

| Parameter | Short | Required | Description |
|---|---|---|---|
| `--url` | `-u` | Yes | Target URL to scan |
| `--tam-tarama` | -- | No | Full scan with all modules |
| `--moduller` | `-m` | No | Comma-separated module list (`sql,xss,lfi`) |
| `--cikti` | `-c` | No | Output format: `konsol`, `json`, `html` |
| `--dosya` | `-d` | No | Output file path |
| `--derinlik` | -- | No | Max crawler depth (default: 3) |
| `--maks-sayfa` | -- | No | Max crawler pages (default: 100) |
| `--surungan-yok` | -- | No | Disable web crawler |
| `--proxy` | -- | No | Interception proxy URL (`http://127.0.0.1:8080`) |
| `--cerez` | -- | No | Primary session cookies (`PHPSESSID=123`) |
| `--thread` | `-t` | No | Number of parallel threads (default: 5) |
| `--gecikme` | -- | No | Delay between requests in seconds |
| `--cerez-b` | -- | No | Secondary user session cookie (for BOLA/IDOR test) |
| `--waf-bypass` | -- | No | Enable adaptive WAF mutation engine |
| `--js-surungan` | -- | No | Enable Headless JS & SPA crawler layer |
| `--sablonlar` | -- | No | YAML vulnerability template file or directory |
| `--modul-listesi` | -- | No | List available modules and exit |
| `--help` | `-h` | No | Show help message and exit |

---

## Project Structure

```
feeble/
├── ana.py                     <- CLI Entry point
├── tarayici.py                <- Main scanner engine
├── surungan.py                <- Web crawler
├── surungan_js.py             <- Headless JS & SPA crawler
├── waf_mutasyon.py            <- WAF mutation engine
├── oob_dinleyici.py           <- Out-Of-Band callback manager
├── sablon_motoru.py           <- YAML template parser & engine
├── istek.py                   <- HTTP request helpers
├── rapor.py                   <- Report generator (HTML/JSON/Console)
├── yapilandirma.py            <- Configuration constants
├── yardimci.py                <- Utility functions
├── test_feeble.py             <- Unit test suite (149/149 passed)
├── moduller/
│   ├── __init__.py            <- Module registry
│   ├── temel_modul.py         <- Abstract base module
│   ├── sql_enjeksiyon.py      <- SQL Injection scanner
│   ├── xss.py                 <- XSS scanner
│   ├── lfi.py                 <- LFI scanner
│   ├── acik_yonlendirme.py    <- Open Redirect scanner
│   ├── csrf.py                <- CSRF scanner
│   ├── baslik_guvenlik.py     <- Security headers scanner
│   └── bola_idor.py           <- BOLA / IDOR scanner
├── payloadlar/                <- Security payload libraries
├── sablonlar/                 <- YAML vulnerability templates
└── README_EN.md               <- English documentation
```

---

## Frequently Asked Questions (FAQ)

**Q: "ModuleNotFoundError" when running?**  
Install dependencies: `pip install -r requirements.txt`

**Q: Which Python version is required?**  
Python 3.8 or higher. Check with `python --version`.

**Q: Scanning takes too long?**  
Disable crawler with `--surungan-yok` or limit page count `--maks-sayfa 20`. You can also select specific modules like `-m sql`.

**Q: Can it scan HTTPS sites?**  
Yes. SSL verification is disabled for testing flexibility.

**Q: Can I use it with Burp Suite / ZAP?**  
Yes. Pass `--proxy http://127.0.0.1:8080`.

**Q: How do I handle WAF rate-limiting?**  
Use `--gecikme 0.5` or `--waf-bypass` to apply request throttling and payload mutations.

---

## Disclaimer

This tool is designed **strictly for educational purposes and authorized security assessment**.
Scanning target web applications without explicit written authorization is **illegal** and may violate applicable local and international laws. Always ensure you have **written consent** before scanning any system.

---

## License

Educational Use Only.

---

**Developer:** erensogutlu  
**Version:** 1.0.0  
**Platform:** Kali Linux / Windows / Python 3.8+
