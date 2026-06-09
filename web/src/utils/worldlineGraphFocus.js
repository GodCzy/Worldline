export const queryValue = (value) => {
  const rawValue = Array.isArray(value) ? value[0] : value
  return rawValue === undefined || rawValue === null ? '' : String(rawValue).trim()
}

export const normalizeId = (value) => String(value || '').trim()

export const getId = (item = {}, keys = []) =>
  keys.map((key) => item?.[key]).find((value) => value !== undefined && value !== null && value !== '')

export const stableRefId = (
  item = {},
  keys = ['id', 'entity_id', 'fact_id', 'evidenceId', 'evidence_id', 'name', 'label', 'title']
) => normalizeId(getId(item, keys))

export const refLabel = (item = {}) =>
  normalizeId(item.title || item.name || item.label || item.slug || item.id || item.fact_id || '')

export const parseGraphFocusQuery = (query = {}) => {
  const entityId = queryValue(query.entity_id || query.entity)
  const factId = queryValue(query.fact_id || query.timeline_id)
  const evidenceId = queryValue(query.evidence_id || query.evidence)
  const requestedLayer = queryValue(query.focus_layer)
  const label = queryValue(query.focus_label || query.label)
  const inferredLayer = entityId ? 'graph' : factId ? 'timeline' : evidenceId ? 'evidence' : requestedLayer
  return {
    entityId,
    factId,
    evidenceId,
    layer: requestedLayer || inferredLayer || '',
    label,
    hasFocus: Boolean(entityId || factId || evidenceId || requestedLayer || label)
  }
}

export const getEvidenceIds = (item = {}) => {
  const direct = item.evidence_ids || item.evidenceIds || item.evidence_id || item.evidenceId || []
  const values = Array.isArray(direct) ? direct : [direct]
  return values.map((value) => normalizeId(value)).filter(Boolean)
}

export const hasEvidenceFocus = (item = {}, focus = {}) =>
  Boolean(focus.evidenceId && getEvidenceIds(item).includes(focus.evidenceId))

export const getEntityStableId = (entity = {}) =>
  normalizeId(getId(entity, ['entity_id', 'id', 'node_id', 'name', 'label', 'title']))

export const getEntityTitle = (entity = {}) =>
  normalizeId(entity.name || entity.label || entity.title || entity.entity_name || getEntityStableId(entity))

export const getTimelineStableId = (fact = {}) => normalizeId(getId(fact, ['fact_id', 'id', 'timeline_id']))

export const getRelationshipStableId = (relationship = {}) =>
  normalizeId(getId(relationship, ['relationship_id', 'id', 'edge_id', 'source_id', 'target_id']))

export const getRelationshipEntityIds = (relationship = {}) =>
  [
    relationship.source_entity_id,
    relationship.target_entity_id,
    relationship.source_id,
    relationship.target_id,
    relationship.source,
    relationship.target
  ]
    .map((value) => normalizeId(value))
    .filter(Boolean)

export const getRelationshipTitle = (relationship = {}) => {
  const relationType = relationship.relation_type || relationship.type || relationship.label || 'relationship'
  const source = relationship.source_name || relationship.source || relationship.source_id || ''
  const target = relationship.target_name || relationship.target || relationship.target_id || ''
  return normalizeId(source || target ? `${source || 'source'} -> ${target || 'target'} / ${relationType}` : relationType)
}

export const isEntityFocused = (entity = {}, focus = {}) => {
  const entityId = getEntityStableId(entity)
  return Boolean((focus.entityId && entityId === focus.entityId) || hasEvidenceFocus(entity, focus))
}

export const isRelationshipFocused = (relationship = {}, focus = {}) =>
  Boolean(
    hasEvidenceFocus(relationship, focus) ||
      (focus.entityId && getRelationshipEntityIds(relationship).includes(focus.entityId))
  )

export const isTimelineFocused = (fact = {}, focus = {}) =>
  Boolean((focus.factId && getTimelineStableId(fact) === focus.factId) || hasEvidenceFocus(fact, focus))

