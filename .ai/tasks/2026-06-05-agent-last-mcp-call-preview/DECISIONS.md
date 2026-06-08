# Decisions

## No contract changes

The existing `worldline.inspect_run_artifacts` call remains the only artifact read boundary used by this stage.

## Preview before copy result

The call is recorded before Clipboard API execution so failed clipboard writes still leave a visible MCP call for manual handoff.
