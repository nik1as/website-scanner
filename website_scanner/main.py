#!/usr/bin/env python

import argparse
import asyncio
import itertools
import json

from aiohttp import BasicAuth, TCPConnector, ClientTimeout

from website_scanner import __version__
from website_scanner.http_client import HTTPClient, ExponentialRetry
from website_scanner.info import InformationModule
from website_scanner.techs import TechnologyModule
from website_scanner.utils import print_json_tree, group_dicts
from website_scanner.vulns import VulnerabilityModule


def parse_args():
    parser = argparse.ArgumentParser(description="Scan a website",
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=70))
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-u", "--url", type=str, required=True, help="URL to scan")
    parser.add_argument("-o", "--output", type=str, required=False, help="Output json file")
    parser.add_argument("-c", "--cookie", type=str, required=False, default="", help="Cookie")
    parser.add_argument("-a", "--user-agent", type=str, required=False, default=f"website-scanner/{__version__}", help="User Agent")
    parser.add_argument("-H", "--headers", type=str, required=False, nargs="*", default=[], help="HTTP Headers")
    parser.add_argument("-t", "--timeout", type=int, required=False, default=60, help="Timeout")
    parser.add_argument("-r", "--retries", type=int, required=False, default=3, help="Number of retries")
    parser.add_argument("-l", "--rate-limit", type=int, required=False, help="Limits the number of HTTP requests per second")
    parser.add_argument("-d", "--depth", type=int, required=False, default=3, help="Maximum crawler and directory enumeration depth")
    parser.add_argument("-i", "--ignore", type=str, required=False, nargs="*", default=["/logout"], help="Directories to ignore e.g. /logout")
    parser.add_argument("--proxy", type=str, required=False, help="HTTP Proxy")
    parser.add_argument("--auth", type=str, required=False, help="Basic Authentication <username>:<password>")
    parser.add_argument('--fill', default=True, action=argparse.BooleanOptionalAction, help="Fill empty values")
    parser.add_argument("--recursive", required=False, default=False, action="store_true", help="Recursive directory enumeration")
    parser.add_argument("--extensions", type=str, required=False, nargs="*", default=[], help="File extensions for directory enumeration")
    parser.add_argument("--vulnerabilities", required=False, action="store_true", help="Scan for vulnerabilities")
    parser.add_argument("--confidence-threshold", type=int, required=False, default=80, help="Threshold for the technology identification (0-100)")
    parser.add_argument("--lfi-depth", type=int, required=False, default=5, help="Maximum LFI depth")
    parser.add_argument("--wordpress-user-ids", type=int, nargs="+", required=False, default=list(range(1, 20)), help="Wordpress user IDs")

    return parser.parse_args()


def print_module_result(name: str, result):
    print("=" * 5 + " " + name.upper() + " " + "=" * 5)
    print_json_tree(result)
    print()


async def website_scanner():
    args = parse_args()

    headers = dict()
    if args.cookie:
        headers["cookie"] = args.cookie
    if args.user_agent:
        headers["user-agent"] = args.user_agent
    for header in args.headers:
        if ":" not in header:
            continue
        name, value = map(str.strip, header.split(":", 1))
        headers[name.lower()] = value

    auth = None
    if args.auth is not None:
        username, password = args.auth.split(":")
        auth = BasicAuth(username, password)

    output = dict()
    async with HTTPClient(retry_options=ExponentialRetry(attempts=args.retries),
                          rate_limit=args.rate_limit,
                          headers=headers,
                          timeout=ClientTimeout(args.timeout),
                          connector=TCPConnector(ssl=False),
                          auth=auth) as session:
        tasks = [module().start(session, args) for module in InformationModule.modules]
        for coro in asyncio.as_completed(tasks):
            name, result = await coro
            if result:
                output[name] = result
                print_module_result(name, result)

        if "technology" in output:
            technology_modules = [tech() for tech in TechnologyModule.modules]
            techs = {tech.lower() for category in output["technology"] for tech in output["technology"][category]}
            tasks = []
            for tech_module in technology_modules:
                if tech_module.name in techs:
                    tasks.append(tech_module.start(session, args))
            for coro in asyncio.as_completed(tasks):
                name, result = await coro
                if result:
                    output[name] = result
                    print_module_result(name, result)

        if args.vulnerabilities:
            output["vulnerabilities"] = []
            directories = output["crawler"]["directories"]
            tasks = [vuln().run(session, args, directories) for vuln in VulnerabilityModule.modules]
            results = list(itertools.chain(*(await asyncio.gather(*tasks))))
            results = group_dicts(results, "payload")
            output["vulnerabilities"] = results
            print_module_result("vulnerabilities", results)

    if args.output is not None:
        with open(args.output, "w") as outfile:
            json.dump(output, outfile, indent=2)


def main():
    asyncio.run(website_scanner())


if __name__ == "__main__":
    main()
