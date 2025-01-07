import json
import os
from itertools import chain
from pathlib import Path

import click
import requests


SONAR_CLOUD_API_URL = "https://sonarcloud.io/api"


def get_issues_page(project: str, token: str | None, url: str, page_size: int, page: int) -> requests.Response:
    url = f"{url}/issues/search"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    params = {"projects": project, "statuses": "OPEN", "ps": page_size, "p": page}
    response = requests.get(url, headers=headers, params=params)
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
        page = count // page_size
        response = get_issues_page(project, token, url, page_size, page)
        pages.append(body := response.json())
        count += body["paging"]["pageSize"]

    # Combine issues from all pages into a single list
    issues = list(chain.from_iterable(page["issues"] for page in pages))

    output = dict(issues=issues)
    result_file.write_text(json.dumps(output, indent=2))

@click.command()
@click.argument("project", type=str, required=True)
@click.argument("result-file", type=Path, required=False, default=None)
@click.option("--url", type=str, default=SONAR_CLOUD_API_URL, help="Sonar URL")
@click.option("--page-size", type=int, default=500, help="Sonar results page size")
def main(project: str, result_file: Path, url: str, page_size: int):
    token = os.getenv("SONAR_TOKEN")
    get_issues(project, result_file, token, url, page_size)
