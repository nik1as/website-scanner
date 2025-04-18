# Website scanner

A fast and powerful web enumeration tool for CTFs.

## Modules

- basic information (title, generator, redirects)
- crawler (directories, forms, emails, comments)
- robots.txt
- git
- favicon fingerprint
- interesting headers
- directory enumeration
- subdomain enumeration
- technology identification
- scan for vulnerabilities
  - Command Injection
  - SQL-Injection (error-based)
  - XSS
  - SSTI
  - File Inclusion

## Installation

### Run in a Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

python3 -m website_scanner.main -u "http://10.x.x.x/"
```

### Install Globally with pipx

```
pipx install .

website-scanner --url "http://10.x.x.x/"
```

## Usage

```
website-scanner --url "http://10.x.x.x/" --vulns --output report.json
```

```
usage: website-scanner [-h] [-v] -u URL [-o OUTPUT] [-c COOKIE] [-a USER_AGENT] [-H [HEADERS ...]] [-t TIMEOUT] [-r RETRIES] [-l RATE_LIMIT] [-d DEPTH] [-i [IGNORE ...]] [--proxy PROXY] [--auth AUTH] [--vulnerabilities] [--confidence-threshold CONFIDENCE_THRESHOLD] [--lfi-depth LFI_DEPTH] [--wordpress-user-ids WORDPRESS_USER_IDS [WORDPRESS_USER_IDS ...]]

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
  -d, --depth DEPTH                                                 Maximum crawler depth
  -i, --ignore [IGNORE ...]                                         Directories to ignore e.g. /logout
  --proxy PROXY                                                     Proxy server
  --auth AUTH                                                       Basic Authentication <username>:<password>
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
