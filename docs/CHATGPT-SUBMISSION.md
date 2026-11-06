# Cosend in the ChatGPT plugin directory: the submission

Everything Ramee needs to submit Cosend to OpenAI's plugin directory, shared by ChatGPT and
Codex, in one sitting. The upload is
[`dist/cosend-chatgpt-0.2.0.zip`](../dist/cosend-chatgpt-0.2.0.zip), built and checked by
`python3 scripts/build-chatgpt-zip.py`.

Source of truth: OpenAI's package guide (developers.openai.com/plugins/build/plugins), the
submission page (/plugins/deploy/submission) and the submission error reference
(/plugins/deploy/submission-errors), as read on 6 Nov 2026.

## What the ZIP already fills in

The portal imports these from `plugin.json` and `mcp.json`, so they show as managed by the ZIP:

- **Listing:** display name `Cosend`, short description `WhatsApp inbox and campaigns`, the long
  description, developer name `Cosend`, category `Communication`, five capabilities, three
  starter prompts, the brand colour `#FF6700`, and the logo and composer icon (512 × 512 PNG).
- **Public URLs:** website `https://cosend.app/mcp`, support `https://cosend.app/support`, privacy
  `https://cosend.app/privacy`, terms `https://cosend.app/terms`. All four show Cosend as the
  publisher.
- **MCP server:** `https://mcp.cosend.app/mcp`, Streamable HTTP, OAuth with Client ID Metadata
  Document registration (Cosend also offers Dynamic Client Registration as the fallback). The
  portal needs no client ID or secret.
- **Review information:** five positive and three negative test cases, the commerce declaration
  and the release notes.

To change any of these, edit the package, run the build script and upload the new ZIP.

## Before the sitting

1. **Reviewer workspace and login.** Set up the workspace in cosend-web
   `docs/directories-submission.md`, Part C: a dedicated test account with email and password,
   the owner role, sample data, and sign-in that works at once with no second factor or
   email code. The test cases also use:
   - a contact named **Test Customer** (your own test phone) with a recent conversation;
   - an approved utility template named **order_ready**;
   - a saved audience named **VIP** on the Campaigns page, made of your own test phones, and an
     approved marketing template for it;
   - at least one automation with runs this week.
   Run all eight test cases with that account before you submit.
2. **Demo recording.** Record the script at the end of this page and upload it where the review
   team can open it, such as an unlisted video. You enter its URL in Review details.
3. **Domain verification.** Have a developer ready to deploy one plain-text file while the portal
   page is open (step 6 below).

## Steps in the dashboard

1. **Plugins:** select the organization and project that own the plugin. As an organization owner
   you can submit.
2. Select **Upload new or existing plugin** and choose your verified business identity, **Cosend**.
   The directory shows this name.
3. Select **Upload plugin** and choose `cosend-chatgpt-0.2.0.zip`. The plugin detail page opens
   with the draft.
4. **Metadata & Skills:** wait for the metadata and skill scans (skill scans take up to 2 hours)
   and resolve any issue. To fix one, correct the package, rebuild and use **Upload plugin**.
5. **MCPs:** select `cosend`, then **Connect**. Check that the server URL is
   `https://mcp.cosend.app/mcp` and authentication is OAuth.
6. **Domain verification:** the portal shows a token and a URL of the form
   `https://<host>/.well-known/openai-apps-challenge`. The developer serves exactly that token as
   plain text, with nothing else in the response, on `mcp.cosend.app` or on `cosend.app`. Select
   **Verify Domain**.
7. **Connect** and sign in to Cosend with the reviewer account, keeping every permission ticked on
   Cosend's consent screen. Wait for the tool scan, then open **Issues**.
8. **Tool annotations:** every tool needs a justification for its `readOnlyHint`, `openWorldHint`
   and `destructiveHint`. Paste the matching line from the table below.
9. **Review information → Review details:** check the imported test cases, enter the demo
   recording URL and the reviewer credentials, and select **Save details**.
10. Select the draft, choose **Submit for review**, and complete the policy attestations. Review
    feedback arrives by email.
11. Once approved, open the approved version and select **Publish plugin**.

## Field values to paste in the dashboard

| Field | Paste |
|---|---|
| Reviewer login URL | `https://dashboard.cosend.app/signin` |
| Reviewer email and password | the reviewer account's, typed into the secure form by you |
| Workspace | `Cosend Review` |
| Sign-in instructions | `Sign in with the email and password above. On Cosend's consent screen keep every permission ticked and select Approve. The workspace Cosend Review holds sample data: a WhatsApp test number, conversations with our own test phones, contacts, approved templates, a saved audience named VIP, automations with this week's runs and the AI receptionist. Each send and each campaign returns a preview first; the second call with its confirmation_token sends it, and messages reach phones we own.` |
| Demo recording URL | the link to your recording |

## Tool annotation justifications

