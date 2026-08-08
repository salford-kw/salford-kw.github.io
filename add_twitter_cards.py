import re, glob

files = [f for f in glob.glob('**/*.html', recursive=True)]
updated = []
skipped = []

for path in files:
    with open(path, encoding='utf-8') as f:
        html = f.read()

    if 'twitter:card' in html:
        continue

    m_title = re.search(r'<meta property="og:title" content="(.*?)">', html)
    m_desc = re.search(r'<meta property="og:description" content="(.*?)">', html)
    m_image = re.search(r'<meta property="og:image" content="(.*?)">', html)
    m_sitename_line = re.search(r'<meta property="og:site_name" content="[^"]*">\n', html)

    if not (m_title and m_desc and m_image and m_sitename_line):
        skipped.append(path)
        continue

    title = m_title.group(1)
    desc = m_desc.group(1)
    image = m_image.group(1)

    twitter_block = (
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{title}">\n'
        f'<meta name="twitter:description" content="{desc}">\n'
        f'<meta name="twitter:image" content="{image}">\n'
    )

    insert_pos = m_sitename_line.end()
    new_html = html[:insert_pos] + twitter_block + html[insert_pos:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    updated.append(path)

print(f"Updated: {len(updated)} files")
print(f"Skipped (missing og fields): {len(skipped)} files")
for s in skipped:
    print("  SKIPPED:", s)
