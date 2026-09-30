#!/usr/bin/env python3

import os
import requests
from collections import defaultdict
from pathlib import Path


USERNAME = "JanESchneider"
OUTPUT = Path("profile/top-langs.svg")
LANGS_COUNT = 10

# Hide D because my .d files are in fact Daedalus, NOT D.
HIDDEN_LANGUAGES = {"D"}

# Jupyter Notebook basically is just Python
MERGE_LANGUAGES = {"Jupyter Notebook": "Python"}

token = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


# ------------------------------------------------------------
# Get repositories
# ------------------------------------------------------------

repos = []

page = 1

while True:

    response = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        headers=headers,
        params={
            "per_page": 100,
            "page": page,
            "type": "owner",
        },
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        break

    repos.extend(data)

    page += 1


# ------------------------------------------------------------
# Collect language statistics
# ------------------------------------------------------------

languages = defaultdict(int)

for repo in repos:

    if repo["fork"]:
        continue

    url = repo["languages_url"]

    response = requests.get(
        url,
        headers=headers,
    )

    response.raise_for_status()

    repo_languages = response.json()

    for language, bytes_count in repo_languages.items():

        if language in HIDDEN_LANGUAGES:
            continue

        language = MERGE_LANGUAGES.get(
            language,
            language,
        )

        languages[language] += bytes_count


# ------------------------------------------------------------
# Sort and limit
# ------------------------------------------------------------

languages = sorted(
    languages.items(),
    key=lambda item: item[1],
    reverse=True,
)

languages = languages[:LANGS_COUNT]

total = sum(value for _, value in languages)


# ------------------------------------------------------------
# SVG
# ------------------------------------------------------------

width = 500
row_height = 35
height = 60 + len(languages) * row_height

rows = []

y = 55

for language, value in languages:

    percentage = value / total * 100

    rows.append(
        f"""
        <text
            x="20"
            y="{y}"
            fill="#c9d1d9"
            font-size="14"
            font-family="Arial, sans-serif"
        >
            {language}
        </text>

        <text
            x="480"
            y="{y}"
            fill="#c9d1d9"
            font-size="14"
            text-anchor="end"
            font-family="Arial, sans-serif"
        >
            {percentage:.1f}%
        </text>

        <rect
            x="20"
            y="{y + 8}"
            width="460"
            height="6"
            rx="3"
            fill="#21262d"
        />

        <rect
            x="20"
            y="{y + 8}"
            width="{460 * percentage / 100:.1f}"
            height="6"
            rx="3"
            fill="#58a6ff"
        />
        """
    )

    y += row_height


svg = f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
>

    <rect
        width="100%"
        height="100%"
        rx="6"
        fill="#0d1117"
    />

    <text
        x="20"
        y="28"
        fill="#58a6ff"
        font-size="18"
        font-weight="600"
        font-family="Arial, sans-serif"
    >
        Most Used Languages
    </text>

    {''.join(rows)}

</svg>
"""


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT.write_text(
    svg,
    encoding="utf-8",
)

print(f"Written {OUTPUT}")

print()

for language, value in languages:

    percentage = value / total * 100

    print(
        f"{language:20s} "
        f"{percentage:6.2f}%"
    )