| Tools | Hints | Justification |
|---|---|---|
| Reads of the workspace (`whoami`, the `list_`, `search_` and `get_` tools, `read_conversation`, `validate_automation`, `check_setup_link`, `automation_recipes`) | read-only true, open-world false, destructive false | `Reads the workspace's own Cosend data and changes nothing.` |
| `whatsapp_link`, `template_check`, `message_cost` | read-only true, open-world false, destructive false | `Computes its answer from the arguments and Meta's published rules and prices, and changes nothing.` |
| `get_business_profile`, `read_integration` | read-only true, open-world true, destructive false | `Reads live data from Meta or the customer's connected app and changes nothing.` |
| `send_message`, `send_campaign`, `submit_template`, `run_automation`, `mark_read`, `change_template`, `sync_templates`, `upload_media`, `update_number`, `manage_number`, `manage_integration`, `create_spreadsheet`, `change_knowledge` | read-only false, open-world true, destructive true | `Sends a WhatsApp message or writes to Meta or a connected app; what goes out stays out, so a person approves its preview first.` |
| Every other tool | read-only false, open-world false, destructive true | `Changes the workspace's Cosend data; Cosend marks every write destructive so the client asks the person first.` |

## The test cases in the ZIP

### Positive

1. **See the WhatsApp inbox at a glance**
   - Prompt: `Show me the WhatsApp chats waiting for a reply today.`
   - Tools: `get_inbox_overview`, `list_conversations`
   - Expected: how many chats are waiting, unread and with a 24-hour window closing soon, and the unread chats by contact name, with customer text marked as untrusted.
2. **Reply in an existing conversation after the person approves the preview**
   - Prompt: `Reply to Test Customer in WhatsApp with our order_ready template.`
   - Tools: `search_conversations`, `send_message`
   - Expected: the first `send_message` call returns a preview naming Test Customer and the message. After the person approves, the second call with the confirmation token sends it into that existing conversation, and it arrives on the test phone.
3. **Set up a campaign to a saved audience and send it once the person approves**
   - Prompt: `Set up a WhatsApp campaign for our weekend offer to the VIP audience, using an approved marketing template.`
   - Tools: `list_audiences`, `list_templates`, `create_campaign`, `update_campaign`, `preview_campaign`, `send_campaign`
   - Expected: the check shows who gets the campaign, who is left out and why, and Meta's list price. `send_campaign` returns a preview; after the person approves it, the campaign sends or is scheduled and appears on the Campaigns page of the Cosend dashboard.
4. **Check a WhatsApp template against Meta's rules**
   - Prompt: `Check this WhatsApp template before I submit it: utility, English, body "Hi {{1}}, your booking for {{2}} is confirmed."`
   - Tools: `template_check`
   - Expected: a verdict of fix_first, warnings or ready, with each point located in the template. The template stays a draft.
5. **Explain why an automation failed**
   - Prompt: `Did any of my automations fail this week? Tell me why.`
   - Tools: `list_runs`, `get_run`
   - Expected: each failed run with the step that failed and its error, or the report that every run this week succeeded.

### Negative

1. **A message on the person's own personal WhatsApp**
   - Prompt: `Text my friend Sam on my personal WhatsApp that I'm running late.`
   - Why: Cosend serves the business's WhatsApp workspace and replies in the business's existing conversations, so ChatGPT leaves Cosend out of it.
2. **A question outside WhatsApp**
   - Prompt: `What's a good recipe for dinner tonight?`
   - Why: ChatGPT answers it itself and calls no Cosend tool.
3. **A travel booking**
   - Prompt: `Book me a flight to Lisbon next Friday.`
   - Why: Cosend runs WhatsApp messaging for businesses, so ChatGPT calls no Cosend tool.

## Demo video script (about 75 seconds)

Record in ChatGPT, signed in as the reviewer account, with Cosend connected. Keep the WhatsApp
test phone in shot for the send.

| Time | On screen | Say |
|---|---|---|
| 0:00 to 0:08 | ChatGPT with Cosend connected | "This is Cosend in ChatGPT: a business's WhatsApp inbox, campaigns, templates and automations, in one chat." |
| 0:08 to 0:20 | Positive case 1; the answer lists the waiting chats | "I ask what's waiting today, and Cosend reads the shared WhatsApp inbox and lists the chats that need a reply." |
| 0:20 to 0:38 | Positive case 2; the preview appears; approve; the phone lights up | "I reply to a customer. Cosend shows me the exact message and who gets it, I approve, and it arrives on their phone in the same conversation." |
| 0:38 to 0:58 | Positive case 3; the check shows who gets it and the price; approve the preview | "To reach many customers, I set up a campaign to a saved audience. Cosend shows who gets it, who is left out and Meta's price, and it sends once I approve." |
| 0:58 to 1:10 | Positive case 5; the failed step and its error | "When an automation needs attention, Cosend shows the run step by step, with the exact step and the error." |
| 1:10 to 1:15 | The Cosend logo and cosend.app | "Cosend. Your WhatsApp, run from ChatGPT." |

## After publishing

OpenAI scans the MCP server daily, and eligible tool changes go live once they pass the automated
checks, with no new ZIP. Select **Rescan** under MCPs to check a server change at once. A change to
the listing, the assets or the skill is a new package version: raise `version` in `plugin.json`,
run the build script and upload the new ZIP to the same plugin.
