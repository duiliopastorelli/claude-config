# claude-config

Public repository of Claude Code agent definitions designed for creating a team of agents.

## Why use this repository

The scope of this repository is to provide an out-of-the-box starting point for working with a team of agents serving common needs of an AI PM.

This repo is supposed to be cloned within the user's home folder. Doing so will apply these agents hierarchically above any other Claude instance. For example, running Claude within a `[myProject]` folder will automatically inherith all the agents created at a home folder level. This also allows the agents to improve themselves globally as they get used, rather than having fragmented improvement on a project-basis.

For users not experienced in Git commands, I recommend to use Claude itself to clone this repository within the home directory: it will generate an error, and Cloude will propose how to work around it.

There are 2 approaches that you can adopt:
- clone the official repository from duiliopastorelli's account - you won't be able to backup in Git on the remote branch any of your changes and improvements to the agents;
- fork the repository in your own GitHub/GitLab account and then clone it from there - you will own it, allowing you to save any change or improvement you done, but you won't get "official" updates from the original repository.
Your call.

## How agents are structured

Above all the specialised agents provided in this repository sits a coordinator (HAL). The coordinator is the only agent that is allowed to communicate directly with the user. The user can comunicate directly with specialised agents, if wanted, but it's discouraged, as specific automatic triggers assuring quality and self-improvement won't be available this way.

Once a specialised agent finishes its task(s) it communicates with other sub agents (if needed) or report back to the coordinator (in case of completion or if further input needed). A retrospective mechanism led by the Retrospective-agent assures that when the user complains about an unexpected behaviour from any agent (including the coordinator), then a process of analysis and process improvement is triggered, leading to the suggestion of modification of the specific agent .md file. The user stays in control of this process.

## How the folder structure is organised

This repository is supposed to be extracted (cloned) in the user's folder (~). This assures that any instance of Cloud run in any other folder still will utilise all the agents available.

### The general PM work

A setup that I found beneficial as PM is the "olof" (One Life One Folder) with integrated knowledge-base. PM usually work with a lot of interconnected documents, all backed up in some cloud services (like GDrive or OneDrive). The agents expect that this work is done in a folder "olof" that contains at minimum the following sub-folders:
- team-inbox/ - where the user drops files to be consumed by the agents team. These file are moved in its own archive (within the folder itself) after consumption from the agents.
- deliverables/ - where the agents will put the files that they create, for the user's evaluation. This is the user's inbox.
- knowledge-base/ - a wiki-like space where notes are kept and organised. A specific agent (Librarian-agent) is responsible to organise and maintain this folder. The agent will expect this folder to be an Obsidian vault. If a different solution is used, ask Claude to update the references.
If you want to use a different name for the folder, ask Claude to update any references from "olof" to "[yourFolderName]"

### The work that involves Git tracking

Projects that are tracked in Git (like software apps) should not reside in a folder synced by services like GDrive and OneDrive. Instead, they should be in a folder outside "olof" (the olof folder IS supposed to be backed up with a claud service).
Run Claude directly from the project's folder, thanks to the agents living in the user's folder (~) they will all be triggered and updated (if needed) anyway.

## What's in this repo

- CLAUDE.md - the file that Claude uses as an entry point for the user-generated instructions
- `agents/*.md` — one file per Claude Code sub-agent (HR-agent, Librarian-agent, etc.)
- `.gitignore` — excludes everything that is not used by Claude

## Commands

`sync agents` or `update agents` are Claude commands described in the HR-agent to retrieve any update from the repository and push any changes. Can be run in a scheduled way to receive the latest and greatest from the repository and keep everything in sync. The push function works only if the user owns the repository (fork). The default repository used is https://github.com/duiliopastorelli/claude-config. If you are working from a fork, ask Claude to update this reference.

Is the responsibility of the HR-agent to push changes to the repository when appropriate.

## Setting up a fresh machine

These steps configure a new machine to use this shared agent set.

### Prerequisites

- Claude Code installed (via the desktop app or `npm install -g @anthropic-ai/claude-code` or other appropriate way)
- GitHub CLI installed (`brew install gh`) and authenticated (`gh auth login`) - or other appropriate way
- Optional: `ANTHROPIC_API_KEY` set in `~/.claude/settings.json` (do this manually and never commit it)

### Abtain the agents

Ask Claude to clone this repository inside your user folder. Follow the instructions.

### Create the environment

Create somewhere within your backup service coverage an "olof" folder with the following sub folders:
- team-inbox/
- deliverables/
- knowledge-base/

### Test the environment

Run Claude within the "olof" folder and ask it to perform a test for all the agents and to report any incongruence or issue found.
