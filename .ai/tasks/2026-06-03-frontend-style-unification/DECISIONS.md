# Frontend Style Unification Decisions

## Decisions

### Keep Vue/CSS Implementation

The current frontend remains Vue 3 + Vite + Ant Design Vue + G6. This pass does not introduce a new design framework or Three.js layer.

### Use One Token Source

All high-value Worldline surfaces now depend on `worldline-design.css` instead of repeating hardcoded cyan/gold/dark values in each component.

### Bring Graph Into Worldline

The graph page is treated as part of the Worldline knowledge OS rather than a separate light admin page. This keeps graph focus, evidence rail, and worldline stage visually coherent.

### Preserve Product Contracts

The pass changes styles and G6 palette defaults only. It does not change API payloads, stores, route contracts, or generation behavior.
