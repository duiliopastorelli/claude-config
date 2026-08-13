# claude-config

Public repository of Claude Code agent definitions for the olof workspace.
Agent files are prompt text — no secrets, credentials, or personal data live here.

## What's in this repo

- `agents/*.md` — one file per Claude Code sub-agent (HR-agent, Librarian-agent, etc.)
- `.gitignore` — excludes all machine-local and secret material

## Setting up a fresh machine

These steps configure a new machine to use this shared agent set.
An agent (HR-agent) can run them after `gh` and Claude Code are installed.

### Prerequisites

- Claude Code installed (via the desktop app or `npm install -g @anthropic-ai/claude-code`)
- GitHub CLI installed (`brew install gh`) and authenticated (`gh auth login`)
- `ANTHROPIC_API_KEY` set in `~/.claude/settings.json` (do this manually — never commit it)

### 1. Clone this repo

```bash
mkdir -p ~/dev && cd ~/dev
git clone https://github.com/duiliopastorelli/claude-config.git
```

### 2. Create the olof working root

**Work Mac (OneDrive):**
```bash
OLOF="$HOME/Library/CloudStorage/OneDrive-SAPSE/olof"
```

**Personal Mac (GDrive):**
```bash
OLOF="$HOME/Library/CloudStorage/GoogleDrive-[ACCOUNT]/My Drive/olof"
```

```bash
mkdir -p "$OLOF/.claude/agent-memory"
mkdir -p "$OLOF/knowledge-base"
mkdir -p "$OLOF/deliverables"
mkdir -p "$OLOF/team-inbox"
```

### 3. Symlink agents into the workspace

```bash
ln -s ~/dev/claude-config/agents "$OLOF/.claude/agents"
# Verify:
ls -la "$OLOF/.claude/"   # should show: agents -> /Users/.../dev/claude-config/agents
```

### 4. Add the session-local .gitignore

```bash
printf 'scheduled_tasks.json\nagent-memory/\n' > "$OLOF/.claude/.gitignore"
```

### 5. Create CLAUDE.md for this machine

Copy the CLAUDE.md from the other machine as a starting point, then edit the machine-specific
sections:
- Cloud path (`OLOF` variable above)
- Task tracker reference (Node/Express for work Mac; custom tracker TBD for a different machine)
- Knowledge-base description (work vault vs personal vault)
- Remove or update any context specific to the other machine (e.g. SAP-specific paths)

### 6. Add sync alias to `.zshrc`

```bash
echo "alias sync-agents='cd ~/dev/claude-config && git pull'" >> ~/.zshrc
source ~/.zshrc
```

## Syncing agent changes

Agent updates are written by HR-agent as normal. To propagate to the other machine:

**After an update on any machine:**
```bash
cd ~/dev/claude-config
git add agents/
git commit -m "Update [agent-name]: [brief reason]"
git push
```

**On the other machine (run before a session or via alias):**
```bash
sync-agents   # alias for: cd ~/dev/claude-config && git pull
```

## What does NOT live in this repo

| Item | Location | Why |
|---|---|---|
| `agent-memory/` | `olof/.claude/agent-memory/` | Machine-local; work and personal memory should diverge |
| `scheduled_tasks.json` | `olof/.claude/` | Session-ephemeral |
| `CLAUDE.md` | `olof/` root | Machine-specific context |
| `~/.claude/settings.json` | `~/.claude/` | Contains auth tokens |
| `knowledge-base/` | `olof/knowledge-base/` | Intentionally separate vaults per machine |
