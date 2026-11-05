"""Builds dist/cosend-chatgpt-<version>.zip, the package uploaded to the OpenAI Platform dashboard.

Run from anywhere: python3 scripts/build-chatgpt-zip.py

It checks the package against OpenAI's package guide, submission page and submission error
reference (developers.openai.com/plugins, read 6 Nov 2026) and refuses to build when a check
fails. The ZIP holds what ChatGPT and Codex read, at its root: the Agent Plugins manifest
(plugin.json), the MCP server (mcp.json), the skill, the listing assets, the README and the
LICENSE. Files go in a fixed order with a fixed date, so the same sources give the same ZIP.
"""

import json
import re
import struct
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_URL = 'https://mcp.cosend.app/mcp'
SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
MCP_SCHEMA = 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json'
INCLUDE = ['plugin.json', 'mcp.json', 'README.md', 'LICENSE', 'skills', 'assets']
FIXED_DATE = (2026, 11, 6, 0, 0, 0)
CATEGORIES = {
    'Productivity', 'Creativity', 'Developer Tools', 'Business & Operations', 'Data & Analytics',
    'Communication', 'Education & Research', 'Security', 'Finance', 'Healthcare', 'Travel',
    'Entertainment', 'Other',
}

problems = []


def check(ok, message):
    print(('ok    ' if ok else 'FAIL  ') + message)
    if not ok:
        problems.append(message)


def one_line(text, limit):
    return isinstance(text, str) and text.strip() != '' and '\n' not in text and len(text) <= limit


def luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def png_size(path):
    head = path.read_bytes()[:24]
    return struct.unpack('>II', head[16:24]) if head[:8] == b'\x89PNG\r\n\x1a\n' else None


def https(url):
    return isinstance(url, str) and url.startswith('https://') and '@' not in url and len(url) <= 1024


manifest = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))
openai = manifest.get('extensions', {}).get('com.openai', {})
listing = openai.get('interface', {})
review = openai.get('review', {})

