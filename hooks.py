import re


def on_page_markdown(markdown, page, config, files):
    """Convert Obsidian ![[path]] embed syntax to standard Markdown ![alt](path)."""
    return re.sub(
        r"!\[\[(.+?\.(?:png|jpg|jpeg|gif|svg|webp))(?:\|\d+)?\]\]",
        lambda m: f"![{m.group(1).rsplit('/', 1)[-1]}]({m.group(1)})",
        markdown,
    )
