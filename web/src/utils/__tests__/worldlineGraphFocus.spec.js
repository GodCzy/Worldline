import assert from 'node:assert/strict'

import {
  buildCitationGraphFocusQuery,
  buildGraphFocusMatches,
  buildGraphFocusQuery,
  findCanvasFocusNodeId,
  parseGraphFocusQuery
} from '../worldlineGraphFocus.js'

const run = () => {
  const focus = parseGraphFocusQuery({
    db_id: 'kb-live',
    fact_id: ['tf-1'],
    evidence_id: 'ev-1',
    focus_label: 'Timeline focus'
  })

  assert.deepEqual(focus, {
    entityId: '',
    factId: 'tf-1',
    evidenceId: 'ev-1',
    layer: 'timeline',
    label: 'Timeline focus',
    hasFocus: true
  })

  const matches = buildGraphFocusMatches({
    focus,
    entities: [{ entity_id: 'ent-1', name: 'Graph', evidence_ids: ['ev-1'] }],
    relationships: [
      {
        relationship_id: 'rel-1',
        source_id: 'ent-1',
        target_id: 'ent-2',
        relation_type: 'mentioned_with',
        evidence_ids: ['ev-1']
      }
    ],
    timeline: [{ fact_id: 'tf-1', subject: 'Graph', evidence_ids: ['ev-1'] }],
    conflicts: [{ conflict_key: 'graph|mentioned_on|2026-06-03', subject: 'graph', predicate: 'mentioned_on', fact_ids: ['tf-1'], evidence_ids: ['ev-1'] }]
  })

  assert.deepEqual(matches.map((item) => item.kind), ['timeline', 'conflict', 'relationship', 'entity'])
  assert.equal(matches[0].id, 'tf-1')

  const graphFocusQuery = buildGraphFocusQuery({
    baseQuery: { theme: 'knowledge-ops' },
    dbId: 'kb-live',
    focus: {
      layer: 'graph',
      targetType: 'graph',
      item: { id: 'ent-1', name: 'Graph', evidenceId: 'ev-1' }
    }
  })

  assert.equal(graphFocusQuery.db_id, 'kb-live')
  assert.equal(graphFocusQuery.knowledge_db_id, 'kb-live')
  assert.equal(graphFocusQuery.entity_id, 'ent-1')
  assert.equal(graphFocusQuery.evidence_id, 'ev-1')
  assert.equal(graphFocusQuery.focus_layer, 'graph')
  assert.equal(graphFocusQuery.focus_label, 'Graph')

  const citationQuery = buildCitationGraphFocusQuery({
    databaseId: 'kb-live',
    citation: { evidence_id: 'ev-2', source: 'page-2' },
    pageTitle: 'Wiki Page'
  })

  assert.equal(citationQuery.focus_layer, 'evidence')
  assert.equal(citationQuery.evidence_id, 'ev-2')
  assert.equal(citationQuery.focus_label, 'Wiki Page')

  const focusedNodeId = findCanvasFocusNodeId({
    focus: { hasFocus: true, entityId: 'ent-1', label: 'Graph' },
    focusedEntities: [{ entity_id: 'ent-1', name: 'Graph' }],
    nodes: [
      { id: 'node-a', data: { original: { properties: { entity_id: 'ent-1' }, name: 'Graph' } } },
      { id: 'node-b', data: { original: { properties: { entity_id: 'ent-2' } } } }
    ]
  })

  assert.equal(focusedNodeId, 'node-a')

  console.log('worldlineGraphFocus: all assertions passed')
}

run()
