# Website scanner

A fast and powerful website scanner for CTFs.

## Modules

- basic information (title, generator, redirects)
- crawler (directories, forms, emails, comments)
- robots.txt
- favicon fingerprint
- interesting headers
- directory enumeration
- technology identification
- scan for vulnerabilities (SQL-Injection, XSS, SSTI, LFI)

## Usage

```
usage: main.py [-h] -u URL [-o OUTPUT] [-c COOKIE] [-t TIMEOUT] [-i [IGNORE ...]] [--user-agent USER_AGENT] [--depth DEPTH] [--proxy PROXY] [--auth AUTH] [--vulns] [--lfi-depth LFI_DEPTH] [--wordpress-user-ids WORDPRESS_USER_IDS [WORDPRESS_USER_IDS ...]]

Scan a website

options:
  -h, --help                                      show this help message and exit
  -u, --url URL                                   URL to scan
  -o, --output OUTPUT                             Output json file
  -c, --cookie COOKIE                             Cookie
  -t, --timeout TIMEOUT                           Timeout
  -i, --ignore [IGNORE ...]                       Directories to ignore e.g. /logout
  --user-agent USER_AGENT                         User Agent
  --depth DEPTH                                   Maximum crawler depth
  --proxy PROXY                                   Proxy server
  --auth AUTH                                     Basic Authentication <username>:<password>
  --vulns                                         Scan for vulnerabilities
  --lfi-depth LFI_DEPTH                           Maximum lfi depth
  --wordpress-user-ids WORDPRESS_USER_IDS [WORDPRESS_USER_IDS ...]
                                                  Wordpress user IDs
```
