# Security policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Contact the
maintainer at averyfreeman@gmail.com with a description, reproduction steps,
and the affected version.

## Runtime safety

The refresh operation has bounded response sizes and timeout-controlled network
requests. Skill installation extracts only files below the official
skills/daisyui archive subtree and rejects traversal paths. Installation is
explicit; the package does not write project files during import.
