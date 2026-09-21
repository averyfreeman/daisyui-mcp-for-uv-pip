 Bundled DaisyUI sources

The package bundles an offline component snapshot and the official DaisyUI skill entrypoint.

- Component refresh source: https://daisyui.com/llms.txt
- Installation specification: https://daisyui.com/docs/install/
- Official skills: https://github.com/saadeghi/daisyui/tree/master/skills/daisyui
- Skill documentation: https://daisyui.com/docs/skill/

At runtime, `daisyui-mcp refresh` fetches the current llms document and stores it in the user cache.
If the network is unavailable, the bundled snapshot remains available.
