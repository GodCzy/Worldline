# Decisions

## Keep MCP generation centralized

Focus Dossier uses the existing `registryArtifactMcpInstruction` helper instead of defining a new URI/args shape. This keeps Registry, Artifact Rail, and Focus Dossier consistent.

## Artifact-only shortcut

Only artifact dossier items get `Copy MCP`; gate/tool/evidence links continue to behave as focus links. This prevents the dossier from becoming visually noisy before those target types have their own MCP read contracts.
