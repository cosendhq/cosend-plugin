# Cosend plugin

Cosend is the WhatsApp platform businesses run their customer conversations on: a shared WhatsApp
inbox on the number you already use, with the WhatsApp Business app still working on your phone,
plus WhatsApp campaigns, WhatsApp templates, WhatsApp automation and an AI receptionist. This plugin
brings all of it into your AI assistant over MCP, with one skill that shows the assistant how to
use every Cosend tool well.

## What is in it

- **The Cosend connector**: Cosend's MCP server at `https://mcp.cosend.app/mcp`, over Streamable
  HTTP. You sign in to Cosend when you connect it, pick the workspace and choose the permissions
  the assistant gets.
- **The `cosend` skill**: how to read and answer chats, work the inbox as a team, run WhatsApp
  campaigns, write WhatsApp templates for Meta's review, keep contacts and consent, build, test
  and fix WhatsApp automations, train the AI receptionist, manage numbers and integrations, read
  reports and connect a WhatsApp number.

## What your assistant does with Cosend

- **WhatsApp inbox**: reads, searches and answers every chat, with text, photos, files, buttons,
  lists, products and templates. It assigns and snoozes chats, adds internal notes, saves inbox
  views and passes chats between teammates.
- **WhatsApp campaigns**: picks a saved audience and an approved marketing template, shows who
  gets the campaign and Meta's list price, then sends it or schedules it, and reports delivery,
  reads and replies.
- **WhatsApp templates**: writes templates, checks them against Meta's rules and submits them for
  Meta's review.
- **Contacts**: keeps contacts, tags, custom fields, CSV imports and consent records in order.
- **WhatsApp automation**: builds automations from ready-made recipes or a plain description,
  tests them on a sample customer, deploys them, switches them on and explains every run step by
  step.
- **AI receptionist**: sets its persona, trains it on your website, files and Google Maps listing,
  and tests it before customers meet it.
- **Numbers, integrations and reports**: manages your WhatsApp numbers and business profile,
  connects Google Sheets, Google Calendar, Calendly, Shopify, Stripe and more, and reads reports on
  response times, the AI receptionist and your team.

Every message, campaign and template submission, and every automation deploy and switch-on, comes
to you as a preview you approve. New automations are saved switched off. Connecting a WhatsApp
number, connecting an app and billing happen on a secure set-up link you open in your own browser.
Every tool is listed on [cosend.app/mcp](https://cosend.app/mcp), and how to connect any MCP client
is on [cosend.app/docs/mcp](https://cosend.app/docs/mcp).

## Install

### Claude Code

```bash
claude plugin marketplace add cosendhq/cosend-plugin
claude plugin install cosend@cosend
```

Then run `/mcp` inside Claude Code and sign in to Cosend.

### claude.ai, Claude Desktop and Cowork

1. Download this repository as a zip.
2. In claude.ai, go to **Customize > Plugins > Add > Upload plugin** and select the zip.
3. Open the plugin's **Connectors** tab and connect Cosend. You sign in to Cosend in the browser.

### Codex

```bash
codex plugin marketplace add cosendhq/cosend-plugin
codex plugin add cosend@cosend
```

You sign in to Cosend when it connects.

### ChatGPT desktop app

1. Clone this repository to `~/.codex/plugins/cosend`.
2. Add it to your personal marketplace, `~/.agents/plugins/marketplace.json`:

   ```json
   {
     "name": "cosend-local",
     "plugins": [
       {
         "name": "cosend",
         "source": { "source": "local", "path": "./.codex/plugins/cosend" },
         "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
         "category": "Productivity"
       }
     ]
   }
   ```

3. Restart the ChatGPT desktop app, open the Plugins Directory, choose that marketplace and install
   Cosend. You sign in to Cosend when it connects.

### Gemini CLI

```bash
gemini extensions install https://github.com/cosendhq/cosend-plugin
```

Gemini CLI opens the Cosend sign-in in your browser when the connector first connects.

### Antigravity

```bash
agy plugin install https://github.com/cosendhq/cosend-plugin
```

Antigravity opens the Cosend sign-in in your browser when the connector first connects.

### Grok Build

```bash
grok plugin install cosendhq/cosend-plugin
```

Then open `/mcps` and press `i` on Cosend to sign in.

### Perplexity

1. Select **Plugins** in the sidebar, then **Add custom**.
2. Import this repository from GitHub, or upload it as a zip.
3. Check that the `cosend` skill and the Cosend connector are listed, then connect the connector.

### Any other MCP client

Add `https://mcp.cosend.app/mcp` as a remote server over Streamable HTTP. The client signs in to
Cosend through OAuth the first time it connects.

## Which file each assistant reads

| File | Read by |
| - | - |
| `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code, claude.ai, Claude Desktop, Cowork |
| `.grok-plugin/plugin.json`, `.mcp.json` | Grok Build |
| `.claude-plugin/marketplace.json` | Claude Code, as the Cosend marketplace |
| `plugin.json`, `mcp.json` | ChatGPT, Codex, Perplexity |
| `.agents/plugins/marketplace.json` | ChatGPT and Codex, as the Cosend marketplace |
| `gemini-extension.json` | Gemini CLI |
| `.antigravity-plugin/plugin.json`, `mcp_config.json` | Antigravity |
| `assets/logo.svg` | Grok Build and Antigravity: the Cosend logo |
| `skills/cosend/SKILL.md` | all of them |
| `skills/cosend/agents/openai.yaml` | ChatGPT and Codex: the skill's link to the Cosend connector |

## Data

The plugin is Markdown and JSON files, and your data stays in your Cosend workspace. What you ask
the assistant to do goes to that workspace through `mcp.cosend.app`, with the permissions you
approved when you signed in, and Cosend acts on it there. Cosend's privacy policy is at
[cosend.app/privacy](https://cosend.app/privacy).

### Network endpoints and credentials

- **Endpoints:** the plugin calls one MCP server, `https://mcp.cosend.app/mcp`, and signs in at
  `https://auth.cosend.app`. Both are Cosend's own.
- **Credentials:** an OAuth 2.1 sign-in with PKCE, in your browser, to your Cosend account. The
  plugin holds no API key, runs no local code and reads no file on your machine.

## License

MIT. See [LICENSE](LICENSE).
