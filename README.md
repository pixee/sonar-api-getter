# sonar-api-getter
Utility for retrieving and combining paginated results from the Sonar APIs

## Overview

The Sonar API Getter is a utility for retrieving and combining paginated results from the Sonar APIs. Specifically, it is intended to retrieve Issues and Hotspots.

These APIs both have a limit of 500 results per page. This utility will retrieve all pages of results (up to the API max of 10000 results total) and combine them into a single JSON file that can be uploaded to Pixee for triage and remediation.

## Requirements

This utility requires Python 3.10 or later.

## Installation

From GitHub repository over SSH (recommended):
```
pip install git+ssh://git@github.com/pixee/sonar-api-getter
```

From GitHub repository over HTTPS:
```
pip install git+https://github.com/pixee/sonar-api-getter
```

## Usage

Once installed, run the following command for a full list of options:
```
sonar-api-getter --help
```

It is necessary to specify either `--issues` or `--hotspots` to retrieve the desired results. The following example retrieves all issues for a project named `my-project`:
```
sonar-api-getter --issues MyOrg_MyRepo
```

To retrieve hotspots, use the following command:
```
sonar-api-getter --hotspots MyOrg_MyRepo
```

By default files are saved to a file in the current working directory. An additional argument can be provided to specify the output file:
```
sonar-api-getter --issues MyOrg_MyRepo my-project-issues.json
```

## Project ID

In order to retrieve issues or hotspots, the project ID must be provided. This can be found in the Sonar UI by navigating to the project and looking at the URL. The project ID is the last part of the URL, after the organization name and a colon. For example, in the URL `https://sonarcloud.io/dashboard?id=MyOrg_MyRepo`, the project ID is `MyOrg_MyRepo`. It can also be found by navigating to the `Information` tab of the project in the Sonar UI and finding the value under `Project Key`.

## Authentication

Authentication with the Sonar API is provided via the `SONAR_TOKEN` environment variable. Tokens can be generated in the Sonar UI under `My Account > Security`, which is reached from the drop-down menu in the upper right-hand side of the UI. In SonarCloud, this can be found [here](https://sonarcloud.io/account/security/).

To run the utility, set the `SONAR_TOKEN` environment variable with the token generated from the Sonar UI:
```
export SONAR_TOKEN=<your-sonar-token>
```
