import json
import os
from itertools import chain
from pathlib import Path

import click
import requests
from security import safe_requests


SONAR_CLOUD_API_URL = "https://sonarcloud.io/api"


def get_issues_page(project: str, token: str | None, url: str, page_size: int, page: int) -> requests.Response:
    url = f"{url}/issues/search"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    params = {"projects": project, "statuses": "OPEN", "ps": page_size, "p": page}
    response = safe_requests.get(url, headers=headers, params=params)
    return response


def write_issues_to_file(response: str, project: str, dest_dir: Path, page: int):
    filename = dest_dir / f"sonar_issues_{project}_{page}.json"
    filename.write_text(response)


def get_issues(project: str, result_file: Path | None, token: str | None, url: str, page_size: int):
    pages = []

    result_file = result_file or Path(f"sonar_issues_{project}.json")

    response = get_issues_page(project, token, url, page_size, 1)
    pages.append(body := response.json())

    total = body["total"]
    count = body["paging"]["pageSize"]

    while count < total:
        # Page indices are 1-based
        page = count // page_size + 1
        response = get_issues_page(project, token, url, page_size, page)
        pages.append(body := response.json())
        count += body["paging"]["pageSize"]

    # Combine issues from all pages into a single list
    issues = list(chain.from_iterable(page["issues"] for page in pages))
    print(f"Retrieved {len(issues)} issues from {len(pages)} pages")

    return issues

def get_hotspots_page(project: str, token: str | None, url: str, page_size: int, page: int) -> requests.Response:
    url = f"{url}/hotspots/search"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    params = {"projectKey": project, "ps": page_size, "p": page}
    response = safe_requests.get(url, headers=headers, params=params)
    return response

def get_hotspots(project: str, result_file: Path | None, token: str | None, url: str, page_size: int):
    pages = []

    result_file = result_file or Path(f"sonar_hotspots_{project}.json")

    response = get_hotspots_page(project, token, url, page_size, 1)
    pages.append(body := response.json())

    total = body["paging"]["total"]
    count = len(body["hotspots"])

    while count < total:
        # Page indices are 1-based
        page = count // page_size + 1
        response = get_hotspots_page(project, token, url, page_size, page)
        pages.append(body := response.json())
        count += len(body["hotspots"])

    # Combine hotspots from all pages into a single list
    hotspots = list(chain.from_iterable(page["hotspots"] for page in pages))
    print(f"Retrieved {len(hotspots)} hotspots from {len(pages)} pages")

    return hotspots

@click.command()
@click.argument("project", type=str, required=True)
@click.argument("result-file", type=Path, required=False, default=None)
@click.option("--issues-only", is_flag=True, help="Get Sonar issues")
@click.option("--hotspots-only", is_flag=True, help="Get Sonar hotspots")
@click.option("--url", type=str, default=SONAR_CLOUD_API_URL, help="Sonar URL")
@click.option("--page-size", type=int, default=500, help="Sonar results page size")
def main(project: str, result_file: Path, issues_only: bool, hotspots_only: bool, url: str, page_size: int):
    if issues_only and hotspots_only:
        raise click.UsageError("Cannot use both --issues-only and --hotspots-only")

    token = os.getenv("SONAR_TOKEN")

    result = {}

    if not hotspots_only:
        result["issues"] = get_issues(project, result_file, token, url, page_size)
    if not issues_only:
        result["hotspots"] = get_hotspots(project, result_file, token, url, page_size)

    if result_file:
        output_file = result_file
    elif hotspots_only:
        output_file = Path(f"sonar_hotspots_{project}.json")
    elif issues_only:
        output_file = Path(f"sonar_issues_{project}.json")
    else:
        output_file = Path(f"sonar_combined_{project}.json")

    # Write results to the file
    output_file.write_text(json.dumps(result, indent=2))
    print(f"Results written to {output_file}")
