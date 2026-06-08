# Evidence Graph Timeline Linkage Decisions

## Use Existing Rail Contract

`WorldlineEvidenceRail` already exposes the required active-layer and active-item contract, so this task keeps the changes in the Agent Workbench view and does not modify the component API.

## Keep Missing Relations Passive

Only current, resolvable graph, timeline, wiki, and evidence targets become clickable. Missing relations remain passive disabled chips so local fallback mode does not pretend unsupported targets exist.
