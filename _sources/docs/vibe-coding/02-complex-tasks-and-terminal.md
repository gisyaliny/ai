# 02 - Refactor Without Losing Behavior Workshop

**Time:** 50 minutes · **Audience:** beginners · **Updated:** November 18, 2026.

## Workshop preparation

The completed to-do app from the previous workshop; Git; Node only if you choose the optional Vite extension.

Download the {download}`shared workshop kit <../workshops/assets/workshop-kit.zip>` and extract it into a disposable folder. [Browse all workshops](../workshops/index.md). Code blocks run in your local terminal, not on this web page. Record your tool versions and use synthetic inputs.

## Hands-on route

1. Run the previous acceptance cases and record the baseline. Commit the working files with `git add index.html` and `git commit -m "Working baseline"` after reviewing their contents.
2. Ask for a read-only plan to split HTML, CSS and JavaScript into separate files. Require the same behavior and no new dependencies.
3. Review the plan, then request implementation. Inspect `git diff` before accepting the result.
4. Serve the folder with `python -m http.server 8000 --bind 127.0.0.1` in a separate terminal. Visit `http://127.0.0.1:8000`; run the same acceptance cases.
5. Stop the server with Ctrl+C. Record a regression if any previously passing behavior fails. Ask for a narrow repair and rerun the case.

```text
Read the app. Propose a behavior-preserving split into index.html, styles.css,
and app.js. Do not edit yet. List files, risks, and the regression checks.
```

Optional: migrate to Vite only after the dependency-free refactor passes. Consult Vite's current runtime requirements instead of assuming every Node release works.

## Acceptance evidence

A before/after file map, reviewed diff, passing regression table, and stopped server.

Create `evidence.md` with your environment, commands, observed outputs, failures and fixes. Label anything you did not run. Do not include secrets, screenshots of account pages, or private paths.

## Troubleshooting and cleanup

Port occupied: choose 8001. Styles missing: check relative link paths. Do not use permission bypass to solve a missing dependency. Stop any demo server when finished; retain only the small fixture and evidence needed to reproduce your result.

```{mermaid}
flowchart LR
    A["Prepare synthetic fixture"] --> B["Run guided task"]
    B --> C["Check observed result"]
    C --> D["Record evidence and limitations"]
```

> **Image Suggestion (Nanobanana Prompt)**: A clean technical workshop illustration titled “Refactor Without Losing Behavior”, with a neutral editor window, a small synthetic fixture, and an evidence checklist. Use legible navy and teal typography on a light background, even lighting, and a visible “Concept illustration” label. Show no account identity, private paths, or simulated success presented as a screenshot.

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
