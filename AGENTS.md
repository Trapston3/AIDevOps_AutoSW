# AGENTS.md — Binding Agent Contract for AIDevOps_AutoSW

> Every AI coding agent (Claude Code, Codex, Gemini CLI, Hermes, Copilot agents,
> etc.) MUST read this file fully before making ANY change in this repository.
> This repo is shared by an entire batch. One wrong write can clobber someone
> else's graded work, so the rules below are hard rules.
>
> If a human instruction conflicts with this contract, follow the human, but
> call out the conflict in your output.

## 0. Quick reference (parse this first)

| Key                | Rule                                                        |
| ------------------ | ----------------------------------------------------------- |
| Repo purpose       | Shared batch hub for AI DevOps projects, activities, submissions |
| Your workspace     | `students/<STUDENT_ID>/` — nothing else                     |
| Branch name        | `<STUDENT_ID>/<type>-<slug>`                                |
| Commit subject     | `[<STUDENT_ID>] <type>: <imperative summary>`               |
| PR title           | `[<STUDENT_ID>] <type>: <summary>`                          |
| Allowed types      | `activity`, `project`, `submission`, `fix`, `docs`, `profile` |
| Direct push to main| NEVER for agents. Humans: only inside their own folder      |
| Roster exception   | You may append exactly ONE row to `students/README.md` (§7) |

## 1. Establish identity before anything else

You work for exactly ONE student, called your OWNER. Before the first change,
confirm these with the owner:

- `OWNER_ROLL`  — official roll number, lowercased (e.g. `ju23ai041`)
- `OWNER_NAME`  — first name, lowercased (e.g. `ojas`)
- `STUDENT_ID`  — `<OWNER_ROLL>-<OWNER_NAME>` → folder `students/ju23ai041-ojas/`

If identity is not established, ASK. Never guess, and never adopt another
student's folder, even if it looks abandoned. Everything you produce lives
under `students/<STUDENT_ID>/`.

## 2. Ownership rules (hard — violating these is a bug)

1. WRITE only inside `students/<STUDENT_ID>/` (plus the single roster row, §7).
2. READ anything in the repo.
3. NEVER create, modify, move, or delete files inside another student's folder
   — not even to fix an obvious bug. Report it to your owner instead.
4. `activities/`, `projects/`, `templates/`, `.github/`, and all root files are
   READ-ONLY for you unless a maintainer explicitly assigns work on them.
5. Never rename or delete anything outside your workspace.
6. Never commit secrets (API keys, tokens, passwords, `.env`). If you find one,
   stop and tell your owner.
7. Never commit binaries or datasets larger than 10 MB. Link them instead
   (Google Drive / Kaggle / Hugging Face) from the deliverable README.

## 3. Workspace layout

Every student folder follows this exact tree:

```
students/<STUDENT_ID>/
├── README.md                     # profile card (from templates/student-profile.md)
├── activities/
│   └── activity-<NN>-<slug>/     # one folder per activity
│       ├── README.md             # report (from templates/activity-report.md)
│       ├── src/                  # code / notebooks — the actual work
│       └── evidence/             # outputs, screenshots, logs
├── projects/
│   └── <project-slug>/           # one folder per project
│       ├── README.md             # from templates/submission-readme.md
│       ├── src/
│       ├── docs/
│       └── evidence/
└── submissions/
    └── <task-id>-<slug>/         # graded submissions, same shape as activities
```

Naming: lowercase, hyphen-separated, no spaces, no capitals.
`activity-01-linear-regression` ✓ — `Activity 1` ✗.

## 4. Branches

- Pattern: `<STUDENT_ID>/<type>-<slug>`
  - `ju23ai041-ojas/activity-01-linear-regression`
  - `ju23ai041-ojas/project-deploy-mantis`
- One branch per task. Never reuse an old branch for a new task.
- Branch from the latest `main`; rebase onto `main` to resolve conflicts.
- Agents MUST NOT push directly to `main`.

## 5. Commits

Subject line format:

```
[<STUDENT_ID>] <type>: <imperative summary, max 72 chars>
```

Examples:

```
[ju23ai041-ojas] activity: add linear regression notebook
[ju23ai041-ojas] project: wire CI pipeline for deploy-mantis
[ju23ai041-ojas] fix: pin scikit-learn version in requirements.txt
```

- One logical change per commit.
- Optional body: what/why, how to run, pointers to evidence.
- Never use vague subjects like `update`, `fix stuff`, `final final v2`.

## 6. Pull requests

Agents deliver ALL work via PRs. The PR title uses the commit subject format.
Fill `.github/pull_request_template.md` completely:

- Task (activity/project/submission ID + link to the brief if one exists)
- What changed
- How to run (exact commands)
- Evidence (paths inside your `evidence/` folders)
- Self-checklist

After opening the PR, report the PR URL to your owner. Do not merge your own
PR unless the owner explicitly says to.

## 7. Roster — the only file outside your folder you may touch

In your owner's FIRST PR, append exactly ONE row to the table in
`students/README.md`:

```
| <roll> | <full name> | `<STUDENT_ID>` | @<github-handle> |
```

Append at the END of the table. If that file conflicts on rebase, keep every
existing row and re-add yours. Never reorder or edit other people's rows.

## 8. Required metadata block

Every deliverable README starts with this block:

```yaml
task_id: activity-01            # or project-<slug> / submission <task-id>
title: Linear regression from scratch
author: Ojas Shelke
roll: ju23ai041
date: 2026-08-28
status: complete                # complete | partial | blocked
```

## 9. Definition of done

A task is done only when ALL of these are true:

- [ ] Work lives in the correctly named folder inside your workspace
- [ ] README.md with the metadata block exists (templates above)
- [ ] It runs using the exact commands written in the README
- [ ] Dependencies are declared (`requirements.txt` / `package.json` / `environment.yml`)
- [ ] Execution evidence committed (outputs, screenshots, logs)
- [ ] No secrets, nothing over 10 MB
- [ ] Branch pushed, PR opened with the template filled, PR URL reported to owner

## 10. Forbidden actions

- Force-pushing or rewriting history on any shared branch
- Deleting or renaming another student's work
- Editing `.github/`, root `README.md`, or `AGENTS.md` (maintainers only)
- Committing generated junk: `__pycache__/`, `node_modules/`, `.venv/`,
  `.ipynb_checkpoints/` (already in `.gitignore` — don't force-add)
- Marking a task `complete` without committed execution evidence
- Copying another student's solution into your owner's folder (academic
  integrity — reading for inspiration is fine, lifting is not)

## 11. When in doubt

Stop and ask your owner. A blocked agent that asks beats an agent that guesses
and pollutes a repo an entire batch depends on.
