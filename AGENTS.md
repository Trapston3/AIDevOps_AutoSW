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
| Repo purpose       | Shared batch hub for AI DevOps projects, activities, assignments, submissions |
| Your workspace     | `students/<USN>/` — one folder per USN, nothing else        |
| Branch name        | `<USN>/<type>-<slug>`                                       |
| Commit subject     | `[<USN>] <type>: <imperative summary>`                      |
| PR title           | `[<USN>] <type>: <summary>`                                 |
| Allowed types      | `activity`, `assignment`, `project`, `submission`, `fix`, `docs`, `profile` |
| Direct push to main| NEVER for agents. Humans: only inside their own folder      |
| Roster             | `students/README.md` is maintainer-managed — do NOT edit    |

## 1. Establish identity before anything else — the USN rule

You work for exactly ONE student, called your OWNER. Before the first change,
confirm with the owner:

- `USN` — the owner's official University Seat Number, lowercased
  (e.g. `ju23ai041`). This is the ONLY thing that names their folder.
- `OWNER_NAME` — full name, used in the roster and READMEs (never in the
  folder name).

**The workspace folder is `students/<USN>/` — the bare USN, nothing appended.**
No name suffix, no spaces, no capitals. `students/ju23ai041/` ✓ —
`students/ju23ai041-ojas/` ✗, `students/Ojas/` ✗.

- If a folder with the owner's USN already exists, that IS the workspace —
  continue inside it.
- If the owner doesn't know their USN, ASK. Never guess.
- One USN = one folder, forever. Never create a second folder for the same
  owner, and never adopt another student's folder even if it looks abandoned.

ALL assignments, activities, projects, and submissions go under
`students/<USN>/` — no work may live anywhere else.

## 2. Ownership rules (hard — violating these is a bug)

1. WRITE only inside `students/<USN>/`. No exceptions.
2. READ anything in the repo.
3. NEVER create, modify, move, or delete files inside another student's folder
   — not even to fix an obvious bug. Report it to your owner instead.
4. `activities/`, `assignments/`, `projects/`, `templates/`, `.github/`, and
   all root files are READ-ONLY for you unless a maintainer explicitly assigns
   work on them.
5. Never rename or delete anything outside your workspace.
6. Never commit secrets (API keys, tokens, passwords, `.env`). If you find one,
   stop and tell your owner.
7. Never commit binaries or datasets larger than 10 MB. Link them instead
   (Google Drive / Kaggle / Hugging Face) from the deliverable README.

## 3. Workspace layout

Every student folder follows this exact tree:

```
students/<USN>/
├── README.md                        # profile card (from templates/student-profile.md)
├── activities/
│   └── activity-<NN>-<slug>/        # one folder per activity
├── assignments/
│   └── assignment-<NN>-<slug>/      # one folder per assignment
├── projects/
│   └── <project-slug>/              # one folder per project
└── submissions/
    └── <task-id>-<slug>/            # graded submissions
```

Every deliverable folder (activity, assignment, project, submission) has the
same inner shape:

```
<deliverable>/
├── README.md      # report, from templates/ (metadata block first)
├── src/           # code / notebooks — the actual work
└── evidence/      # outputs, screenshots, logs
```

(Projects may also add a `docs/` folder.)

Naming: lowercase, hyphen-separated, no spaces, no capitals.
`assignment-02-docker-basics` ✓ — `Assignment 2` ✗.

## 4. Branches

- Pattern: `<USN>/<type>-<slug>`
  - `ju23ai041/activity-01-linear-regression`
  - `ju23ai041/assignment-02-docker-basics`
  - `ju23ai041/project-deploy-mantis`
- One branch per task. Never reuse an old branch for a new task.
- Branch from the latest `main`; rebase onto `main` to resolve conflicts.
- Agents MUST NOT push directly to `main`.

## 5. Commits

Subject line format:

```
[<USN>] <type>: <imperative summary, max 72 chars>
```

Examples:

```
[ju23ai041] activity: add linear regression notebook
[ju23ai041] assignment: complete docker basics exercises
[ju23ai041] project: wire CI pipeline for deploy-mantis
[ju23ai041] fix: pin scikit-learn version in requirements.txt
```

- One logical change per commit.
- Optional body: what/why, how to run, pointers to evidence.
- Never use vague subjects like `update`, `fix stuff`, `final final v2`.

## 6. Pull requests

Agents deliver ALL work via PRs. The PR title uses the commit subject format.
Fill `.github/pull_request_template.md` completely:

- Task (activity/assignment/project/submission ID + link to the brief if one exists)
- What changed
- How to run (exact commands)
- Evidence (paths inside your `evidence/` folders)
- Self-checklist

After opening the PR, report the PR URL to your owner. Do not merge your own
PR unless the owner explicitly says to.

## 7. Roster — maintainer-managed, do not touch

`students/README.md` (the batch roster) is maintained ONLY by the repo
maintainers. Do NOT edit it — not even to add your owner's row. Keeping the
roster out of student writes means no two submissions can ever conflict on a
shared file. Maintainers rebuild the roster from the `students/` folder names.

## 8. Required metadata block

Every deliverable README starts with this block:

```yaml
task_id: activity-01            # or assignment-<NN> / project-<slug> / submission <task-id>
title: Linear regression from scratch
author: Ojas Shelke
usn: ju23ai041
date: 2026-08-28
status: complete                # complete | partial | blocked
```

## 9. Definition of done

A task is done only when ALL of these are true:

- [ ] Work lives in the correctly named folder inside `students/<USN>/`
- [ ] README.md with the metadata block exists (templates above)
- [ ] It runs using the exact commands written in the README
- [ ] Dependencies are declared (`requirements.txt` / `package.json` / `environment.yml`)
- [ ] Execution evidence committed (outputs, screenshots, logs)
- [ ] No secrets, nothing over 10 MB
- [ ] Branch pushed, PR opened with the template filled, PR URL reported to owner

## 10. Forbidden actions

- Force-pushing or rewriting history on any shared branch
- Deleting or renaming another student's work
- Editing `.github/`, root `README.md`, `AGENTS.md`, or `students/README.md`
  (the roster — all maintainer-only)
- Creating a student folder named anything other than the bare USN
- Committing generated junk: `__pycache__/`, `node_modules/`, `.venv/`,
  `.ipynb_checkpoints/` (already in `.gitignore` — don't force-add)
- Marking a task `complete` without committed execution evidence
- Copying another student's solution into your owner's folder (academic
  integrity — reading for inspiration is fine, lifting is not)

## 11. When in doubt

Stop and ask your owner. A blocked agent that asks beats an agent that guesses
and pollutes a repo an entire batch depends on.
