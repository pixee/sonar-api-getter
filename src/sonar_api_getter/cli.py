from pathlib import Path

import click
import requests


SONAR_CLOUD_API_URL = "https://sonarcloud.io/api"


def get_issues_page(project: str, token: str, url: str, page_size: int, page: int) -> requests.Response:
    url = f"{url}/issues/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"projects": project, "statuses": "OPEN", "ps": page_size, "p": page}
    response = requests.get(url, headers=headers, params=params)
    return response


def write_issues_to_file(response: str, project: str, dest_dir: Path, page: int):
    filename = dest_dir / f"sonar_issues_{project}_{page}.json"
    filename.write_text(response)


def get_issues(project: str, dest_dir: Path, token: str, url: str, page_size: int):
    response = get_issues_page(project, token, url, page_size, 1)
    write_issues_to_file(response.text, project, dest_dir, 1)

    json = response.json()
    total = json["total"]
    count = json["paging"]["pageSize"]

    while count < total:
        page = count // page_size
        response = get_issues_page(project, token, url, page_size, page)
        write_issues_to_file(response.text, project, dest_dir, page)

        json = response.json()
        count += json["paging"]["pageSize"]

@click.command()
@click.argument("project", type=str, required=True)
@click.argument("dest-dir", type=Path, required=False, default=Path.cwd())
@click.option("-t", "--token", type=str, help="Sonar API token")
@click.option("--url", type=str, default=SONAR_CLOUD_API_URL, help="Sonar URL")
@click.option("--page-size", type=int, default=500, help="Sonar results page size")
def main(project: str, dest_dir: Path, token: str, url: str, page_size: int):
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)

    get_issues(project, dest_dir, token, url, page_size)
