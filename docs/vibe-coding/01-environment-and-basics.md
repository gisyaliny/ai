# 01 - Build and Test a Small App Workshop

**Time:** 45 minutes · **Audience:** beginners · **Updated:** November 18, 2026.

## Workshop preparation

Desktop editor, Git, a supported Claude Code installation and account; no private project data.

Download the {download}`shared workshop kit <../workshops/assets/workshop-kit.zip>` and extract it into a disposable folder. [Browse all workshops](../workshops/index.md). Code blocks run in your local terminal, not on this web page. Record your tool versions and use synthetic inputs.

## Hands-on route

1. Follow the [official installation and sign-in guide](https://code.claude.com/docs/en/quickstart), then run `claude --version`. Record the version; account access and billing are separate from this workshop.
2. Create a fresh folder named `todo-workshop`. Run `git init` there and open it in your editor. Start `claude` from that folder.
3. Send the prompt below. Review each proposed file and command. Use the normal permission workflow; bypass mode is not a workshop requirement.
4. Open the generated `index.html` in a browser. Add two tasks, complete one, delete the other, and refresh. Repeat using only keyboard navigation.
5. Save an evidence table with actions, expected behavior and observed behavior. Ask for a minimal fix for any failed case, then repeat the same test.

```text
Create a single-file HTML to-do app with no dependencies or network calls.
Support add, complete, delete, and persistence after refresh using localStorage.
Reject blank tasks, use textContent for task labels, and label every control.
Explain the plan first. Ask before running terminal commands.
```

## Acceptance evidence

A working HTML file, five-case manual test table, and a reviewed diff.

Create `evidence.md` with your environment, commands, observed outputs, failures and fixes. Label anything you did not run. Do not include secrets, screenshots of account pages, or private paths.

## Troubleshooting and cleanup

Blank tasks accepted: test trim() at input. Tasks disappear: inspect localStorage and browser errors. A command fails: record the actual error before asking for a fix. Stop any demo server when finished; retain only the small fixture and evidence needed to reproduce your result.

```{mermaid}
flowchart LR
    A["Prepare synthetic fixture"] --> B["Run guided task"]
    B --> C["Check observed result"]
    C --> D["Record evidence and limitations"]
```

> **Image Suggestion (Nanobanana Prompt)**: A clean technical workshop illustration titled “Build and Test a Small App”, with a neutral editor window, a small synthetic fixture, and an evidence checklist. Use legible navy and teal typography on a light background, even lighting, and a visible “Concept illustration” label. Show no account identity, private paths, or simulated success presented as a screenshot.

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
