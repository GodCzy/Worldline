import manifestData from '@poe-data/poe/processed/cards/manifest.json'
import recommendationData from '@poe-data/poe/processed/recommendation/phase1-candidates.json'
import necromancerLoop from '@poe-data/poe/processed/graph/poe-necromancer-minion-loop.json'
import deadeyeLoop from '@poe-data/poe/processed/graph/poe-deadeye-mapping-loop.json'
import boneshatterLoop from '@poe-data/poe/processed/graph/poe-boneshatter-melee-loop.json'

const cardEntries = Array.isArray(manifestData?.cards) ? manifestData.cards : []
const cardTitleMap = new Map(cardEntries.map((item) => [item.card_id, item.title]))
const cardCategoryMap = new Map(cardEntries.map((item) => [item.card_id, item.category]))
const graphLoopList = [necromancerLoop, deadeyeLoop, boneshatterLoop]

const displayLabelMap = {
  build_recommend: '推荐场景',
  mapping_path: '刷图场景',
  mechanic_explain: '机制讲解',
  new_player_minion_league_start: '新手召唤开荒',
  returning_player_ranged_mapping: '回归远程刷图',
  returning_player_melee_progression: '回归近战推进'
}

const graphKeywordPriority = ['Build', 'SkillGem', 'Mechanic', 'Ascendancy', 'Class']

export const getCardTitleById = (cardId) => cardTitleMap.get(cardId) || cardId || ''

export const getCardCategoryById = (cardId) => cardCategoryMap.get(cardId) || ''

export const getPoeDisplayLabel = (value) => displayLabelMap[value] || value || ''

const resolveBuildCardId = (graphLoop) =>
  (graphLoop?.source_card_ids || []).find((cardId) => getCardCategoryById(cardId) === 'item_build') || ''

export const poeGraphLoops = graphLoopList.map((graphLoop) => ({
  ...graphLoop,
  build_card_id: resolveBuildCardId(graphLoop),
  node_count: Array.isArray(graphLoop?.nodes) ? graphLoop.nodes.length : 0,
  edge_count: Array.isArray(graphLoop?.edges) ? graphLoop.edges.length : 0,
  related_cards: (graphLoop?.recommended_next_cards || []).map((cardId) => ({
    id: cardId,
    title: getCardTitleById(cardId)
  }))
}))

export const getGraphLoopById = (graphId) =>
  poeGraphLoops.find((graphLoop) => graphLoop.graph_id === graphId) || null

const resolveGraphDefaultKeyword = (graphLoop) => {
  if (!graphLoop) {
    return ''
  }

  const nodes = Array.isArray(graphLoop.nodes) ? graphLoop.nodes : []
  for (const type of graphKeywordPriority) {
    const matchedNode = nodes.find((node) => node?.type === type && node?.label)
    if (matchedNode?.label) {
      return matchedNode.label
    }
  }

  return getCardTitleById(graphLoop.entry_card_id) || graphLoop.label || ''
}

export const getGraphDefaultKeyword = (graphLoopOrGraphId) => {
  const graphLoop =
    typeof graphLoopOrGraphId === 'string'
      ? getGraphLoopById(graphLoopOrGraphId)
      : graphLoopOrGraphId

  return resolveGraphDefaultKeyword(graphLoop)
}

export const poeRecommendationCandidates = (recommendationData?.candidates || []).map((candidate) => {
  const graphLoop = getGraphLoopById(candidate.graph_loop_id)

  return {
    ...candidate,
    build_title: getCardTitleById(candidate.build_card_id),
    graph_label: graphLoop?.label || candidate.graph_loop_id,
    graph_focus: graphLoop?.focus || '',
    next_card_items: (candidate.next_cards || []).map((cardId) => ({
      id: cardId,
      title: getCardTitleById(cardId)
    })),
    supporting_card_items: (candidate.supporting_card_ids || []).map((cardId) => ({
      id: cardId,
      title: getCardTitleById(cardId)
    }))
  }
})

export const getRecommendationCandidateById = (candidateId) =>
  poeRecommendationCandidates.find((candidate) => candidate.candidate_id === candidateId) || null

export const poeManifestSummary = {
  version: manifestData?.version || '',
  card_count: manifestData?.card_count || 0,
  content_type_counts: manifestData?.content_type_counts || {}
}
