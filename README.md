# Website scanner

A fast and powerful web enumeration tool for CTFs.

## Modules

- information
  - basic: title, generator, redirects
  - cookies: secure and httponly flag
  - crawler: directories, forms, emails, comments
  - directories: directory enumeration
  - favicon: favicon fingerprinting
  - git: check for git repo
  - headers: interesting http headers
  - methods: allowed http methods
  - not_found_page: 404 page fingerprinting
  - robots: parse robots.txt
  - subdomains: subdomain enumeration
  - technology: technology identification
  - tls: show certificate information
- vulnerabilities
  - command_injection: Command Injection
  - lfi: Local File Inclusion
  - sqli: error-based SQL injection
  - ssti: Server-side template injection
  - xss: Cross Site Scripting
- technologies
  - wordpress
  - joomla

## Installation

### Install Globally with pipx

```
pipx install git+https://github.com/nik1as/website-scanner.git
  
website-scanner --url "http://10.x.x.x/"
```

### Run in a Virtual Environment

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

python3 -m website_scanner.main -u "http://10.x.x.x/"
```

## Usage

```
website-scanner --url "http://10.x.x.x/" --vulns --output report.json
```

```
usage: website-scanner [-h] [-v] -u URL [-o OUTPUT] [-c COOKIE] [-a USER_AGENT] [-H [HEADERS ...]] [-t TIMEOUT] [-r RETRIES] [-l RATE_LIMIT] [-d DEPTH] [-i [IGNORE ...]] [--proxy PROXY] [--auth AUTH] [--recursive] [--extensions [EXTENSIONS ...]] [--vulnerabilities] [--confidence-threshold CONFIDENCE_THRESHOLD] [--lfi-depth LFI_DEPTH] [--wordpress-user-ids WORDPRESS_USER_IDS [WORDPRESS_USER_IDS ...]]

Scan a website

options:
  -h, --help                                                        show this help message and exit
  -v, --version                                                     show program's version number and exit
  -u, --url URL                                                     URL to scan
  -o, --output OUTPUT                                               Output json file
  -c, --cookie COOKIE                                               Cookie
  -a, --user-agent USER_AGENT                                       User Agent
  -H, --headers [HEADERS ...]                                       HTTP Headers
  -t, --timeout TIMEOUT                                             Timeout
  -r, --retries RETRIES                                             Number of retries
  -l, --rate-limit RATE_LIMIT                                       Limits the number of HTTP requests per second
  -d, --depth DEPTH                                                 Maximum crawler and directory enumeration depth
  -i, --ignore [IGNORE ...]                                         Directories to ignore e.g. /logout
  --proxy PROXY                                                     Proxy server
  --auth AUTH                                                       Basic Authentication <username>:<password>
  --recursive                                                       Recursive directory enumeration
  --extensions [EXTENSIONS ...]                                     File extensions for directory enumeration
  --vulnerabilities                                                 Scan for vulnerabilities
  --confidence-threshold CONFIDENCE_THRESHOLD                       Threshold for the technology identification (0-100)
  --lfi-depth LFI_DEPTH                                             Maximum LFI depth
  --wordpress-user-ids WORDPRESS_USER_IDS [WORDPRESS_USER_IDS ...]  Wordpress user IDs
```

## Credit

- [webappanalyzer](https://github.com/enthec/webappanalyzer)
- [OWASP Favicon Database](https://owasp.org/www-community/favicons_database)
- [Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404)

## Legal Disclaimer

This tool is intended solely for educational and legal security testing purposes within controlled environments such as Capture The Flag (CTF) competitions or explicitly authorized engagements.

Developers and people involved in this project assume no liability and are not responsible for any misuse or damage caused by this program.