export const isConflictFocused = (conflict = {}, focus = {}) => {
  const factIds = (conflict.fact_ids || []).map((value) => normalizeId(value))
  return Boolean((focus.factId && factIds.includes(focus.factId)) || hasEvidenceFocus(conflict, focus))
}

const uniqueMatches = (matches = []) => {
  const seen = new Set()
  return matches.filter((match) => {
    const key = `${match.kind}:${match.id || match.label}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

export const buildGraphFocusMatches = ({
  focus = {},
  entities = [],
  relationships = [],
  timeline = [],
  conflicts = []
} = {}) => {
  const entityMatches = entities
    .filter((item) => isEntityFocused(item, focus))
    .map((item) => ({ kind: 'entity', label: getEntityTitle(item), id: getEntityStableId(item) }))

  const relationshipMatches = relationships
    .filter((item) => isRelationshipFocused(item, focus))
    .map((item) => ({ kind: 'relationship', label: getRelationshipTitle(item), id: getRelationshipStableId(item) }))

  const timelineMatches = timeline
    .filter((item) => isTimelineFocused(item, focus))
    .map((item) => ({
      kind: 'timeline',
      label: item.subject || item.object || item.label || getTimelineStableId(item),
      id: getTimelineStableId(item)
    }))

  const conflictMatches = conflicts
    .filter((item) => isConflictFocused(item, focus))
    .map((item) => ({
      kind: 'conflict',
      label: `${item.subject || 'unknown'} / ${item.predicate || 'state'}`,
      id: item.conflict_key || item.fact_ids?.[0] || ''
    }))

  if (focus.factId || focus.layer === 'timeline') {
    return uniqueMatches([...timelineMatches, ...conflictMatches, ...relationshipMatches, ...entityMatches])
  }
  if (focus.entityId || focus.layer === 'graph') {
    return uniqueMatches([...entityMatches, ...relationshipMatches, ...timelineMatches, ...conflictMatches])
  }
  if (focus.evidenceId || focus.layer === 'evidence') {
    return uniqueMatches([...conflictMatches, ...timelineMatches, ...relationshipMatches, ...entityMatches])
  }
  return uniqueMatches([...entityMatches, ...relationshipMatches, ...timelineMatches, ...conflictMatches])
}

export const getFocusDisplay = (focus = {}, matches = []) => {
  if (!focus.hasFocus) return { title: '', subtitle: '' }
  if (matches.length) {
    return {
      title: matches[0].label || 'Focused graph evidence',
      subtitle: `${focus.layer || 'route'} focus matched ${matches.length} graph review item(s).`
    }
  }
  if (focus.label) return { title: focus.label, subtitle: `${focus.layer || 'route'} focus is waiting for a matching graph, timeline, or evidence record.` }
  if (focus.entityId) return { title: 'Focused entity', subtitle: 'graph focus is waiting for a matching graph, timeline, or evidence record.' }
  if (focus.factId) return { title: 'Focused timeline fact', subtitle: 'timeline focus is waiting for a matching graph, timeline, or evidence record.' }
  if (focus.evidenceId) return { title: 'Focused evidence anchor', subtitle: 'evidence focus is waiting for a matching graph, timeline, or evidence record.' }
  return { title: 'Focused graph route', subtitle: `${focus.layer || 'route'} focus is waiting for a matching graph, timeline, or evidence record.` }
}

export const focusHighlightKeywords = ({ searchInput = '', focus = {}, focusedEntities = [] } = {}) =>
  [
    searchInput,
    focus.label,
    focus.entityId,
    focusedEntities[0] ? getEntityTitle(focusedEntities[0]) : ''
  ].filter((value) => normalizeId(value))

export const nodeFocusCandidates = (node = {}) => {
  const original = node.data?.original || {}
  const properties = node.properties || original.properties || {}
  return [
    node.id,
    node.entity_id,
    node.node_id,
    node.name,
    node.label,
    node.title,
    original.id,
    original.entity_id,
    original.node_id,
    original.name,
    original.label,
    original.title,
    properties.entity_id,
    properties.node_id,
    properties.name,
    properties.label,
    properties.title
  ]
    .map((value) => normalizeId(value))
    .filter(Boolean)
}

export const findCanvasFocusNodeId = ({ nodes = [], focus = {}, focusedEntities = [] } = {}) => {
  if (!focus.hasFocus) return ''
  const targetValues = [
    focus.entityId,
    focus.label,
    focusedEntities[0] ? getEntityStableId(focusedEntities[0]) : '',
    focusedEntities[0] ? getEntityTitle(focusedEntities[0]) : ''
  ]
    .map((value) => normalizeId(value))
    .filter(Boolean)

  if (!targetValues.length) return ''

  const matchedNode = nodes.find((node) => {
    const candidates = nodeFocusCandidates(node)
    return targetValues.some((target) => candidates.includes(target))
  })

  return matchedNode?.id ? normalizeId(matchedNode.id) : ''
}

export const defaultGraphFocus = ({ entityRefs = [], timelineRefs = [] } = {}) => {
  const entity = entityRefs[0]
  if (entity) {
    return {
      layer: 'graph',
      entityId: stableRefId(entity, ['id', 'entity_id', 'name']),
      evidenceId: stableRefId(entity, ['evidenceId', 'evidence_id']),
      label: refLabel(entity)
    }
  }

  const fact = timelineRefs[0]
  if (fact) {
    return {
      layer: 'timeline',
      factId: stableRefId(fact, ['fact_id', 'id']),
      evidenceId: stableRefId(fact, ['evidenceId', 'evidence_id']),
      label: refLabel(fact)
    }
  }

  return {}
}

export const normalizeGraphFocus = (focus = {}, fallback = {}) => {
  const source = focus?.item || focus?.entity || focus?.fact || focus || {}
  const normalized = {
    layer: focus.layer || focus.focus_layer || '',
    entityId: focus.entityId || focus.entity_id || '',
    factId: focus.factId || focus.fact_id || '',
    evidenceId: focus.evidenceId || focus.evidence_id || '',
    label: focus.label || focus.focus_label || refLabel(source)
  }

  if (!normalized.entityId && (focus.targetType === 'graph' || normalized.layer === 'graph')) {
    normalized.entityId = focus.targetId || stableRefId(source, ['id', 'entity_id', 'name'])
    normalized.layer = 'graph'
  }

  if (!normalized.factId && normalized.layer === 'timeline') {
    normalized.factId = focus.targetId || stableRefId(source, ['fact_id', 'id'])
  }

  if (!normalized.evidenceId) {
    normalized.evidenceId = stableRefId(source, ['evidenceId', 'evidence_id'])
  }

  if (!normalized.entityId && !normalized.factId && !normalized.evidenceId && !normalized.layer) {
    return defaultGraphFocus(fallback)
  }

  return normalized
}

export const buildGraphFocusQuery = ({ baseQuery = {}, focus = {}, dbId = '', fallback = {} } = {}) => {
  const normalizedFocus = normalizeGraphFocus(focus, fallback)
  const query = { ...baseQuery }
  const resolvedDbId = dbId || query.knowledge_db_id || query.db_id
  if (resolvedDbId) {
    query.db_id = resolvedDbId
    query.knowledge_db_id = resolvedDbId
  }
  if (normalizedFocus.layer) query.focus_layer = normalizedFocus.layer
  if (normalizedFocus.entityId) query.entity_id = normalizedFocus.entityId
  if (normalizedFocus.factId) query.fact_id = normalizedFocus.factId
  if (normalizedFocus.evidenceId) query.evidence_id = normalizedFocus.evidenceId
  if (normalizedFocus.label) query.focus_label = normalizedFocus.label
  return query
}

export const citationEvidenceId = (citation = {}) =>
  stableRefId(citation, ['evidence_id', 'evidenceId', 'id'])

export const buildCitationGraphFocusQuery = ({ databaseId = '', citation = {}, pageTitle = '' } = {}) =>
  buildGraphFocusQuery({
    baseQuery: {},
    dbId: databaseId,
    focus: {
      layer: 'evidence',
      evidenceId: citationEvidenceId(citation),
      label: pageTitle || citation.source || citation.title || citationEvidenceId(citation),
      item: citation
    }
  })
