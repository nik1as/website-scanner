import argparse
import asyncio
import itertools
import json

import aiohttp
from aiohttp import BasicAuth

from modules import Module
from utils import print_json_tree, group_dicts
from vulns import VulnerabilityModule


def parse_args():
    parser = argparse.ArgumentParser(description="Scan a website",
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=70))
    parser.add_argument("-u", "--url", type=str, required=True, help="URL to scan")
    parser.add_argument("-o", "--output", type=str, required=False, help="Output json file")
    parser.add_argument("-c", "--cookie", type=str, required=False, default="", help="Cookie")
    parser.add_argument("-t", "--timeout", type=int, required=False, default=60, help="Timeout")
    parser.add_argument("-i", "--ignore", type=str, required=False, nargs="*", default=["/logout"], help="Directories to ignore e.g. /logout")
    parser.add_argument("--user-agent", type=str, required=False, default="webscan", help="User Agent")
    parser.add_argument("--depth", type=int, required=False, default=3, help="Maximum crawler depth")
    parser.add_argument("--proxy", type=str, required=False, help="Proxy server")
    parser.add_argument("--auth", type=str, required=False, help="Basic Authentication <username>:<password>")

    parser.add_argument("--vulns", required=False, action="store_true", help="Scan for vulnerabilities")
    parser.add_argument("--confidence-threshold", type=int, required=False, default=80, help="Threshold for the technology identification (0-100)")
    parser.add_argument("--lfi-depth", type=int, required=False, default=5, help="Maximum LFI depth")
    parser.add_argument("--wordpress-user-ids", type=int, nargs="+", required=False, default=list(range(1, 20)), help="Wordpress user IDs")

    return parser.parse_args()


async def main():
    args = parse_args()

    headers = dict()
    if args.cookie:
        headers["cookie"] = args.cookie
    if args.user_agent:
        headers["user-agent"] = args.user_agent

    auth = None
    if args.auth is not None:
        username, password = args.auth.split(":")
        auth = BasicAuth(username, password)

    output = dict()
    async with aiohttp.ClientSession(headers=headers,
                                     timeout=aiohttp.ClientTimeout(args.timeout),
                                     connector=aiohttp.TCPConnector(ssl=False),
                                     auth=auth) as session:
        tasks = [module().start(session, args) for module in Module.modules]
        results = await asyncio.gather(*tasks)

        for name, result in results:
            if result:
                output[name] = result

    if args.vulns:
        async with aiohttp.ClientSession(headers=headers,
                                         timeout=aiohttp.ClientTimeout(args.timeout),
                                         connector=aiohttp.TCPConnector(ssl=False),
                                         auth=auth) as session:
            output["vulnerabilities"] = []

            dirs = output["crawler"]["directories"]
            tasks = [vuln().run(session, args, dirs) for vuln in VulnerabilityModule.modules]
            results = await asyncio.gather(*tasks)
            results = list(itertools.chain(*results))
            results = group_dicts(results, "payload")
            output["vulnerabilities"] = results

    for title, result in sorted(output.items()):
        print("=" * 5 + " " + title.upper() + " " + "=" * 5)
        print_json_tree(result)
        print()

    if args.output is not None:
        with open(args.output, "w") as outfile:
            json.dump(output, outfile, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