# Package identity (plugin_manifest_* and final submission rules).
check(manifest.get('$schema') == SCHEMA, 'plugin.json declares the Agent Plugins 1.0.0 schema')
check(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', manifest.get('name', '')) is not None, 'name: at most 64 ASCII letters, digits, _ or -')
check(re.fullmatch(r'\d+\.\d+\.\d+', manifest.get('version', '')) is not None, 'version is a semantic version')
check(0 < len(manifest.get('description', '')) <= 1024, 'description is 1 to 1,024 characters')
check(one_line(manifest.get('author', {}).get('name'), 120), 'author.name is set')
check(https(manifest.get('author', {}).get('url')) and https(manifest.get('homepage')), 'author.url and homepage are HTTPS')
check(not {'apps', 'hooks'} & set(openai), 'no apps and no hooks (app_configuration_excluded)')

# Listing metadata, at the final-submission limits.
check(one_line(listing.get('displayName'), 30), 'interface.displayName: one line, at most 30')
check(one_line(listing.get('shortDescription'), 30), 'interface.shortDescription: one line, at most 30')
check(0 < len(listing.get('longDescription', '')) <= 4000, 'interface.longDescription: at most 4,000')
check(one_line(listing.get('developerName'), 80), 'interface.developerName: one line, at most 80')
check(listing.get('category') in CATEGORIES, f"interface.category is a supported category ({listing.get('category')})")
capabilities = listing.get('capabilities', [])
check(len(capabilities) <= 20 and all(one_line(c, 120) for c in capabilities), 'interface.capabilities: at most 20, one line, at most 120 each')
prompts = listing.get('defaultPrompt', [])
normalised = [' '.join(unicodedata.normalize('NFKC', p).split()) for p in prompts]
check(len(prompts) <= 3 and all(one_line(p, 128) and '@' not in p for p in prompts), 'interface.defaultPrompt: at most 3, one line, at most 128, no @mention')
check(len(set(normalised)) == len(normalised), 'interface.defaultPrompt entries are unique')
for key in ['websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL']:
    check(https(listing.get(key)) and listing[key].startswith('https://cosend.app/'), f'interface.{key} is an HTTPS page on cosend.app')
colour = listing.get('brandColor', '')
check(re.fullmatch(r'#[0-9A-Fa-f]{6}', colour) is not None and 1.05 / (luminance(colour) + 0.05) >= 2, 'interface.brandColor is #RRGGBB with at least 2:1 contrast against white')

# Icons (image errors): PNG, square, 48 to 4,096 px, at most 5 MiB, under ./assets/.
for key in ['logo', 'composerIcon']:
    path = listing.get(key, '')
    file = ROOT / path
    size = png_size(file) if file.is_file() else None
    check(path.startswith('./assets/') and file.is_file() and file.stat().st_size <= 5 * 1024 * 1024 and size is not None and size[0] == size[1] and 48 <= size[0] <= 4096, f'interface.{key} is a square PNG of 48 to 4,096 px, at most 5 MiB ({size})')

# Review and publication information (imported with the ZIP).
positive = review.get('test_cases', {}).get('positive', [])
negative = review.get('test_cases', {}).get('negative', [])
check(len(positive) == 5 and len(negative) == 3, 'exactly five positive and three negative test cases')
check(all(c.get('description') and c.get('prompt') and c.get('tools_triggered') and c.get('expected_behavior') for c in positive), 'every positive case has description, prompt, tools_triggered and expected_behavior')
check(all(c.get('description') and c.get('prompt') for c in negative), 'every negative case has description and prompt')
check(isinstance(review.get('commerce'), bool), 'review.commerce is declared')
check(bool(openai.get('publication', {}).get('release_notes')), 'publication.release_notes is set')

# MCP server: one remote HTTPS server with OAuth, no headers.
mcp = json.loads((ROOT / 'mcp.json').read_text(encoding='utf-8'))
servers = mcp.get('mcpServers', {})
server = servers.get('cosend', {})
check(mcp.get('$schema') == MCP_SCHEMA and list(servers) == ['cosend'], 'mcp.json declares exactly one server, cosend, with the Agent Plugins MCP schema')
check(server.get('type') == 'streamable-http' and server.get('url') == MCP_URL and 'headers' not in server, 'the server is streamable-http at https://mcp.cosend.app/mcp, with no headers')
auth = server.get('extensions', {}).get('com.openai', {}).get('auth', {})
check(auth.get('type') == 'oauth' and auth.get('client') == {'mode': 'cimd'}, 'auth is OAuth with CIMD client registration and no client credentials')

# Skills (skill errors) and the skill's agents/openai.yaml interface.
skills = sorted(p for p in (ROOT / 'skills').iterdir() if p.is_dir())
for skill_dir in skills:
    text = (skill_dir / 'SKILL.md').read_text(encoding='utf-8')
    front = re.match(r'^---\nname: (\S+)\ndescription: (.+)\n---\n(.+)', text, re.S)
    check(front is not None and 0 < len(front.group(2)) <= 1024 and front.group(3).strip() != '', f'{skill_dir.name}/SKILL.md has a name, a description of at most 1,024 and instructions')
    check(front is not None and len(f"{manifest['name']}:{front.group(1)}") <= 64, f'{skill_dir.name}: plugin-name:skill-name is at most 64 characters')
    agent = skill_dir / 'agents' / 'openai.yaml'
    if agent.exists():
        yaml_text = agent.read_text(encoding='utf-8')
        check(re.search(r'^interface:\n  display_name: ".+"\n  short_description: ".+"$', yaml_text, re.M) is not None, f'{skill_dir.name}/agents/openai.yaml has interface.display_name and short_description')
        check(re.search(r'^dependencies:\n  tools:', yaml_text, re.M) is not None, f'{skill_dir.name}/agents/openai.yaml dependencies hold tools only')

# Text hygiene in every packaged text file.
entries = []
for name in INCLUDE:
    path = ROOT / name
    entries += [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file())
for file in entries:
    if file.suffix in ('.md', '.json', '.yaml'):
        text = file.read_text(encoding='utf-8')
        rel = file.relative_to(ROOT)
        check('—' not in text, f'{rel} has no em dash')
        check(not re.search(r'clientSecret|test_credentials|reviewer_instructions|Bearer ', text), f'{rel} carries no secret, credential or reviewer field')

if problems:
    sys.exit(f'\n{len(problems)} check(s) failed; no ZIP was built.')

out = ROOT / 'dist' / f"cosend-chatgpt-{manifest['version']}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in entries:
        info = zipfile.ZipInfo(file.relative_to(ROOT).as_posix(), FIXED_DATE)
        info.external_attr = 0o644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, file.read_bytes())
print(f'\nBuilt {out.relative_to(ROOT)} with {len(entries)} files.')
