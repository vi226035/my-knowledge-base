import re
import os


def _extract_description(markdown, max_length=160):
    """Extract the first meaningful paragraph from markdown content as meta description."""
    # Remove YAML frontmatter if still present
    text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", markdown, flags=re.DOTALL)

    # Split into blocks by blank lines
    blocks = re.split(r"\n\s*\n", text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Skip headings
        if block.startswith("#"):
            continue
        # Skip horizontal rules
        if re.match(r"^[-*_]{3,}\s*$", block):
            continue
        # Skip image-only blocks
        if re.match(r"^!\[.*?\]\(.*?\)\s*$", block):
            continue
        # Skip HTML comments
        if block.startswith("<!--"):
            continue
        # Handle blockquotes — strip > prefix and use inner text
        if block.startswith(">"):
            inner = re.sub(r"^>\s*", "", block, flags=re.MULTILINE).strip()
            if inner and not inner.startswith("["):
                block = inner
            else:
                continue

        # Strip inline markdown formatting
        clean = block
        clean = re.sub(r"!\[.*?\]\(.*?\)", "", clean)  # images
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)  # links → keep text
        clean = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", clean)  # bold/italic *
        clean = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", clean)  # bold/italic _
        clean = re.sub(r"`[^`]+`", "", clean)  # inline code
        clean = re.sub(r"\$\$.*?\$\$", "", clean, flags=re.DOTALL)  # display math
        clean = re.sub(r"\$[^$]+\$", "", clean)  # inline math
        clean = re.sub(r"<[^>]+>", "", clean)  # HTML tags
        clean = re.sub(r"\s+", " ", clean).strip()

        # Skip if too short
        if len(clean) < 10:
            continue

        # Replace ASCII double quotes with proper Chinese quotes to avoid
        # breaking HTML meta attribute delimiters
        clean = clean.replace('"', '“').replace('"', '”')

        # Truncate to max_length characters
        if len(clean) > max_length:
            clean = clean[: max_length - 1] + "…"

        return clean

    return None


def on_page_markdown(markdown, page, config, files):
    """Convert Obsidian ![[embed]] and [[wikilink]] syntax to standard Markdown."""

    # Current page directory relative to docs root
    page_dir = os.path.dirname(page.file.src_path) if page.file.src_path else ""

    def make_relative(target, is_image=False):
        """Compute relative path from current page to target."""
        # Targets that are already relative to the current note should not be
        # re-relativized, otherwise ../kb_material/... becomes ../../kb_material/...
        if target.startswith(("../", "./")):
            return target
        if not page_dir:
            return target
        return os.path.relpath(target, page_dir).replace("\\", "/")

    # 1. Convert image embeds: ![[path.png]] -> ![alt](relative_path)
    def convert_image(m):
        target = m.group(1)
        return f"![{target.rsplit('/', 1)[-1]}]({make_relative(target, True)})"

    markdown = re.sub(
        r"!\[\[(.+?\.(?:png|jpg|jpeg|gif|svg|webp))(?:\|\d+)?\]\]",
        convert_image,
        markdown,
    )

    # 2. Convert wiki-links: [[target|alias]] -> [alias](relative_path.md)
    def convert_wikilink(m):
        target = m.group(1).strip()
        alias = m.group(2) or target.rsplit("/", 1)[-1]
        if target.startswith(("http://", "https://")):
            return f"[{alias}]({target})"
        # Only add .md if target doesn't already have an extension
        if "." not in target.rsplit("/", 1)[-1]:
            target += ".md"
        return f"[{alias}]({make_relative(target)})"

    markdown = re.sub(
        r"(?<!!)\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]",
        convert_wikilink,
        markdown,
    )

    # 3. Auto-generate per-page description from first paragraph
    if not page.meta.get("description"):
        desc = _extract_description(markdown)
        if desc:
            page.meta["description"] = desc

    return markdown
