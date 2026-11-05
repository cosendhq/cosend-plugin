"""Builds dist/cosend-chatgpt-<version>.zip, the package uploaded to the OpenAI Platform dashboard.

Run from anywhere: python3 scripts/build-chatgpt-zip.py

It checks the package first and refuses to build when a check fails. The ZIP holds what ChatGPT
reads, at its root: the Agent Plugins manifest (plugin.json), the MCP server (mcp.json), the
skill, the listing assets, the README and the LICENSE. The files are written in a fixed order with
a fixed date, so the same sources always give the same ZIP.
"""

import json
import re
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_URL = 'https://mcp.cosend.app/mcp'
SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
MCP_SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json'
INCLUDE = ['plugin.json', 'mcp.json', 'README.md', 'LICENSE', 'skills', 'assets']
FIXED_DATE = (2026, 11, 6, 0, 0, 0)

problems = []


def check(ok, message):
    print(('ok    ' if ok else 'FAIL  ') + message)
    if not ok:
        problems.append(message)


def png_size(path):
    head = path.read_bytes()[:24]
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', head[16:24])


manifest = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))
listing = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {})

check(manifest.get('$schema') == SCHEMA, 'plugin.json declares the Agent Plugins 1.0.0 schema')
for key in ['name', 'version', 'description']:
    check(isinstance(manifest.get(key), str) and manifest[key] != '', f'plugin.json has {key}')
check(isinstance(manifest.get('author', {}).get('name'), str), 'plugin.json has author.name')
check(re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', manifest.get('name', '')) is not None, 'name is lowercase letters, digits, dots or hyphens')
check(list(manifest.get('extensions', {}).get('com.openai', {})) == ['interface'], 'com.openai holds the listing only: no apps, no hooks')

for key, limit in [('displayName', 30), ('shortDescription', 30), ('longDescription', 4000), ('developerName', 80)]:
    value = listing.get(key, '')
    check(0 < len(value) <= limit, f'interface.{key} is 1 to {limit} characters ({len(value)})')
prompts = listing.get('defaultPrompt', [])
check(len(prompts) <= 3 and all(len(p) <= 128 for p in prompts), 'interface.defaultPrompt has at most 3 prompts of at most 128 characters')
capabilities = listing.get('capabilities', [])
check(len(capabilities) <= 20 and all(len(c) <= 120 for c in capabilities), 'interface.capabilities has at most 20 labels of at most 120 characters')
for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
    check(str(listing.get(key, '')).startswith('https://cosend.app/'), f'interface.{key} is an https page on cosend.app')
check(re.fullmatch(r'#[0-9A-Fa-f]{6}', listing.get('brandColor', '')) is not None, 'interface.brandColor is a #RRGGBB colour')

logo = ROOT / listing.get('logo', 'missing')
size = png_size(logo) if logo.is_file() else None
check(listing.get('logo', '').startswith('./assets/') and size is not None and size[0] == size[1] >= 512, f'interface.logo is a square PNG of at least 512 px under ./assets/ ({size})')
icon = ROOT / listing.get('composerIcon', 'missing')
check(listing.get('composerIcon', '').startswith('./assets/') and icon.is_file(), 'interface.composerIcon is a file under ./assets/')

mcp = json.loads((ROOT / 'mcp.json').read_text(encoding='utf-8'))
check(mcp == {'$schema': MCP_SCHEMA, 'mcpServers': {'cosend': {'type': 'streamable-http', 'url': MCP_URL}}}, 'mcp.json is the one Cosend server, streamable-http, with no headers or secrets')

skill = (ROOT / 'skills' / 'cosend' / 'SKILL.md').read_text(encoding='utf-8')
front = re.match(r'^---\nname: cosend\ndescription: (.+)\n---\n', skill)
check(front is not None and len(front.group(1)) <= 1024, 'skills/cosend/SKILL.md has its name and a description of at most 1,024 characters')

for path in [ROOT / name for name in INCLUDE]:
    files = [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file())
    for file in files:
        if file.suffix in ('.md', '.json', '.yaml'):
            text = file.read_text(encoding='utf-8')
            check('—' not in text, f'{file.relative_to(ROOT)} has no em dash')
            check(not re.search(r'"headers"|Bearer |clientSecret|test_credentials|reviewer_instructions', text), f'{file.relative_to(ROOT)} carries no credential or reviewer field')
check(not (ROOT / 'hooks').exists() and not (ROOT / '.app.json').exists(), 'no hooks and no .app.json')

if problems:
    sys.exit(f'\n{len(problems)} check(s) failed; no ZIP was built.')

out = ROOT / 'dist' / f"cosend-chatgpt-{manifest['version']}.zip"
out.parent.mkdir(exist_ok=True)
entries = []
for name in INCLUDE:
    path = ROOT / name
    entries += [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file())
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in entries:
        info = zipfile.ZipInfo(file.relative_to(ROOT).as_posix(), FIXED_DATE)
        info.external_attr = 0o644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, file.read_bytes())
print(f'\nBuilt {out.relative_to(ROOT)} with {len(entries)} files.')
