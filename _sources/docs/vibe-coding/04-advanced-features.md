# 04 - Create a Reusable Review Skill Workshop

**Time:** 45 minutes · **Audience:** beginners · **Updated:** November 18, 2026.

## Workshop preparation

The toy app and a client that supports project skills. No extra plugin or server is required.

Download the {download}`shared workshop kit <../workshops/assets/workshop-kit.zip>` and extract it into a disposable folder. [Browse all workshops](../workshops/index.md). Code blocks run in your local terminal, not on this web page. Record your tool versions and use synthetic inputs.

## Hands-on route

1. Create `.claude/skills/review-demo/SKILL.md` in the disposable project using the block below.
2. Start or refresh the client and explicitly invoke `/review-demo`. Check the installed version's skill documentation if discovery differs.
3. Ask it to review the app, citing file locations. Check two findings yourself. A skill guides behavior; it does not guarantee correctness.
4. Change the instruction to prioritize keyboard access and rerun it. Compare which findings changed and whether file edits were avoided.
5. Optional: add a read-only reviewer through the current agent UI. Compare its report with the skill report. Separate context is not an operating-system sandbox. Keep hooks optional until you understand their event payload and execution permissions.

```markdown
---
name: review-demo
description: Review a small demo app without editing files.
disable-model-invocation: true
---
Read the target files. Check keyboard access, empty input, and persistence.
For each finding, cite a file location and a reproducible observation.
Do not edit files or run commands. State which checks were not performed.
```

## Acceptance evidence

One skill file and two evidence-backed review reports; no automatic edits.

Create `evidence.md` with your environment, commands, observed outputs, failures and fixes. Label anything you did not run. Do not include secrets, screenshots of account pages, or private paths.

## Troubleshooting and cleanup

Skill missing: check exact SKILL.md case, folder nesting, and current documentation. Do not assume placing an arbitrary skill.md in the project root registers it. Stop any demo server when finished; retain only the small fixture and evidence needed to reproduce your result.

```{mermaid}
flowchart LR
    A["Prepare synthetic fixture"] --> B["Run guided task"]
    B --> C["Check observed result"]
    C --> D["Record evidence and limitations"]
```

> **Image Suggestion (Nanobanana Prompt)**: A clean technical workshop illustration titled “Create a Reusable Review Skill”, with a neutral editor window, a small synthetic fixture, and an evidence checklist. Use legible navy and teal typography on a light background, even lighting, and a visible “Concept illustration” label. Show no account identity, private paths, or simulated success presented as a screenshot.

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
