# DaisyUI MCP

This context defines the language used by the local server that makes official DaisyUI documentation useful to MCP clients.

## Language

**Component**:
A DaisyUI UI primitive with a canonical name and official documentation.
_Avoid_: Widget, control

**Documentation**:
The Markdown reference material published for DaisyUI components and their usage.
_Avoid_: Scrape, page dump

**Skill**:
An official, reusable set of DaisyUI guidance intended to teach an AI tool how to work with the library.
_Avoid_: Prompt, recipe

**Content source**:
The official DaisyUI material from which a served component or skill document originates.
_Avoid_: Feed, endpoint

**Project-local installation**:
An installation of an official skill into the current project’s designated skills directory.
_Avoid_: Global installation, user installation
