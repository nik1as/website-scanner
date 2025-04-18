import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse

import aiohttp

from website_scanner.info import InformationModule


class TLS(InformationModule):

    def __init__(self):
        super().__init__("tls")

    async def run(self, session: aiohttp.ClientSession, args):
        try:
            parsed = urlparse(args.url)
            hostname = parsed.hostname
            ip = socket.gethostbyname(hostname)
            port = parsed.port or 443

            context = ssl.create_default_context()

            with socket.create_connection((ip, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    result = dict()
                    result["protocol"] = ssock.version()
                    result["cipher"] = ssock.cipher()[0]

                    cert = ssock.getpeercert()
                    not_before = cert.get("notBefore", "")
                    not_after = cert.get("notAfter", "")

                    result["issuer"] = dict()
                    for entry in cert.get("issuer", []):
                        result["issuer"].update(dict(entry))

                    result["subject"] = dict()
                    for entry in cert.get("subject", []):
                        result["subject"].update(dict(entry))

                    try:
                        cert_not_before = datetime.strptime(not_before, "%b %d %H:%M:%S %Y %Z")
                        cert_not_after = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    except ValueError:
                        cert_not_before = cert_not_after = "Invalid date format"

                    result["not-before"] = str(cert_not_before)
                    result["not-after"] = str(cert_not_after)

                    return result
        except:
            pass
