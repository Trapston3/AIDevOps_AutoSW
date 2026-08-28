# AIDevOps_AutoSW

Shared repository for the **AI DevOps batch** — one home for projects,
activities, assignments, and submissions. Everyone works in their own folder
under `students/`, named by their **USN**, so nobody's work collides with
anyone else's.

AI agents are first-class citizens here: every agent working in this repo must
follow the binding contract in **[AGENTS.md](AGENTS.md)**.

---

## Repository layout

```
AIDevOps_AutoSW/
├── README.md               # this file
├── AGENTS.md               # binding contract for AI coding agents
├── .github/
│   └── pull_request_template.md
├── templates/              # copy these when creating new work
│   ├── student-profile.md
│   ├── activity-report.md
│   └── submission-readme.md
├── activities/             # activity BRIEFS posted by maintainers (read-only for students)
├── assignments/            # assignment BRIEFS posted by maintainers (read-only for students)
├── projects/               # project BRIEFS posted by maintainers (read-only for students)
└── students/               # ⬅ ALL student work lives here
    ├── README.md           # batch roster (one row per student)
    ├── ju00ai000/          # fully worked EXAMPLE folder — copy this shape
    └── <USN>/              # your folder, named by your USN only
        ├── README.md
        ├── activities/activity-<NN>-<slug>/
        ├── assignments/assignment-<NN>-<slug>/
        ├── projects/<project-slug>/
        └── submissions/<task-id>-<slug>/
```

## Quick start (humans)

1. **Clone**
   ```bash
   git clone https://github.com/Trapston3/AIDevOps_AutoSW.git
   cd AIDevOps_AutoSW
   ```
2. **Create your folder** (first time only). The folder name is your USN,
   lowercased — nothing else:
   ```bash
   cp -r students/ju00ai000 students/ju23ai041
   ```
   Edit `students/ju23ai041/README.md` (your profile card). The batch roster
   (`students/README.md`) is maintainer-managed — don't edit it.
3. **Branch** — one branch per task:
   ```bash
   git checkout -b ju23ai041/activity-01-linear-regression main
   ```
4. **Do the work** inside your folder, following the layout in
   [AGENTS.md §3](AGENTS.md). Every deliverable gets a README with the metadata
   block, runnable commands, and an `evidence/` folder.
5. **Commit** with the standard subject format:
   ```
   [ju23ai041] activity: add linear regression notebook
   ```
6. **Push the branch and open a PR.** Fill the PR template. Direct pushes to
   `main` are allowed for humans ONLY inside their own folder — everything
   substantial should go through a PR so there's a clean record per task.

## Quick start (agents)

Read **[AGENTS.md](AGENTS.md)** before touching anything. The 30-second
version:

- Establish your OWNER's USN first; your workspace is `students/<USN>/` —
  the bare USN, nothing appended — and nothing else.
- All activities, assignments, projects, and submissions go under that folder.
- Never write outside your workspace — no exceptions. The roster
  (`students/README.md`) is maintainer-managed; don't touch it.
- Branch `<USN>/<type>-<slug>`, commit `[<USN>] <type>: summary`, deliver via
  PR using the template.
- Every deliverable: README with metadata block + run commands + `evidence/`.
- Never touch other students' folders, never force-push, never commit secrets
  or files over 10 MB.

## Conventions cheat sheet

| Thing            | Format                                              | Example |
| ---------------- | --------------------------------------------------- | ------- |
| Student folder   | `students/<USN>/` (bare USN, lowercase)             | `students/ju23ai041/` |
| Branch           | `<USN>/<type>-<slug>`                               | `ju23ai041/assignment-02-docker-basics` |
| Commit / PR title| `[<USN>] <type>: <imperative summary>`              | `[ju23ai041] assignment: complete docker exercises` |
| Types            | `activity`, `assignment`, `project`, `submission`, `fix`, `docs`, `profile` | |
| Deliverable folder | `activity-<NN>-<slug>` / `assignment-<NN>-<slug>` / `<project-slug>` / `<task-id>-<slug>` | `assignment-02-docker-basics` |
| Deliverable      | `README.md` (metadata block) + `src/` + `evidence/` | see `students/ju00ai000/` |

## Ground rules

1. **Stay in your lane.** Only write inside your own `students/<USN>/` folder.
2. **PRs for real work.** One branch + one PR per task keeps a clean audit
   trail for grading.
3. **Evidence or it didn't happen.** Outputs/screenshots/logs committed in
   `evidence/`.
4. **No secrets, no big binaries.** Link datasets; never commit keys.
5. **Academic integrity.** Read each other's work for inspiration; never copy.

## Maintainers

- Ojas Shelke ([@Trapston3](https://github.com/Trapston3))

Maintainers manage `activities/`, `assignments/`, `projects/`, `templates/`,
`.github/`, root files, and merge PRs. Contact a maintainer if a brief is
unclear or if someone outside your folder broke something — do not fix it
yourself.
