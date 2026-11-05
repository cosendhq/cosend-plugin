# Cosend in the ChatGPT plugin directory: the submission

Everything Ramee needs to submit Cosend to OpenAI's plugin directory for ChatGPT and Codex, in
one sitting. The upload is [`dist/cosend-chatgpt-0.2.0.zip`](../dist/cosend-chatgpt-0.2.0.zip),
built by `python3 scripts/build-chatgpt-zip.py`.

**Sources.** OpenAI's pages under developers.openai.com/plugins (the package guide, the
submission page and the submission errors page) are read here through search-engine extracts,
because this build environment's network reaches GitHub but not developers.openai.com. The
manifest fields also match OpenAI's own published plugins in
[openai/plugins](https://github.com/openai/plugins), and the package loads in the Codex CLI. A
field the portal shows differently from this page wins: follow the portal.

## Before you start

- **Identity:** your OpenAI organization is verified as a business. Publish under **Cosend**, the
  name the four public URLs show.
- **Project:** use a project with global data residency. EU-residency projects submit MCP plugins
  for review later.
- **Domain verification:** the portal gives a token to serve as plain text at
  `/.well-known/openai-apps-challenge` on `mcp.cosend.app` or on `cosend.app`. Ask a developer to
  deploy it while the portal page is open, then press **Verify Domain**.
- **Reviewer account:** the reviewer workspace and login set out in cosend-web
  `docs/directories-submission.md`, Part C: email and password, owner role, fully populated, with
  no second factor. Add a saved audience named **VIP** on its Campaigns page (your own test
  phones) and an approved marketing template, so test case 3 runs. The password goes into the
  portal's secure reviewer form, typed by you.
- **Demo recording:** record it with the script at the end of this page and upload it where
  reviewers can open it (an unlisted video link).

## The upload

Dashboard: **platform.openai.com → Plugins → Upload new or existing plugin**, choose your verified
identity, and upload `cosend-chatgpt-0.2.0.zip`. The portal reads the listing from the ZIP's
`plugin.json`, runs its automated checks, and shows the findings before you submit.

## Every field, with the text to paste

| Field | Paste |
|---|---|
| Plugin name | `Cosend` |
| Short description | `WhatsApp inbox and campaigns` |
| Description | `Cosend runs your business's WhatsApp from your AI assistant over MCP: a shared WhatsApp inbox on the number you already use, WhatsApp campaigns to saved audiences, WhatsApp templates submitted for Meta's review, WhatsApp automation built from a plain description, an AI receptionist trained on your website and files, contacts, integrations and team reports. Every send, campaign, template, automation change and switch-on comes to you as a preview you approve.` |
| Long description | read from `plugin.json`, `extensions.com.openai.interface.longDescription` |
| Developer name | `Cosend` |
| Category | `Productivity` |
| Website URL | `https://cosend.app/mcp` |
| Support URL | `https://cosend.app/support` |
| Privacy policy URL | `https://cosend.app/privacy` |
| Terms of service URL | `https://cosend.app/terms` |
| Logo | `assets/logo.png` (512 × 512 PNG, in the ZIP) |
| Composer icon | `assets/composer-icon.svg` (in the ZIP) |
| Brand colour | `#FF6700` |
| Starter prompts | `Show me the WhatsApp chats waiting for a reply today.` / `Set up a WhatsApp campaign for our weekend offer to our VIP customers.` / `Build an automation that welcomes first-time customers and answers their first questions.` |
| MCP server URL | `https://mcp.cosend.app/mcp` |
| Authentication | `OAuth`. Cosend supports Dynamic Client Registration and Client ID Metadata Documents, so the portal needs no client ID or secret. |
| Reviewer login URL | `https://app.cosend.app/signin` |
| Reviewer email and password | the reviewer account's, typed into the secure form |
| Reviewer instructions | `Sign in with the email and password above. On Cosend's consent screen keep every permission ticked and approve. The workspace "Cosend Review" holds test data: one WhatsApp test number, chats with our own test phones, contacts, approved templates, a saved audience called VIP, automations with run history and the AI receptionist. Every send and campaign returns a preview first; call again with its confirmation_token to send. Messages reach phones we own.` |
| Release notes | `First release of Cosend for ChatGPT: the WhatsApp inbox, WhatsApp campaigns, templates, automation and the AI receptionist, with every send and campaign previewed for your approval.` |
| Demo recording URL | the link to your recording |

**Tool annotations.** The portal asks for a justification of each tool's `readOnlyHint`,
`destructiveHint` and `openWorldHint`. Paste these, by kind of tool:

- **Reads** (`readOnlyHint` true, `destructiveHint` false, `openWorldHint` false): `Reads the workspace's own Cosend data and changes nothing.`
- **Reads from Meta or a connected app** (`get_business_profile`, `read_integration`; `openWorldHint` true): `Reads live data from Meta or the customer's connected app and changes nothing.`
- **Writes that reach a person or Meta** (`send_message`, `send_campaign`, `submit_template`, `run_automation` and the other tools marked `openWorldHint` true): `Sends a WhatsApp message or writes to Meta or a connected app; a sent message stays sent, so a person approves its preview first.`
- **Writes inside Cosend** (every other tool): `Changes the workspace's Cosend data; Cosend marks every write destructive so the client asks the person first.`

## Test cases

Each case runs in the reviewer workspace. *Names in ‹ › are the ones in that workspace.*

### Positive

1. **Inbox at a glance.**
   - Prompt: `Show me the WhatsApp chats waiting for a reply today.`
   - Expected tools: `get_inbox_overview`, `list_conversations`
   - Expected result: the counts of chats waiting, unread and with a window closing soon, and the unread chats by name, with customer text marked as untrusted.
2. **Reply in a conversation.**
   - Prompt: `Reply to ‹Test Customer› in WhatsApp with our order_ready template.`
   - Expected tools: `search_conversations`, `send_message` (twice)
   - Expected result: the first call returns a preview naming the recipient and the message. After the person approves, the second call with the confirmation token sends it into that existing conversation, and it arrives on the test phone.
3. **A campaign a person approves.**
   - Prompt: `Set up a WhatsApp campaign for our weekend offer to the VIP audience, using an approved marketing template.`
   - Expected tools: `list_audiences`, `list_templates`, `create_campaign`, `update_campaign`, `preview_campaign`, `send_campaign`
   - Expected result: the check shows who gets the campaign, who is left out and why, and Meta's list price. `send_campaign` returns a preview, and after the person approves it the campaign sends or is scheduled. It then shows on the Campaigns page.
4. **Template check.**
   - Prompt: `Check this WhatsApp template before I submit it: utility, English, body "Hi {{1}}, your booking for {{2}} is confirmed."`
   - Expected tools: `template_check`
   - Expected result: a verdict of fix_first, warnings or ready, with each point located in the template. The template stays a draft.
5. **Why an automation failed.**
   - Prompt: `Did any of my automations fail this week? Tell me why.`
   - Expected tools: `list_runs`, `get_run`
   - Expected result: each failed run with the step that failed and its error, or the answer that every run this week succeeded.

### Negative

1. **A personal message.**
   - Prompt: `Text my friend Sam on my personal WhatsApp that I'm running late.`
   - Expected: ChatGPT leaves Cosend out. Cosend serves the business's WhatsApp workspace, and `send_message` replies in the business's existing conversations.
2. **A question outside WhatsApp.**
   - Prompt: `What's a good recipe for dinner tonight?`
   - Expected: ChatGPT answers itself and calls no Cosend tool.
3. **Travel booking.**
   - Prompt: `Book me a flight to Lisbon next Friday.`
   - Expected: ChatGPT calls no Cosend tool.

## Demo video script (about 75 seconds)

Record in ChatGPT, signed in to the reviewer workspace, with Cosend connected. Keep the WhatsApp
test phone in shot for the send.

| Time | On screen | Say |
|---|---|---|
| 0:00 to 0:08 | ChatGPT with Cosend connected | "This is Cosend in ChatGPT: a business's WhatsApp inbox, campaigns, templates and automations, in one chat." |
| 0:08 to 0:20 | Type positive case 1; the answer lists the waiting chats | "I ask what's waiting today, and Cosend reads the shared WhatsApp inbox and lists the chats that need a reply." |
| 0:20 to 0:38 | Type positive case 2; the preview appears; approve; the phone lights up | "I reply to a customer. Cosend shows me the exact message and who gets it, I approve, and it arrives on their phone in the same conversation." |
| 0:38 to 0:58 | Type positive case 3; the campaign check shows who gets it and the price; approve the preview | "To reach many customers, I set up a campaign to a saved audience. Cosend shows who gets it, who is left out and Meta's price, and it sends once I approve." |
| 0:58 to 1:10 | Type positive case 5; the failed step and its error | "When an automation needs attention, Cosend shows the run step by step, with the exact step and the error." |
| 1:10 to 1:15 | The Cosend logo, cosend.app | "Cosend. Your WhatsApp, run from ChatGPT." |

## After you submit

The review runs in the dashboard, one version at a time. Once it is approved, press **Publish**.
Tool changes on the server then go through continuous review; a change to the listing or the
skill is a new version: raise `version` in `plugin.json`, run the build script, and upload the
new ZIP.
