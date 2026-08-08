#!/usr/bin/env python

import os
import sys
import yaml
from datetime import datetime, timezone
from scholarly import scholarly


def load_scholar_user_id() -> str:
    """Load the Google Scholar user ID from the configuration file."""
    config_file = "_data/socials.yml"
    if not os.path.exists(config_file):
        print(
            f"Configuration file {config_file} not found. Please ensure the file exists and contains your Google Scholar user ID."
        )
        sys.exit(1)
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        scholar_user_id = config.get("scholar_userid")
        if not scholar_user_id:
            print(
                "No 'scholar_userid' found in the configuration file. Please add 'scholar_userid' to _data/socials.yml."
            )
            sys.exit(1)
        return scholar_user_id
    except yaml.YAMLError as e:
        print(
            f"Error parsing YAML file {config_file}: {e}. Please check the file for correct YAML syntax."
        )
        sys.exit(1)


SCHOLAR_USER_ID: str = load_scholar_user_id()
OUTPUT_FILE: str = "_data/citations.yml"
MINIMUM_EXISTING_PAPER_RATIO: float = 0.8


def load_existing_data() -> dict:
    """Load the last known-good citation data, if available."""
    if not os.path.exists(OUTPUT_FILE):
        return {}

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError("top-level YAML value is not a mapping")
        return data
    except Exception as e:
        print(f"Error reading existing citation data from {OUTPUT_FILE}: {e}")
        sys.exit(1)


def validate_publications(new_papers: dict, existing_papers: dict) -> None:
    """Reject empty or suspiciously incomplete Scholar responses."""
    if not new_papers:
        print("Google Scholar returned no usable publications; keeping existing data.")
        sys.exit(1)

    existing_count = len(existing_papers)
    minimum_count = int(existing_count * MINIMUM_EXISTING_PAPER_RATIO)
    if existing_count and len(new_papers) < minimum_count:
        print(
            "Google Scholar returned a suspiciously incomplete publication list "
            f"({len(new_papers)} fetched, {existing_count} stored, minimum accepted "
            f"{minimum_count}); keeping existing data."
        )
        sys.exit(1)


def get_scholar_citations() -> None:
    """Fetch and update Google Scholar citation data."""
    print(f"Fetching citations for Google Scholar ID: {SCHOLAR_USER_ID}")
    checked_at = datetime.now(timezone.utc)
    today = checked_at.strftime("%Y-%m-%d")
    existing_data = load_existing_data()
    existing_papers = existing_data.get("papers", {})
    if not isinstance(existing_papers, dict):
        print(f"Existing citation data in {OUTPUT_FILE} has an invalid papers mapping.")
        sys.exit(1)

    citation_data = {"metadata": {}, "papers": {}}

    scholarly.set_timeout(15)
    scholarly.set_retries(3)
    try:
        author = scholarly.search_author_id(SCHOLAR_USER_ID)
        author_data = scholarly.fill(author)
    except Exception as e:
        print(
            f"Error fetching author data from Google Scholar for user ID '{SCHOLAR_USER_ID}': {e}. Please check your internet connection and Scholar user ID."
        )
        sys.exit(1)

    if not author_data:
        print(
            f"Could not fetch author data for user ID '{SCHOLAR_USER_ID}'. Please verify the Scholar user ID and try again."
        )
        sys.exit(1)

    if not author_data.get("publications"):
        print(f"No publications found in author data for user ID '{SCHOLAR_USER_ID}'.")
        sys.exit(1)

    for pub in author_data["publications"]:
        try:
            pub_id = pub.get("pub_id") or pub.get("author_pub_id")
            if not pub_id:
                print(
                    f"Warning: No ID found for publication: {pub.get('bib', {}).get('title', 'Unknown')}. This publication will be skipped."
                )
                continue

            title = pub.get("bib", {}).get("title", "Unknown Title")
            year = pub.get("bib", {}).get("pub_year", "Unknown Year")
            citations = pub.get("num_citations", 0)

            print(f"Found: {title} ({year}) - Citations: {citations}")

            citation_data["papers"][pub_id] = {
                "title": title,
                "year": year,
                "citations": citations,
            }
        except Exception as e:
            print(
                f"Error processing publication '{pub.get('bib', {}).get('title', 'Unknown')}': {e}. This publication will be skipped."
            )

    validate_publications(citation_data["papers"], existing_papers)

    papers_changed = existing_papers != citation_data["papers"]
    previous_metadata = existing_data.get("metadata", {})
    if not isinstance(previous_metadata, dict):
        previous_metadata = {}

    citation_data["metadata"] = {
        "last_checked": checked_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_updated": today
        if papers_changed
        else previous_metadata.get("last_updated", today),
    }

    if papers_changed:
        print("Citation counts or publications changed.")
    else:
        print("Citation counts are unchanged; recording the successful check time.")

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            yaml.dump(citation_data, f, width=1000, sort_keys=True)
        print(f"Citation data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(
            f"Error writing citation data to {OUTPUT_FILE}: {e}. Please check file permissions and disk space."
        )
        sys.exit(1)


if __name__ == "__main__":
    try:
        get_scholar_citations()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
