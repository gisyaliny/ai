# 03 - Reproduce a Design and Preserve Context Workshop

**Time:** 45 minutes · **Audience:** beginners · **Updated:** November 18, 2026.

## Workshop preparation

The to-do app, a self-created screenshot with no personal content, and a model/client supporting image input.

Download the {download}`shared workshop kit <../workshops/assets/workshop-kit.zip>` and extract it into a disposable folder. [Browse all workshops](../workshops/index.md). Code blocks run in your local terminal, not on this web page. Record your tool versions and use synthetic inputs.

## Hands-on route

1. Create a simple reference sketch: title, input, add button and list. Save it as `reference.png`; ensure it contains no account details or personal browser tabs.
2. Attach it using the image mechanism supported by your installed client. Ask the assistant to describe the layout before making changes; verify it actually received the image.
3. Request only the layout changes, preserving behavior. Compare at 400px and 1200px browser widths and rerun the add/delete tests.
4. Write `handoff.md` containing goals, changed files, failed tests, and next steps. Start a new conversation and explicitly attach/read that handoff. Verify the assistant can state the next action correctly.
5. Optional MCP exercise: select a read-only server from its maintainer's documentation. Record the host, granted permissions, and one observed tool result. Do not connect a production database for this exercise.

```text
Describe the attached layout first. Then propose only CSS changes to match its
spacing and arrangement. Preserve task behavior. Report uncertain measurements;
do not claim pixel-perfect reproduction without comparison.
```

## Acceptance evidence

Two viewport screenshots, a handoff file, and a capability record distinguishing image input from MCP access.

Create `evidence.md` with your environment, commands, observed outputs, failures and fixes. Label anything you did not run. Do not include secrets, screenshots of account pages, or private paths.

## Troubleshooting and cleanup

No image received: use the supported attachment UI rather than assuming a pasted path uploads bytes. New session forgets decisions: read handoff.md explicitly. Stop any demo server when finished; retain only the small fixture and evidence needed to reproduce your result.

```{mermaid}
flowchart LR
    A["Prepare synthetic fixture"] --> B["Run guided task"]
    B --> C["Check observed result"]
    C --> D["Record evidence and limitations"]
```

> **Image Suggestion (Nanobanana Prompt)**: A clean technical workshop illustration titled “Reproduce a Design and Preserve Context”, with a neutral editor window, a small synthetic fixture, and an evidence checklist. Use legible navy and teal typography on a light background, even lighting, and a visible “Concept illustration” label. Show no account identity, private paths, or simulated success presented as a screenshot.

## Read More

- [Claude Code quickstart](https://code.claude.com/docs/en/quickstart) — Installation and account setup.
- [Skills](https://code.claude.com/docs/en/skills) — Supported skill paths and invocation.
- [Permissions](https://code.claude.com/docs/en/permissions) — Review the installed client's permission behavior.
- [MCP](https://code.claude.com/docs/en/mcp) — Configure a specific trusted server and inspect access.

## Knowledge Quiz

**What evidence makes this lab complete?**
<details><summary>Answer</summary>The acceptance artifacts listed above and actual observed results. A model's claim of success is insufficient.</details>

**Does accepting file edits approve every terminal command or remote action?**
<details><summary>Answer</summary>No. Editing, shell execution and remote tool permissions are separate controls; inspect the actual scope before approving.</details>
