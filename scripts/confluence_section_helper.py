#!/usr/bin/env python3
"""
Section-aware Confluence page editor.
Allows updating specific sections without touching others.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import List, Optional, Tuple


class ConfluenceSectionHelper:
    def __init__(self):
        # Try environment variables first
        self.url = os.environ.get("CONFLUENCE_URL")
        self.username = os.environ.get("CONFLUENCE_USERNAME")
        self.token = os.environ.get("CONFLUENCE_API_TOKEN")

        # Fallback to keychain if not in env
        if not self.token:
            self.token = self._get_from_keychain(
                "confluence_api_token", os.environ.get("USER", "")
            )
        if not self.username:
            self.username = self._get_from_keychain(
                "confluence_username", os.environ.get("USER", "")
            )
        if not self.url:
            self.url = "https://metal-scribe.atlassian.net/wiki"

        if not all([self.url, self.username, self.token]):
            raise ValueError(
                "Missing required credentials (check environment or keychain)"
            )

        self.auth_str = f"{self.username}:{self.token}"

    def _get_from_keychain(self, service: str, account: str) -> str:
        """Get credential from macOS keychain."""
        try:
            cmd = [
                "security",
                "find-generic-password",
                "-a",
                account,
                "-s",
                service,
                "-w",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""

    def _curl_get(self, endpoint: str) -> dict:
        """Execute GET request via curl."""
        cmd = ["curl", "-s", "-u", self.auth_str, f"{self.url}{endpoint}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Curl GET failed: {result.stderr}")
        return json.loads(result.stdout)

    def _curl_put(self, endpoint: str, data: dict) -> dict:
        """Execute PUT request via curl."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_file = f.name

        cmd = [
            "curl",
            "-s",
            "-X",
            "PUT",
            "-H",
            "Content-Type: application/json",
            "-u",
            self.auth_str,
            "-d",
            f"@{temp_file}",
            f"{self.url}{endpoint}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        os.unlink(temp_file)

        if result.returncode != 0:
            raise RuntimeError(f"Curl PUT failed: {result.stderr}")
        return json.loads(result.stdout)

    def get_sections(self, page_id: str) -> List[Tuple[str, str, int, int]]:
        """
        Parse page into sections.
        Returns: [(section_title, content, start_pos, end_pos), ...]
        """
        data = self._curl_get(f"/rest/api/content/{page_id}?expand=body.storage")
        content = data["body"]["storage"]["value"]

        # Find all h1 and h2 headings
        heading_pattern = r"(<h[12][^>]*>.*?</h[12]>)"
        headings = list(re.finditer(heading_pattern, content))

        sections = []
        for i, match in enumerate(headings):
            heading_html = match.group(1)
            # Extract text from heading (remove HTML tags)
            title = re.sub(r"<[^>]+>", "", heading_html)

            start = match.end()
            end = headings[i + 1].start() if i + 1 < len(headings) else len(content)

            section_content = content[start:end]
            sections.append((title, section_content, match.start(), end))

        return sections

    def list_sections(self, page_id: str) -> None:
        """List all sections in a page with numbers."""
        sections = self.get_sections(page_id)
        print(f"\nFound {len(sections)} sections:\n")
        for i, (title, content, _, _) in enumerate(sections, 1):
            # Clean up title
            title = title.strip().replace("\n", " ")
            content_preview = content.strip()[:80].replace("\n", " ")
            print(f"{i}. {title}")
            print(f"   Preview: {content_preview}...")
            print()

    def update_section(
        self, page_id: str, page_title: str, section_number: int, new_content: str
    ) -> dict:
        """
        Update a specific section by number (1-based).
        Only this section is modified, others remain unchanged.
        """
        # Get page data
        data = self._curl_get(
            f"/rest/api/content/{page_id}?expand=body.storage,version"
        )
        version = data["version"]["number"]
        content = data["body"]["storage"]["value"]

        # Parse sections
        sections = self.get_sections(page_id)
        if section_number < 1 or section_number > len(sections):
            raise ValueError(
                f"Invalid section number. Page has {len(sections)} sections."
            )

        # Get the section to update (0-based index)
        section_idx = section_number - 1
        title, old_content, start, end = sections[section_idx]

        # Replace only this section's content
        # Keep the heading, replace the content after it
        heading_end = sections[section_idx][2]
        for i, (t, c, s, e) in enumerate(sections):
            if i == section_idx:
                heading_end = s + len(
                    re.search(r"<h[12][^>]*>.*?</h[12]>", content[s:]).group(0)
                )
                break

        new_full_content = content[:heading_end] + new_content + content[end:]

        # Update page
        update_data = {
            "version": {"number": version + 1},
            "type": "page",
            "title": page_title,
            "body": {
                "storage": {"value": new_full_content, "representation": "storage"}
            },
        }

        result = self._curl_put(f"/rest/api/content/{page_id}", update_data)
        print(f"✅ Updated section {section_number}: '{title}'")
        print(f"   Version: {version} → {version + 1}")
        return result

    def update_section_by_title(
        self, page_id: str, page_title: str, section_title: str, new_content: str
    ) -> dict:
        """
        Update a section by its title (fuzzy match).
        More intuitive than section numbers.
        """
        sections = self.get_sections(page_id)

        # Find matching section
        section_idx = None
        for i, (title, _, _, _) in enumerate(sections):
            if section_title.lower() in title.lower():
                section_idx = i + 1  # Convert to 1-based
                break

        if section_idx is None:
            available = [t for t, _, _, _ in sections]
            raise ValueError(
                f"Section '{section_title}' not found. Available: {available}"
            )

        return self.update_section(page_id, page_title, section_idx, new_content)

    def append_to_section(
        self, page_id: str, page_title: str, section_number: int, content_to_append: str
    ) -> dict:
        """Append content to end of a section without replacing it."""
        sections = self.get_sections(page_id)
        if section_number < 1 or section_number > len(sections):
            raise ValueError(
                f"Invalid section number. Page has {len(sections)} sections."
            )

        section_idx = section_number - 1
        _, old_content, _, _ = sections[section_idx]

        new_content = old_content + content_to_append
        return self.update_section(page_id, page_title, section_number, new_content)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  List sections:  confluence_section_helper.py list <page_id>")
        print(
            "  Update section: confluence_section_helper.py update <page_id> <page_title> <section_num> <new_content>"
        )
        print(
            "  Update by title: confluence_section_helper.py update-title <page_id> <page_title> <section_title> <new_content>"
        )
        sys.exit(1)

    command = sys.argv[1]
    helper = ConfluenceSectionHelper()

    if command == "list":
        page_id = sys.argv[2]
        helper.list_sections(page_id)

    elif command == "update":
        page_id = sys.argv[2]
        page_title = sys.argv[3]
        section_num = int(sys.argv[4])
        new_content = sys.argv[5]
        helper.update_section(page_id, page_title, section_num, new_content)

    elif command == "update-title":
        page_id = sys.argv[2]
        page_title = sys.argv[3]
        section_title = sys.argv[4]
        new_content = sys.argv[5]
        helper.update_section_by_title(page_id, page_title, section_title, new_content)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
