<template>
  <div class="agent-workbench">
    <header class="agent-header">
      <div>
        <p class="eyebrow">AGENT WORLDLINE</p>
        <h1>Agent 工作台</h1>
        <p>
          把一次 Agent 任务拆成计划、证据、工具、审查和技能候选分支；每条分支都能被回放、审批和验证。
        </p>
      </div>

      <nav class="agent-actions" aria-label="Worldline agent navigation">
        <router-link to="/worldline">首页</router-link>
        <router-link to="/themes">模块</router-link>
        <router-link to="/graph">图谱</router-link>
      </nav>
    </header>

    <main class="agent-shell">
      <aside class="run-rail">
        <section class="rail-panel run-card">
          <div class="panel-head">
            <p class="eyebrow">任务账本</p>
            <span>{{ protocolLabel }}</span>
          </div>
          <h2>{{ run.title }}</h2>
          <p>{{ run.goal }}</p>

          <div class="run-stats">
            <div>
              <strong>{{ worldlineStore.branchCount }}</strong>
              <span>分支</span>
            </div>
            <div>
              <strong>{{ agentRun.episodes.length }}</strong>
              <span>回合</span>
            </div>
            <div>
              <strong>{{ agentRun.skillProposals.length }}</strong>
              <span>技能</span>
            </div>
          </div>

          <div class="ledger-status" :class="ledgerStateClass">
            <div>
              <CheckCircle2 v-if="ledgerRunId" :size="16" />
              <strong>{{ ledgerStateLabel }}</strong>
              <span>{{ ledgerRunId || '本地预览' }}</span>
            </div>
            <p>{{ ledgerMessage }}</p>
          </div>

          <div class="ledger-actions">
            <button class="sync-action" type="button" :disabled="!canUseRunLedger || ledgerBusy" @click="syncRunToLedger">
              <Save :size="15" />
              <span>{{ ledgerRunId ? '重新同步账本' : '保存到后端账本' }}</span>
            </button>
            <button
              class="sync-action secondary"
              type="button"
              :disabled="!canUseRunLedger || ledgerBusy || ledgerEventsBusy || !ledgerRunId"
              @click="refreshLedgerEvents"
            >
              <RefreshCw :size="15" />
              <span>事件 {{ ledgerEventsTotal || ledgerEvents.length }}</span>
            </button>
          </div>

          <div class="run-selector" data-run-selector="true">
            <div class="run-selector-head">
              <div class="run-selector-title">
                <p class="eyebrow">任务选择</p>
                <strong>{{ ledgerRunListTotal }} 个已保存任务</strong>
              </div>
              <button
                class="run-selector-refresh"
                type="button"
                data-run-selector-refresh="true"
                :disabled="!canUseRunLedger || ledgerBusy || ledgerRunListBusy"
                @click="refreshLedgerRuns"
              >
              <RefreshCw :size="13" />
                <span>{{ ledgerRunListBusy ? '加载中' : '刷新任务' }}</span>
              </button>
            </div>
            <p>{{ runSelectorMessage }}</p>
            <form class="run-selector-filters" data-run-selector-filters="true" @submit.prevent="refreshLedgerRuns">
              <input
                v-model.trim="ledgerRunQuery"
                type="search"
                placeholder="搜索任务"
                aria-label="搜索后端任务"
                data-run-selector-query="true"
              />
              <select v-model="ledgerRunStatus" aria-label="筛选任务状态" data-run-selector-status="true">
                <option value="">全部状态</option>
                <option value="ready">就绪</option>
                <option value="approved">已审批</option>
                <option value="synced">已同步</option>
                <option value="failed">失败</option>
                <option value="archived">已归档</option>
              </select>
              <input
                v-model.trim="ledgerRunThemeId"
                type="text"
                placeholder="主题"
                aria-label="筛选任务主题"
                data-run-selector-theme="true"
              />
              <input
                v-model.trim="ledgerRunCreatedBy"
                type="text"
                placeholder="创建人"
                aria-label="筛选创建人"
                data-run-selector-created-by="true"
              />
              <button class="run-selector-refresh secondary" type="submit" :disabled="!canUseRunLedger || ledgerBusy || ledgerRunListBusy">
                <span>应用</span>
              </button>
              <button
                class="run-selector-refresh secondary"
                type="button"
                :disabled="ledgerBusy || ledgerRunListBusy || !hasRunSelectorFilters"
                @click="clearLedgerRunFilters"
              >
                <span>清空</span>
              </button>
            </form>
            <form class="run-maintenance" data-run-maintenance="true" @submit.prevent="renameActiveLedgerRun">
              <input
                v-model.trim="runMaintenanceTitle"
                type="text"
                placeholder="当前任务标题"
                aria-label="重命名当前任务"
                data-run-rename-title="true"
              />
              <button
                class="run-selector-refresh secondary"
                type="submit"
                data-run-rename-active="true"
                :disabled="!ledgerRunId || !runMaintenanceTitle || ledgerBusy || runMaintenanceBusy || !canUseRunLedger"
              >
                <span>{{ runMaintenanceBusy && runMaintenanceTarget === ledgerRunId ? '重命名中' : '重命名' }}</span>
              </button>
            </form>
            <p v-if="runMaintenanceMessage">{{ runMaintenanceMessage }}</p>
            <div class="run-selector-bulk" data-run-selector-bulk="true">
              <span>{{ selectedLedgerRunCount ? `已选 ${selectedLedgerRunCount} 个` : '选择任务' }}</span>
              <button
                class="run-selector-refresh secondary"
                type="button"
                data-run-bulk-archive="true"
                :disabled="!selectedArchiveRuns.length || ledgerBusy || runMaintenanceBusy || !canUseRunLedger"
                @click="archiveSelectedLedgerRuns"
              >
                <span>{{ runMaintenanceBusy && runMaintenanceTarget === 'bulk-archive' ? '归档中' : '归档' }}</span>
              </button>
              <button
                class="run-selector-refresh secondary"
                type="button"
                data-run-bulk-restore="true"
                :disabled="!selectedRestoreRuns.length || ledgerBusy || runMaintenanceBusy || !canUseRunLedger"
                @click="restoreSelectedLedgerRuns"
              >
                <span>{{ runMaintenanceBusy && runMaintenanceTarget === 'bulk-restore' ? '恢复中' : '恢复' }}</span>
              </button>
              <button
                class="run-selector-refresh secondary"
                type="button"
                data-run-bulk-clear="true"
                :disabled="!selectedLedgerRunCount || ledgerBusy || runMaintenanceBusy"
                @click="clearLedgerRunSelection"
              >
                <span>清空</span>
              </button>
            </div>
            <div v-if="visibleLedgerRuns.length" class="run-selector-list">
              <article
                v-for="item in visibleLedgerRuns"
                :key="item.id"
                class="run-selector-item"
                :class="{ active: item.id === ledgerRunId }"
                :data-run-selector-item="item.id"
              >
                <label class="run-selector-pick" :title="`选择 ${item.title || item.id}`">
                  <input
                    v-model="selectedLedgerRunIds"
                    type="checkbox"
                    :value="item.id"
                    :data-run-selector-select="item.id"
                    :disabled="ledgerBusy || runMaintenanceBusy || !canUseRunLedger"
                  />
                </label>
                <button
                  class="run-selector-load"
                  type="button"
                  :data-run-selector-load="item.id"
                  :disabled="ledgerBusy || !canUseRunLedger"
                  @click="loadLedgerRun(item.id)"
                >
                  <span>{{ item.title || item.id }}</span>
                  <small>{{ runSummaryMeta(item) }}</small>
                </button>
                <button
                  class="run-selector-compare"
                  type="button"
                  :data-run-selector-compare="item.id"
                  :disabled="!ledgerRunId || item.id === ledgerRunId || ledgerBusy || runCompareBusy || !canUseRunLedger"
                  @click="compareLedgerRun(item.id)"
                >
                  <span>{{ runCompareBusy && runCompareTarget === item.id ? '对比中' : '对比' }}</span>
                </button>
                <button
                  v-if="item.status === 'archived'"
                  class="run-selector-archive restore"
                  type="button"
                  :data-run-selector-restore="item.id"
                  :disabled="ledgerBusy || runMaintenanceBusy || !canUseRunLedger"
                  @click="restoreLedgerRun(item.id)"
                >
                  <span>{{ runMaintenanceBusy && runMaintenanceTarget === item.id ? '恢复中' : '恢复' }}</span>
                </button>
                <button
                  v-else
                  class="run-selector-archive"
                  type="button"
                  :data-run-selector-archive="item.id"
                  :disabled="ledgerBusy || runMaintenanceBusy || !canUseRunLedger"
                  @click="archiveLedgerRun(item.id)"
                >
                  <span>{{ runMaintenanceBusy && runMaintenanceTarget === item.id ? '归档中' : '归档' }}</span>
                </button>
              </article>
            </div>
            <div v-if="ledgerRunList.length" class="run-selector-pagination" data-run-selector-pagination="true">
              <span>已载入 {{ ledgerRunList.length }}/{{ ledgerRunListTotal || ledgerRunList.length }}</span>
              <button
                class="run-selector-refresh secondary"
                type="button"
                data-run-selector-load-more="true"
                :disabled="!canLoadMoreLedgerRuns || ledgerBusy || ledgerRunListBusy || !canUseRunLedger"
                @click="loadMoreLedgerRuns"
              >
                <span>{{ ledgerRunListBusy && canLoadMoreLedgerRuns ? '加载中' : '载入更多' }}</span>
              </button>
            </div>
            <div v-if="runCompareResult || runCompareMessage" class="run-diff-panel" data-run-diff-panel="true">
              <div class="run-diff-head">
                <div>
                  <p class="eyebrow">任务对比</p>
                  <strong>{{ runCompareTitle }}</strong>
                </div>
                <span>{{ runCompareTotalDelta }} 项差异</span>
              </div>
              <p>{{ runCompareMessage }}</p>
              <dl v-if="runCompareResult" class="run-diff-counts">
                <div>
                  <dt>新增</dt>
                  <dd>{{ runCompareResult.summary?.added || 0 }}</dd>
                </div>
                <div>
                  <dt>缺失</dt>
                  <dd>{{ runCompareResult.summary?.removed || 0 }}</dd>
                </div>
                <div>
                  <dt>变化</dt>
                  <dd>{{ runCompareResult.summary?.changed || 0 }}</dd>
                </div>
              </dl>
              <div v-if="runCompareTimeline.length" class="run-diff-timeline">
                <div v-for="item in runCompareTimeline" :key="item.key" class="run-diff-row">
                  <span>{{ item.label }}</span>
                  <small>+{{ item.added }} / -{{ item.removed }} / Δ{{ item.changed }}</small>
                </div>
              </div>
            </div>
          </div>

          <div class="replay-export-panel" data-replay-export="true">
            <div class="replay-export-head">
              <p class="eyebrow">REPLAY EXPORT</p>
              <span>{{ replayExportArtifact.replayTimeline.length }} steps</span>
            </div>

            <div class="replay-export-actions">
              <button class="replay-export-action" type="button" @click="downloadReplayExport">
                <Download :size="14" />
                <span>Download JSON</span>
              </button>
              <button class="replay-export-action" type="button" @click="copyReplayExportMarkdown">
                <Clipboard :size="14" />
                <span>Copy Markdown</span>
              </button>
              <button class="replay-export-action" type="button" @click="toggleReplayExportPreview">
                <Eye :size="14" />
                <span>{{ exportPreviewOpen ? 'Hide Preview' : 'Preview Artifact' }}</span>
              </button>
              <button
                class="replay-export-action"
                type="button"
                :disabled="!canUseRunLedger || ledgerBusy || artifactSaveBusy"
                @click="saveReplayExportArtifact"
              >
                <Save :size="14" />
                <span>{{ artifactSaveBusy ? 'Saving Artifact' : 'Save Artifact' }}</span>
              </button>
            </div>

            <p v-if="exportMessage" class="replay-export-message">{{ exportMessage }}</p>
            <p v-if="artifactRegistryMessage" class="replay-export-message">{{ artifactRegistryMessage }}</p>
            <div v-if="artifactRegistryItems.length" class="replay-export-registry" data-artifact-registry="true">
              <div class="registry-head">
                <strong>Registry</strong>
                <span>{{ filteredArtifactRegistryItems.length }}/{{ artifactRegistryItems.length }}</span>
              </div>
              <div class="registry-filters" aria-label="Artifact registry filters">
                <button
                  v-for="filter in artifactRegistryFilters"
                  :key="filter.id"
                  class="registry-filter-button"
                  :class="{ active: artifactRegistryFilter === filter.id }"
                  type="button"
                  @click="artifactRegistryFilter = filter.id"
                >
                  <span>{{ filter.label }}</span>
                  <small>{{ filter.count }}</small>
                </button>
              </div>
              <div
                v-for="artifact in filteredArtifactRegistryItems"
                :key="artifact.id"
                class="registry-artifact-row"
              >
                <button
                  class="registry-artifact-button"
                  type="button"
                  @click="focusRegisteredArtifact(artifact)"
                >
                  <span>{{ artifact.label || artifact.id }}</span>
                  <small>
                    {{ registryArtifactTypeLabel(artifact) }} / {{ artifact.registryState || 'saved' }}
                  </small>
                </button>
                <button
                  class="registry-mcp-button"
                  type="button"
                  @click="copyRegistryArtifactMcpCall(artifact)"
                >
                  <Clipboard :size="12" />
                  <span>Copy MCP</span>
                </button>
                <button
                  v-if="isResourceDetailSnapshotArtifact(artifact)"
                  class="registry-mcp-button"
                  type="button"
                  :data-resource-detail-replay="artifact.id"
                  :disabled="
                    artifact.registryState !== 'saved' ||
                    !canUseRunLedger ||
                    ledgerBusy ||
                    resourceDrilldownBusy ||
                    resourceDetailReplayBusyId === artifact.id
                  "
                  @click="replayResourceDetailArtifact(artifact)"
                >
                  <Eye :size="12" />
                  <span>{{ resourceDetailReplayBusyId === artifact.id ? '读取中' : '读取详情' }}</span>
                </button>
                <button
                  v-if="isResourceDetailSnapshotArtifact(artifact)"
                  class="registry-mcp-button"
                  type="button"
                  :data-resource-detail-diff="artifact.id"
                  :disabled="
                    artifact.registryState !== 'saved' ||
                    !resourceDrilldownResult ||
                    !canUseRunLedger ||
                    ledgerBusy ||
                    resourceDrilldownBusy ||
                    resourceDetailCompareBusyId === artifact.id
                  "
                  @click="compareResourceDetailSnapshotArtifact(artifact)"
                >
                  <Eye :size="12" />
                  <span>{{ resourceDetailCompareBusyId === artifact.id ? '对比中' : '对比详情' }}</span>
                </button>
              </div>
            </div>
            <div class="mcp-readable-panel" data-mcp-readable="true">
              <div class="mcp-readable-head">
                <p class="eyebrow">MCP READABLE</p>
                <span :class="['mcp-readable-status', mcpReadableState]">{{ mcpReadableLabel }}</span>
              </div>
              <dl class="mcp-readable-meta">
                <div>
                  <dt>Tool</dt>
                  <dd>{{ MCP_RUN_ARTIFACT_TOOL }}</dd>
                </div>
                <div>
                  <dt>URI</dt>
                  <dd>{{ mcpReadableArtifactUri }}</dd>
                </div>
              </dl>
              <button
                class="mcp-readable-copy secondary"
                type="button"
                data-detail-modal-open="mcp-readable"
                @click="openMcpReadableArgsModal"
              >
                <Eye :size="13" />
                <span>查看 MCP 参数</span>
              </button>
              <button class="mcp-readable-copy" type="button" @click="copyMcpReadInstruction">
                <Clipboard :size="13" />
                <span>复制 MCP 调用</span>
              </button>
              <p>{{ mcpReadableHint }}</p>
              <div class="run-mcp-manifest" data-run-mcp-manifest="true">
                <div class="run-mcp-manifest-head">
                  <strong>MCP 资源清单</strong>
                  <span>{{ runMcpManifestTotal }} 个资源</span>
                </div>
                <dl class="run-mcp-manifest-counts">
                  <div v-for="item in runMcpManifestCounts" :key="item.key">
                    <dt>{{ item.label }}</dt>
                    <dd>{{ item.count }}</dd>
                  </div>
                </dl>
                <button
                  class="mcp-readable-copy secondary"
                  type="button"
                  data-detail-modal-open="run-manifest"
                  @click="openRunManifestArgsModal"
                >
                  <Eye :size="13" />
                  <span>查看 Manifest 参数</span>
                </button>
                <button class="mcp-readable-copy" type="button" @click="copyRunManifestMcpCall">
                  <Clipboard :size="13" />
                  <span>复制 Manifest 调用</span>
                </button>
                <button
                  class="mcp-readable-copy"
                  type="button"
                  :disabled="!ledgerRunId || !canUseRunLedger || ledgerBusy || runManifestBusy"
                  @click="loadBackendRunManifest"
                >
                  <RefreshCw :size="13" />
                  <span>{{ runManifestBusy ? '载入清单中' : '载入后端清单' }}</span>
                </button>
                <div class="run-manifest-api-inspector" data-run-manifest-api-inspector="true">
                  <div class="run-manifest-api-head">
                    <strong>后端清单</strong>
                    <span :class="['run-manifest-api-status', backendRunManifestStatus]">
                      {{ backendRunManifestStatusLabel }}
                    </span>
                  </div>
                  <p>{{ backendRunManifestSummary }}</p>
                  <dl v-if="backendRunManifestCounts.length" class="run-mcp-manifest-counts">
                    <div v-for="item in backendRunManifestCounts" :key="item.key">
                      <dt>{{ item.label }}</dt>
                      <dd>{{ item.count }}</dd>
                    </div>
                  </dl>
                  <div v-if="backendRunManifestTools.length" class="run-manifest-api-tools">
                    <span v-for="tool in backendRunManifestTools" :key="tool.name">{{ tool.name }}</span>
                  </div>
                  <ul v-if="backendRunManifestResources.length" class="run-manifest-api-resources">
                    <li v-for="resource in backendRunManifestResources" :key="resource.key">
                      <div class="run-manifest-resource-head">
                        <span>{{ resource.section }}</span>
                        <button
                          type="button"
                          :disabled="resourceDrilldownBusy || !canUseRunLedger"
                          @click="inspectBackendManifestResource(resource)"
                        >
                          {{ resourceDrilldownBusy && resourceDrilldownTarget === resource.key ? '读取中' : '检查' }}
                        </button>
                      </div>
                      <code>{{ resource.uri }}</code>
                    </li>
                  </ul>
                  <div
                    v-if="resourceDrilldownResult || resourceDrilldownMessage"
                    class="run-manifest-resource-detail"
                    data-run-resource-drilldown="true"
                  >
                    <div class="run-manifest-api-head">
                      <strong>资源详情</strong>
                      <span :class="['run-manifest-api-status', resourceDrilldownResult ? 'loaded' : 'failed']">
                        {{ resourceDrilldownResult ? '已载入' : '待检查' }}
                      </span>
                    </div>
                    <p>{{ resourceDrilldownMessage }}</p>
                    <dl v-if="resourceDrilldownResult" class="run-resource-detail-summary">
                      <div v-for="item in resourceDrilldownSummaryCards" :key="item.key">
                        <dt>{{ item.label }}</dt>
                        <dd>{{ item.value }}</dd>
                      </div>
                    </dl>
                    <dl v-if="resourceDrilldownResult" class="last-mcp-call-meta">
                      <div>
                        <dt>工具</dt>
                        <dd>{{ resourceDrilldownResult.tool }}</dd>
                      </div>
                      <div>
                        <dt>URI</dt>
                        <dd>{{ resourceDrilldownResult.uri }}</dd>
                      </div>
                    </dl>
                    <div v-if="resourceDrilldownResult" class="run-resource-detail-actions">
                      <button
                        class="mcp-readable-copy"
                        type="button"
                        data-run-resource-save-artifact="true"
                        :disabled="resourceDetailSaveBusy || ledgerBusy || !canUseRunLedger"
                        @click="saveResourceDetailArtifact"
                      >
                        {{ resourceDetailSaveBusy ? '保存中' : '保存详情证据' }}
                      </button>
                      <button
                        class="mcp-readable-copy secondary"
                        type="button"
                        data-detail-modal-open="resource-response"
                        @click="openResourceDetailResponseModal"
                      >
                        <Eye :size="13" />
                        <span>查看后端响应</span>
                      </button>
                    </div>
                    <div
                      v-if="resourceDetailCompareResult || resourceDetailCompareMessage"
                      class="resource-detail-diff-panel"
                      data-resource-detail-diff-panel="true"
                    >
                      <div class="run-diff-head">
                        <div>
                          <p class="eyebrow">详情差异</p>
                          <strong>{{ resourceDetailCompareResult?.title || '资源详情快照对比' }}</strong>
                        </div>
                        <span>{{ resourceDetailCompareTotalDelta }} 项差异</span>
                      </div>
                      <p>{{ resourceDetailCompareMessage }}</p>
                      <dl v-if="resourceDetailCompareResult" class="run-diff-counts">
                        <div>
                          <dt>新增</dt>
                          <dd>{{ resourceDetailCompareResult.summary.added }}</dd>
                        </div>
                        <div>
                          <dt>缺失</dt>
                          <dd>{{ resourceDetailCompareResult.summary.removed }}</dd>
                        </div>
                        <div>
                          <dt>变化</dt>
                          <dd>{{ resourceDetailCompareResult.summary.changed }}</dd>
                        </div>
                      </dl>
                      <div v-if="resourceDetailCompareResult?.preview?.length" class="run-diff-timeline">
                        <div
                          v-for="item in resourceDetailCompareResult.preview"
                          :key="`${item.type}:${item.path}`"
                          class="run-diff-row"
                          :title="`${item.path} - ${item.typeLabel}`"
                        >
                          <span>{{ item.path }}</span>
                          <small>{{ item.typeLabel }}</small>
                        </div>
                      </div>
                      <button
                        v-if="resourceDetailCompareResult"
                        class="mcp-readable-copy"
                        type="button"
                        data-resource-detail-diff-save="true"
                        :disabled="resourceDetailDiffSaveBusy || ledgerBusy || !canUseRunLedger"
                        @click="saveResourceDetailDiffArtifact"
                      >
                        {{ resourceDetailDiffSaveBusy ? '保存中' : '保存差异证据' }}
                      </button>
                    </div>
                  </div>
                </div>
                <p v-if="runManifestMessage" class="replay-export-message">{{ runManifestMessage }}</p>
              </div>
              <p v-if="mcpReadMessage" class="replay-export-message">{{ mcpReadMessage }}</p>
              <div v-if="lastMcpCall" class="last-mcp-call" data-last-mcp-call="true">
                <div class="last-mcp-call-head">
                  <strong>最近 MCP 调用</strong>
                  <span>{{ lastMcpCall.sourceLabel }}</span>
                </div>
                <p>{{ lastMcpCall.label }}</p>
                <dl class="last-mcp-call-meta">
                  <div>
                    <dt>工具</dt>
                    <dd>{{ lastMcpCall.tool }}</dd>
                  </div>
                  <div>
                    <dt>URI</dt>
                    <dd>{{ lastMcpCall.uri }}</dd>
                  </div>
                </dl>
                <button
                  class="mcp-readable-copy secondary"
                  type="button"
                  data-detail-modal-open="last-mcp"
                  @click="openLastMcpArgsModal"
                >
                  <Eye :size="13" />
                  <span>查看调用参数</span>
                </button>
              </div>
            </div>
            <div class="agent-handoff-panel" data-agent-handoff="true">
              <div class="agent-handoff-head">
                <p class="eyebrow">AGENT HANDOFF</p>
                <span>{{ savedHandoffArtifact ? 'saved' : agentHandoffCapsule.boundary.write_scope }}</span>
              </div>
              <p>{{ agentHandoffCapsule.intent }}</p>
              <dl class="agent-handoff-meta">
                <div>
                  <dt>Protocol</dt>
                  <dd>{{ agentHandoffCapsule.protocol }}</dd>
                </div>
                <div>
                  <dt>Target</dt>
                  <dd>{{ agentHandoffCapsule.source.event_label }}</dd>
                </div>
                <div>
                  <dt>Rule</dt>
                  <dd>{{ agentHandoffCapsule.quality.rollback }}</dd>
                </div>
              </dl>
              <div class="agent-handoff-actions">
                <button class="agent-handoff-action" type="button" @click="toggleHandoffCapsulePreview">
                  <Eye :size="13" />
                  <span>{{ handoffPreviewOpen ? 'Hide Capsule' : 'Preview Capsule' }}</span>
                </button>
                <button class="agent-handoff-action" type="button" @click="copyHandoffCapsule">
                  <Clipboard :size="13" />
                  <span>Copy Handoff</span>
                </button>
                <button
                  class="agent-handoff-action save"
                  type="button"
                  :disabled="!canUseRunLedger || ledgerBusy || handoffSaveBusy"
                  @click="saveAgentHandoffCapsule"
                >
                  <Save :size="13" />
                  <span>{{ handoffSaveBusy ? 'Saving Handoff' : 'Save Handoff' }}</span>
                </button>
              </div>
              <pre v-if="handoffPreviewOpen" class="handoff-capsule-preview">{{ agentHandoffCapsulePreview }}</pre>
              <p v-if="handoffMessage" class="replay-export-message">{{ handoffMessage }}</p>
            </div>
            <pre v-if="exportPreviewOpen" class="replay-export-preview">{{ replayExportMarkdown }}</pre>
          </div>
        </section>

        <section class="rail-panel">
          <p class="eyebrow">TASK PROMPT</p>
          <textarea
            v-model="questionDraft"
            rows="7"
            aria-label="Agent worldline task prompt"
            @keydown.ctrl.enter.prevent="regenerateRun"
          />
          <button class="primary-action" type="button" @click="regenerateRun">
            <RefreshCw :size="16" />
            <span>重建任务世界线</span>
          </button>
        </section>

        <section class="rail-panel branch-list">
          <p class="eyebrow">BRANCHES</p>
          <button
            v-for="branch in worldlineStore.branches"
            :key="branch.id"
            class="branch-button"
            :class="{ active: branch.id === worldlineStore.activeBranchId, focused: isBranchFocused(branch) }"
            type="button"
            :data-inspector-target="`branch:${branch.id}`"
            @click="selectBranch(branch.id)"
          >
            <span>{{ branch.title }}</span>
            <small>{{ branch.choiceLabel }} / {{ branch.status || branch.quality?.status }}</small>
          </button>
        </section>

        <section class="rail-panel contract-panel">
          <p class="eyebrow">CONTRACT</p>
          <dl>
            <div v-for="(fields, name) in agentRun.contract" :key="name">
              <dt>{{ name }}</dt>
              <dd>{{ fields.length }} fields</dd>
            </div>
          </dl>
        </section>
      </aside>

      <section class="stage-column">
        <WorldlineBranchCanvas
          :tree="worldlineStore.tree"
          :active-branch-id="worldlineStore.activeBranchId"
          :selected-node-id="worldlineStore.selectedNodeId"
          :branch-count="worldlineStore.branchCount"
          :display-meta="worldlineStore.displayMeta"
          :active-snapshot="worldlineStore.activeSnapshot"
          @select-node="handleCanvasSelect"
        />

        <WorldlineTimelineScrubber
          :snapshots="worldlineStore.snapshots"
          :active-index="worldlineStore.activeSnapshotIndex"
          :timeline-refs="worldlineStore.timelineRefs"
          :active-timeline-id="activeTimelineId"
          @update:active-index="worldlineStore.setActiveSnapshot"
        />

        <section class="episode-strip" aria-label="Agent episode replay">
          <button
            v-for="episode in activeEpisodes"
            :key="episode.id"
            class="episode-card"
            :class="{ active: isEpisodeFocused(episode) }"
            type="button"
            :aria-pressed="isEpisodeFocused(episode)"
            :data-inspector-target="`episode:${episode.id}`"
            @click="focusEpisodeCard(episode)"
          >
            <span class="episode-actor">{{ episode.actor }}</span>
            <strong>{{ episode.output }}</strong>
            <small>{{ episodeReplaySummary(episode) }}</small>
            <span class="episode-metrics" aria-label="Episode replay counters">
              <span v-for="chip in episodeReplayChips(episode)" :key="chip.key">
                {{ chip.label }} {{ chip.value }}
              </span>
            </span>
          </button>
        </section>
      </section>

      <aside class="inspect-rail">
        <WorldlineBranchDetailPanel
          :branch="worldlineStore.activeBranch"
          @handoff="handleBranchAction"
          @open-graph="handleBranchAction"
        />

        <section class="rail-panel event-panel">
          <div class="panel-head">
            <p class="eyebrow">RUN EVENTS</p>
            <span>{{ ledgerEvents.length || visibleLedgerEvents.length }}/{{ ledgerEventsTotal || visibleLedgerEvents.length }} events</span>
          </div>

          <div class="event-filter" aria-label="Run event filters">
            <button
              v-for="filter in ledgerEventFilters"
              :key="filter.id"
              class="event-filter-button"
              :class="{ active: activeEventFilter === filter.id }"
              type="button"
              @click="activeEventFilter = filter.id"
            >
              <span>{{ filter.label }}</span>
              <small>{{ filter.count }}</small>
            </button>
          </div>
          <div class="event-audit-toolbar" data-run-event-audit="true">
            <input
              v-model.trim="eventAuditQuery"
              type="search"
              placeholder="Search events"
              aria-label="Search run events"
              data-run-event-audit-search="true"
            />
            <select v-model="eventAuditActor" aria-label="Filter run event actor" data-run-event-audit-actor="true">
              <option value="">Any actor</option>
              <option v-for="actor in eventActorOptions" :key="actor" :value="actor">{{ actor }}</option>
            </select>
            <button
              class="event-audit-button"
              type="button"
              data-run-event-audit-export="true"
              :disabled="!filteredLedgerEvents.length"
              @click="downloadEventAuditExport"
            >
              <Download :size="12" />
              <span>Export JSON</span>
            </button>
            <button
              class="event-audit-button"
              type="button"
              data-run-event-audit-clear="true"
              :disabled="!hasEventAuditFilters && !eventAuditMessage"
              @click="clearEventAuditFilters"
            >
              <span>Reset</span>
            </button>
          </div>
          <p class="event-audit-status" data-run-event-audit-status="true">
            {{ eventAuditFilterSummary }}
            <template v-if="eventAuditMessage"> / {{ eventAuditMessage }}</template>
          </p>

          <section class="replay-lane" aria-label="Run diff timeline">
            <div class="replay-lane-head">
              <strong>REPLAY LANE</strong>
              <span>{{ replayTimelineSteps.length }} steps</span>
            </div>
            <div class="replay-steps">
              <button
                v-for="step in replayTimelineSteps"
                :key="step.id"
                class="replay-step"
                :class="{ active: step.event.id === selectedLedgerEvent?.id }"
                type="button"
                @click="selectReplayStep(step)"
              >
                <span class="replay-index">{{ step.indexLabel }}</span>
                <span class="replay-step-body">
                  <strong>{{ step.label }}</strong>
                  <small>{{ step.summary }}</small>
                  <span class="replay-delta-row">
                    <span v-for="chip in step.chips" :key="chip.key">{{ chip.label }}</span>
                  </span>
                </span>
              </button>
            </div>
          </section>

          <div v-if="filteredLedgerEvents.length" class="event-list">
            <button
              v-for="event in filteredLedgerEvents"
              :key="event.id"
              class="event-item"
              :class="[`kind-${eventKind(event)}`, { preview: event.isPreview, selected: event.id === selectedLedgerEvent?.id }]"
              type="button"
              @click="selectLedgerEvent(event)"
            >
              <span class="event-dot" />
              <span class="event-body">
                <span class="event-title">
                  <strong>{{ eventTypeLabel(event.eventType) }}</strong>
                  <time>{{ formatEventTime(event.createdAt) }}</time>
                </span>
                <span class="event-summary">{{ formatEventSummary(event) }}</span>
                <span v-if="eventLinkChips(event).length" class="event-link-row">
                  <span v-for="chip in eventLinkChips(event)" :key="chip.key" class="event-link-chip">
                    {{ chip.label }}
                  </span>
                </span>
                <small>
                  {{ event.actor || 'local-workbench' }}
                  <template v-if="event.branchId"> / {{ eventBranchTitle(event.branchId) }}</template>
                  <template v-if="event.isPreview"> / preview</template>
                </small>
              </span>
            </button>
          </div>
          <p v-else class="empty-copy" data-run-event-audit-empty="true">No matching run events.</p>
          <div v-if="ledgerRunId && ledgerEvents.length" class="event-pagination" data-run-events-pagination="true">
            <span>{{ ledgerEvents.length }}/{{ ledgerEventsTotal || ledgerEvents.length }} loaded</span>
            <button
              class="event-page-button"
              type="button"
              data-run-events-load-more="true"
              :disabled="!canLoadMoreLedgerEvents || ledgerBusy || ledgerEventsBusy || !canUseRunLedger"
              @click="loadMoreLedgerEvents"
            >
              <RefreshCw :size="12" />
              <span>{{ ledgerEventsBusy && canLoadMoreLedgerEvents ? 'Loading' : 'Load More Events' }}</span>
            </button>
          </div>

          <div v-if="selectedLedgerEvent" class="event-detail">
            <div class="event-detail-head">
              <div>
                <p class="eyebrow">EVENT DETAIL</p>
                <h3>{{ eventTypeLabel(selectedLedgerEvent.eventType) }}</h3>
              </div>
              <span :class="['status-pill', eventKind(selectedLedgerEvent)]">
                {{ selectedLedgerEvent.isPreview ? 'preview' : 'ledger' }}
              </span>
            </div>

            <p class="event-detail-summary">{{ formatEventSummary(selectedLedgerEvent) }}</p>

            <div v-if="eventCanOpenManifest(selectedLedgerEvent)" class="event-manifest-actions">
              <button class="manifest-action" type="button" @click="focusRunManifest(selectedLedgerEvent)">
                Open Replay Manifest
              </button>
            </div>

            <dl class="event-meta-grid">
              <div>
                <dt>Event ID</dt>
                <dd>{{ selectedLedgerEvent.id }}</dd>
              </div>
              <div>
                <dt>Actor</dt>
                <dd>{{ selectedLedgerEvent.actor || 'local-workbench' }}</dd>
              </div>
              <div>
                <dt>Branch</dt>
                <dd>{{ selectedLedgerEvent.branchId ? eventBranchTitle(selectedLedgerEvent.branchId) : 'run scope' }}</dd>
              </div>
              <div>
                <dt>Run</dt>
                <dd>{{ selectedLedgerEvent.runId || run.id }}</dd>
              </div>
            </dl>

            <section v-if="eventDecisionSnapshot(selectedLedgerEvent).length" class="decision-snapshot">
              <div class="decision-snapshot-head">
                <strong>Decision Snapshot</strong>
                <span>{{ eventDecisionStatusLabel(selectedLedgerEvent) }}</span>
              </div>
              <dl>
                <div v-for="item in eventDecisionSnapshot(selectedLedgerEvent)" :key="item.label">
                  <dt>{{ item.label }}</dt>
                  <dd>{{ item.value }}</dd>
                </div>
              </dl>
            </section>

            <div class="event-detail-sections">
              <section v-for="section in eventDetailSections(selectedLedgerEvent)" :key="section.key" class="event-detail-section">
                <strong>{{ section.label }}</strong>
                <div v-if="section.items.length" class="event-detail-items">
                  <button
                    v-for="item in section.items"
                    :key="`${section.key}-${item.id}`"
                    class="event-detail-token"
                    :class="{ focused: isFocusedToken(item), disabled: !item.canFocus }"
                    type="button"
                    :data-event-detail-token="item.token"
                    :disabled="!item.canFocus"
                    :title="item.canFocus ? `定位 ${item.label}` : '当前页面暂无可定位目标'"
                    @click="focusEventDetailToken(item)"
                  >
                    {{ item.label }}
                  </button>
                </div>
                <p v-else>暂无关联线索</p>
              </section>
            </div>

            <p v-if="inspectorFocusMessage" class="event-focus-message">{{ inspectorFocusMessage }}</p>

            <section v-if="focusedDossier" class="focus-dossier" data-inspector-dossier="true">
              <div class="focus-dossier-head">
                <div>
                  <p class="eyebrow">FOCUS DOSSIER</p>
                  <h3>{{ focusedDossier.title }}</h3>
                </div>
                <span class="status-pill">{{ focusedDossier.badge }}</span>
              </div>

              <p>{{ focusedDossier.summary }}</p>

              <dl v-if="focusedDossier.meta.length" class="focus-dossier-meta">
                <div v-for="item in focusedDossier.meta" :key="item.label">
                  <dt>{{ item.label }}</dt>
                  <dd>{{ item.value }}</dd>
                </div>
              </dl>

              <div v-if="focusedDossier.items.length" class="focus-dossier-links">
                <div
                  v-for="item in focusedDossier.items"
                  :key="item.key"
                  class="focus-dossier-link-row"
                >
                  <button
                    class="focus-dossier-link"
                    :class="{ active: isFocusedDossierItem(item), disabled: !item.canFocus }"
                    type="button"
                    :disabled="!item.canFocus"
                    @click="focusDossierItem(item)"
                  >
                    {{ item.label }}
                  </button>
                  <button
                    v-if="['artifact', 'gate', 'evidence', 'source', 'wiki', 'graph', 'timeline'].includes(item.targetType)"
                    class="focus-dossier-mcp-button"
                    type="button"
                    :disabled="!item.targetId"
                    @click.stop="copyFocusDossierMcpCall(item)"
                  >
                    <Clipboard :size="12" />
                    <span>Copy MCP</span>
                  </button>
                </div>
              </div>

              <p v-if="focusDossierMcpMessage" class="focus-dossier-mcp-message">
                {{ focusDossierMcpMessage }}
              </p>
              <div
                v-if="focusDossierMcpPreview"
                class="focus-dossier-mcp-preview"
                data-focus-dossier-mcp-preview="true"
              >
                <span>{{ focusDossierMcpPreview.uri }}</span>
                <pre>{{ focusDossierMcpArgsPreview }}</pre>
              </div>
            </section>
          </div>
        </section>

        <WorldlineEvidenceRail
          :evidence-refs="worldlineStore.evidenceRefs"
          :wiki-refs="worldlineStore.wikiRefs"
          :entity-refs="worldlineStore.entityRefs"
          :timeline-refs="worldlineStore.timelineRefs"
          :active-layer="activeEvidenceLayer"
          :active-item-id="activeEvidenceId"
          @focus-item="focusEvidenceRailItem"
        />

        <section class="rail-panel artifact-panel">
          <div class="panel-head">
            <p class="eyebrow">ARTIFACT RAIL</p>
            <span>{{ visibleArtifactDetails.length }} visible</span>
          </div>

          <div class="artifact-scope" aria-label="Artifact scope filters">
            <button
              v-for="scope in artifactScopeOptions"
              :key="scope.id"
              class="artifact-scope-button"
              :class="{ active: artifactScope === scope.id }"
              type="button"
              @click="artifactScope = scope.id"
            >
              <span>{{ scope.label }}</span>
              <small>{{ scope.count }}</small>
            </button>
          </div>

          <p v-if="artifactRailMessage" class="artifact-mcp-message">{{ artifactRailMessage }}</p>

          <div v-if="visibleArtifactDetails.length" class="artifact-list">
            <div
              v-for="artifact in visibleArtifactDetails"
              :key="artifact.id"
              class="artifact-row"
            >
              <button
                class="artifact-item"
                :class="{ focused: isArtifactFocused(artifact) }"
                type="button"
                :data-inspector-target="`artifact:${artifact.id}`"
                @click="focusArtifactRailItem(artifact)"
              >
                <span class="artifact-type">{{ artifact.type || 'artifact' }}</span>
                <strong>{{ artifact.label || artifact.id }}</strong>
                <small>{{ artifact.path || artifact.id }}</small>
                <em>
                  {{ artifact.toolName || artifact.toolCallId || 'unlinked tool' }}
                  <template v-if="artifact.branchId"> / {{ eventBranchTitle(artifact.branchId) }}</template>
                </em>
              </button>
              <button
                class="artifact-mcp-button"
                type="button"
                @click.stop="copyArtifactRailMcpCall(artifact)"
              >
                <Clipboard :size="12" />
                <span>Copy MCP</span>
              </button>
            </div>
          </div>

          <p v-else class="empty-copy">
            当前视角暂无产物。
          </p>
        </section>

        <section class="rail-panel trace-panel">
          <div class="panel-head">
            <p class="eyebrow">TOOL TRACE</p>
            <span>{{ activeToolTraces.length }} visible</span>
          </div>

          <article
            v-for="trace in activeToolTraces"
            :key="trace.id"
            class="trace-item"
            :class="{ focused: isToolTraceFocused(trace) }"
            :data-inspector-target="`tool:${trace.id}`"
            :data-inspector-permission-target="`permission:${trace.permission}`"
          >
            <div>
              <strong>{{ trace.name }}</strong>
              <small>{{ trace.permission }}</small>
            </div>
            <p>{{ trace.summary }}</p>
            <span :class="['status-pill', trace.status]">{{ trace.result }}</span>
          </article>

          <p v-if="!activeToolTraces.length" class="empty-copy">
            当前分支没有工具调用。计划和证据分支可以先审查，再进入工具执行。
          </p>
        </section>

        <section class="rail-panel gate-panel">
          <div class="panel-head">
            <p class="eyebrow">QUALITY GATES</p>
            <span>{{ visibleGateDetails.length }} visible</span>
          </div>

          <div class="gate-scope" aria-label="Quality gate scope filters">
            <button
              v-for="scope in gateScopeOptions"
              :key="scope.id"
              class="gate-scope-button"
              :class="{ active: gateScope === scope.id }"
              type="button"
              @click="gateScope = scope.id"
            >
              <span>{{ scope.label }}</span>
              <small>{{ scope.count }}</small>
            </button>
          </div>

          <div v-if="visibleGateDetails.length" class="gate-run-list">
            <p v-if="gatePanelMessage" class="artifact-mcp-message gate-mcp-message">{{ gatePanelMessage }}</p>
            <div
              v-for="gate in visibleGateDetails"
              :key="gate.id"
              class="gate-run-row"
            >
              <button
                :class="['gate-run-item', gate.status, { focused: isGateFocused(gate) }]"
                type="button"
                :data-inspector-target="`gate:${gate.id}`"
                @click="focusGateRunItem(gate)"
              >
              <span class="gate-run-status">{{ gate.status || 'pending' }}</span>
              <strong>{{ gate.label || gate.id }}</strong>
              <p>{{ gate.summary || '等待质量门详情。' }}</p>
              <dl class="gate-run-meta">
                <div>
                  <dt>Value</dt>
                  <dd>{{ gate.value || 'n/a' }}</dd>
                </div>
                <div>
                  <dt>Threshold</dt>
                  <dd>{{ gate.threshold || 'not set' }}</dd>
                </div>
                <div>
                  <dt>Input</dt>
                  <dd>{{ gate.input || 'not recorded' }}</dd>
                </div>
                <div>
                  <dt>Artifacts</dt>
                  <dd>{{ joinList(gate.artifactIds || []) }}</dd>
                </div>
              </dl>
              <div class="gate-support-strip" :aria-label="`Support coverage for ${gate.label || gate.id}`">
                <span>Evidence {{ gateSupportSummary(gate).evidenceIds.length }}</span>
                <span>Source {{ gateSupportSummary(gate).sourceIds.length }}</span>
                <span>Graph {{ gateSupportSummary(gate).entityIds.length }}</span>
                <span>Time {{ gateSupportSummary(gate).timelineIds.length }}</span>
              </div>
              <em>{{ gate.remediation || gate.failureReason || 'No action required.' }}</em>
              </button>
              <button
                class="gate-mcp-button"
                type="button"
                @click.stop="copyGateRunMcpCall(gate)"
              >
                <Clipboard :size="12" />
                <span>Copy MCP</span>
              </button>
            </div>
          </div>

          <p v-else class="empty-copy">
            当前视角暂无质量门。
          </p>
        </section>

        <section class="rail-panel skill-panel">
          <div class="panel-head">
            <p class="eyebrow">SKILL GENOME</p>
            <span>{{ agentRun.skillProposals.length }} candidates</span>
          </div>

          <article
            v-for="skill in agentRun.skillProposals"
            :key="skill.id"
            class="skill-item"
            :class="{ focused: isSkillFocused(skill) }"
            role="button"
            tabindex="0"
            :data-inspector-target="`skill:${skill.id}`"
            @click="focusSkillCard(skill)"
            @keydown.enter.prevent="focusSkillCard(skill)"
            @keydown.space.prevent="focusSkillCard(skill)"
          >
            <div>
              <strong>{{ skill.name }}</strong>
              <span>{{ Math.round(skill.evalScore * 100) }}%</span>
            </div>
            <p>{{ skill.trigger }}</p>
            <div class="skill-genome-chips" :aria-label="`Genome metadata for ${skill.name}`">
              <span v-for="chip in skillGenomeChips(skill)" :key="chip.key">
                {{ chip.label }}
              </span>
            </div>
            <div class="skill-meta">
              <small>{{ joinList(skill.requiredPermissions || []) }}</small>
              <button
                class="skill-action"
                type="button"
                :disabled="!canUseRunLedger || ledgerBusy"
                @click.stop="submitSkillProposal(skill)"
              >
                <Send :size="14" />
                <span>提交候选</span>
              </button>
            </div>
          </article>
        </section>
      </aside>
    </main>
    <div
      v-if="detailModalOpen"
      class="detail-modal-backdrop"
      data-detail-modal="true"
      @click.self="closeDetailModal"
    >
      <section class="detail-modal" role="dialog" aria-modal="true" :aria-label="detailModalTitle">
        <div class="detail-modal-head">
          <div>
            <p class="eyebrow">后端详情</p>
            <strong>{{ detailModalTitle }}</strong>
            <span v-if="detailModalSubtitle">{{ detailModalSubtitle }}</span>
          </div>
          <button type="button" @click="closeDetailModal">关闭</button>
        </div>
        <pre>{{ detailModalBody }}</pre>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { CheckCircle2, Clipboard, Download, Eye, RefreshCw, Save, Send } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'
import { useWorldlineContextStore } from '@/stores/worldlineContext'
import { worldlineRunApi } from '@/apis/worldline_api'
import WorldlineBranchCanvas from '@/components/worldline/WorldlineBranchCanvas.vue'
import WorldlineBranchDetailPanel from '@/components/worldline/WorldlineBranchDetailPanel.vue'
import WorldlineEvidenceRail from '@/components/worldline/WorldlineEvidenceRail.vue'
import WorldlineTimelineScrubber from '@/components/worldline/WorldlineTimelineScrubber.vue'
import { AGENT_WORKBENCH_PROTOCOL, createAgentWorkbenchRun } from '@/data/worldline/agentWorkbench'

const worldlineStore = useWorldlineContextStore()
const userStore = useUserStore()

const LEDGER_RUN_PAGE_SIZE = 8
const LEDGER_EVENT_PAGE_SIZE = 6
const agentRun = ref(createAgentWorkbenchRun())
const questionDraft = ref(agentRun.value.run.goal)
const protocolLabel = AGENT_WORKBENCH_PROTOCOL.replace('worldline-', '')
const ledgerRunId = ref('')
const ledgerEvents = ref([])
const ledgerEventsTotal = ref(0)
const ledgerEventsBusy = ref(false)
const ledgerRunList = ref([])
const ledgerRunListTotal = ref(0)
const ledgerRunListMessage = ref('')
const ledgerRunListBusy = ref(false)
const ledgerRunQuery = ref('')
const ledgerRunStatus = ref('')
const ledgerRunThemeId = ref('')
const ledgerRunCreatedBy = ref('')
const selectedLedgerRunIds = ref([])
const runCompareBusy = ref(false)
const runCompareTarget = ref('')
const runCompareResult = ref(null)
const runCompareMessage = ref('')
const runMaintenanceTitle = ref('')
const runMaintenanceBusy = ref(false)
const runMaintenanceTarget = ref('')
const runMaintenanceMessage = ref('')
const ledgerBusy = ref(false)
const ledgerError = ref('')
const ledgerMessage = ref('本地预览中；管理员登录后可保存到后端 run ledger。')
const activeEventFilter = ref('all')
const eventAuditQuery = ref('')
const eventAuditActor = ref('')
const eventAuditMessage = ref('')
const artifactScope = ref('branch')
const gateScope = ref('branch')
const artifactRegistryFilter = ref('all')
const selectedEventId = ref('')
const inspectorFocus = ref({ type: '', id: '', token: '', layer: '' })
const inspectorFocusMessage = ref('')
const exportPreviewOpen = ref(false)
const exportMessage = ref('')
const artifactSaveBusy = ref(false)
const artifactRegistryMessage = ref('')
const savedReplayArtifacts = ref([])
const mcpReadMessage = ref('')
const artifactRailMessage = ref('')
const gatePanelMessage = ref('')
const focusDossierMcpMessage = ref('')
const runManifestMessage = ref('')
const runManifestBusy = ref(false)
const runManifestError = ref('')
const backendRunManifest = ref(null)
const resourceDrilldownBusy = ref(false)
const resourceDrilldownTarget = ref('')
const resourceDrilldownResult = ref(null)
const resourceDrilldownMessage = ref('')
const resourceDetailSaveBusy = ref(false)
const resourceDetailReplayBusyId = ref('')
const resourceDetailCompareBusyId = ref('')
const resourceDetailCompareResult = ref(null)
const resourceDetailCompareMessage = ref('')
const resourceDetailDiffSaveBusy = ref(false)
const detailModalOpen = ref(false)
const detailModalTitle = ref('')
const detailModalSubtitle = ref('')
const detailModalBody = ref('')
const lastMcpCall = ref(null)
const handoffPreviewOpen = ref(false)
const handoffMessage = ref('')
const handoffSaveBusy = ref(false)

const run = computed(() => agentRun.value.run || {})
const canUseRunLedger = computed(() => userStore.isAdmin)
const ledgerState = computed(() => {
  if (ledgerError.value) return 'failed'
  if (ledgerRunId.value) return 'synced'
  if (!userStore.isLoggedIn) return 'local'
  if (!canUseRunLedger.value) return 'locked'
  return 'ready'
})
const ledgerStateLabel = computed(() => {
  const labels = {
    synced: '已同步',
    failed: '同步失败',
    locked: '需要管理员',
    ready: '可保存',
    local: '本地预览'
  }
  return labels[ledgerState.value] || '本地预览'
})
const ledgerStateClass = computed(() => `is-${ledgerState.value}`)
const visibleLedgerRuns = computed(() => ledgerRunList.value)
const canLoadMoreLedgerRuns = computed(() => ledgerRunListTotal.value > ledgerRunList.value.length)
const canLoadMoreLedgerEvents = computed(() => ledgerEventsTotal.value > ledgerEvents.value.length)
const selectedLedgerRunSet = computed(() => new Set(selectedLedgerRunIds.value.map(String)))
const selectedLedgerRuns = computed(() =>
  ledgerRunList.value.filter((item) => selectedLedgerRunSet.value.has(String(item.id || '')))
)
const selectedLedgerRunCount = computed(() => selectedLedgerRuns.value.length)
const selectedArchiveRuns = computed(() => selectedLedgerRuns.value.filter((item) => item.status !== 'archived'))
const selectedRestoreRuns = computed(() => selectedLedgerRuns.value.filter((item) => item.status === 'archived'))
const hasRunSelectorFilters = computed(() =>
  Boolean(ledgerRunQuery.value || ledgerRunStatus.value || ledgerRunThemeId.value || ledgerRunCreatedBy.value)
)
const runCompareTimeline = computed(() =>
  (runCompareResult.value?.timeline || []).filter((item) => Number(item.totalDelta || 0) > 0)
)
const runCompareTotalDelta = computed(() =>
  runCompareResult.value
    ? Number(runCompareResult.value.summary?.added || 0) +
      Number(runCompareResult.value.summary?.removed || 0) +
      Number(runCompareResult.value.summary?.changed || 0)
    : 0
)
const resourceDetailCompareTotalDelta = computed(() =>
  resourceDetailCompareResult.value
    ? Number(resourceDetailCompareResult.value.summary?.added || 0) +
      Number(resourceDetailCompareResult.value.summary?.removed || 0) +
      Number(resourceDetailCompareResult.value.summary?.changed || 0)
    : 0
)
const runCompareTitle = computed(() => {
  if (!runCompareResult.value) return '选择一个已保存任务进行对比'
  const left = runCompareResult.value.left?.title || runCompareResult.value.left?.id || '左侧任务'
  const right = runCompareResult.value.right?.title || runCompareResult.value.right?.id || '右侧任务'
  return `${left} 对比 ${right}`
})
const runSelectorMessage = computed(() => {
  if (ledgerRunListMessage.value) return ledgerRunListMessage.value
  if (!canUseRunLedger.value) return '需要管理员权限才能读取后端任务。'
  if (!ledgerRunList.value.length) return '需要切换上下文时，先刷新后端已保存任务。'
  return `已载入 ${ledgerRunList.value.length}/${ledgerRunListTotal.value || ledgerRunList.value.length} 个后端任务。`
})
const activeBranchId = computed(() => worldlineStore.activeBranch?.id || worldlineStore.activeBranchId)
const activeEpisodes = computed(() =>
  agentRun.value.episodes.filter((episode) => episode.branchId === activeBranchId.value)
)
const activeToolTraces = computed(() =>
  agentRun.value.toolTraces.filter((trace) => trace.branchId === activeBranchId.value)
)

const uniqueStrings = (items = []) => Array.from(new Set((items || []).filter(Boolean).map(String)))
const runSummaryMeta = (item = {}) => {
  const counts = item.counts || {}
  return [
    item.id,
    item.status || '',
    `${counts.branches || 0} 分支`,
    `${counts.events || 0} 事件`,
    `${counts.artifacts || 0} 证据`
  ]
    .filter(Boolean)
    .join(' / ')
}
const MCP_RUN_ARTIFACT_TOOL = 'worldline.inspect_run_artifacts'
const MCP_RUN_GATE_TOOL = 'worldline.inspect_run_gates'
const MCP_RUN_EVIDENCE_TOOL = 'worldline.inspect_run_evidence'
const MCP_RUN_KNOWLEDGE_TOOL = 'worldline.inspect_run_knowledge'
const MCP_RUN_MANIFEST_TOOL = 'worldline.inspect_run_manifest'
const RUN_MANIFEST_SECTION_LABELS = {
  artifacts: 'Artifacts',
  gates: 'Gates',
  evidence: 'Evidence',
  sources: 'Sources',
  wiki: 'Wiki',
  graph: 'Graph',
  timeline: 'Time'
}
const AGENT_HANDOFF_PROTOCOL = 'worldline-agent-handoff@0.1'
const toolTraceArtifactIds = (trace = {}) =>
  uniqueStrings([
    ...(Array.isArray(trace.artifactIds) ? trace.artifactIds : []),
    ...(Array.isArray(trace.artifacts) ? trace.artifacts.map((artifact) => artifact?.id) : [])
  ])
const normalizeArtifactDetail = (artifact = {}, trace = {}) => {
  const artifactId = String(artifact.id || artifact.artifactId || artifact.path || artifact.uri || '').trim()
  return {
    id: artifactId,
    label: artifact.label || artifact.title || artifactId,
    type: artifact.type || artifact.kind || 'artifact',
    path: artifact.path || artifact.uri || '',
    summary: artifact.summary || artifact.description || '',
    toolCallId: artifact.toolCallId || artifact.tool_call_id || trace.id || '',
    toolName: artifact.toolName || artifact.tool_name || trace.name || '',
    branchId: artifact.branchId || artifact.branch_id || trace.branchId || '',
    permission: artifact.permission || trace.permission || ''
  }
}
const registryArtifactPath = (artifact = {}) =>
  artifact.path || `worldline-run-ledger://${artifact.runId || ledgerRunId.value || run.value.id}/artifacts/${artifact.id}`
const normalizeRegistryArtifactDetail = (artifact = {}) =>
  normalizeArtifactDetail({
    ...artifact,
    type: artifact.kind || artifact.type || 'replay_export',
    path: registryArtifactPath(artifact),
    summary: artifact.summary || 'Registered replay artifact.'
  })
const summarizeToolTraces = (traces = []) =>
  traces.map((trace) => ({
    id: trace.id,
    branchId: trace.branchId || '',
    name: trace.name,
    status: trace.status,
    permission: trace.permission,
    summary: trace.summary,
    result: trace.result,
    artifactIds: toolTraceArtifactIds(trace),
    failureReason: trace.failureReason || ''
  }))
const summarizeArtifactsForTraces = (traces = []) => {
  const details = []
  traces.forEach((trace) => {
    const artifacts = Array.isArray(trace.artifacts) ? trace.artifacts : []
    toolTraceArtifactIds(trace).forEach((artifactId) => {
      const artifact = artifacts.find((item) => item?.id === artifactId) || {}
      details.push(normalizeArtifactDetail({ ...artifact, id: artifactId }, trace))
    })
  })
  return details
}
const normalizeGateDetail = (gate = {}) => {
  const gateId = String(gate.id || gate.gateId || gate.gate_id || gate.label || '').trim()
  return {
    id: gateId,
    label: gate.label || gate.name || gateId,
    status: gate.status || 'pending',
    value: gate.value || gate.score || '',
    summary: gate.summary || gate.description || '',
    branchId: gate.branchId || gate.branch_id || '',
    threshold: gate.threshold || gate.criteria || '',
    input: gate.input || gate.inputSummary || gate.input_summary || '',
    toolCallIds: uniqueStrings(gate.toolCallIds || gate.tool_call_ids || []),
    artifactIds: uniqueStrings(gate.artifactIds || gate.artifact_ids || []),
    failureReason: gate.failureReason || gate.failure_reason || '',
    remediation: gate.remediation || gate.fix || gate.nextStep || gate.next_step || ''
  }
}
const summarizeGatesForIds = (gateIds = []) =>
  uniqueStrings(gateIds).map((gateId) => {
    const gate = (agentRun.value.gateResults || []).find((item) => item.id === gateId) || {}
    return normalizeGateDetail({ ...gate, id: gateId, status: gate.status || 'linked' })
  })

const previewLedgerEvents = computed(() => {
  const currentRun = run.value
  const activeBranch = worldlineStore.activeBranch
  const toolCount = activeToolTraces.value.length
  const skillCount = agentRun.value.skillProposals.length
  const createdAt = currentRun.createdAt || new Date().toISOString()
  const runToolTraces = agentRun.value.toolTraces || []
  const runGateIds = uniqueStrings((agentRun.value.gateResults || []).map((gate) => gate.id))
  const events = [
    {
      id: 'preview-run-created',
      runId: currentRun.id,
      eventType: 'run.previewed',
      actor: 'local-workbench',
      summary: {
        title: currentRun.title,
        branch_count: worldlineStore.branchCount,
        episode_count: agentRun.value.episodes.length,
        skill_proposal_count: agentRun.value.skillProposals.length,
        branch_ids: worldlineStore.branches.map((branch) => branch.id).filter(Boolean),
        episodeIds: agentRun.value.episodes.map((episode) => episode.id).filter(Boolean),
        skillProposalIds: agentRun.value.skillProposals.map((skill) => skill.id).filter(Boolean),
        evidenceIds: worldlineStore.evidenceRefs.map((item) => item.evidenceId || item.id).filter(Boolean),
        toolCallIds: runToolTraces.map((trace) => trace.id).filter(Boolean),
        temporalFactIds: worldlineStore.timelineRefs.map((item) => item.id).filter(Boolean),
        requiredPermissions: uniqueStrings(runToolTraces.map((trace) => trace.permission)),
        gateResultIds: runGateIds,
        artifactIds: uniqueStrings(runToolTraces.flatMap(toolTraceArtifactIds)),
        toolDetails: summarizeToolTraces(runToolTraces),
        gateDetails: summarizeGatesForIds(runGateIds),
        artifactDetails: summarizeArtifactsForTraces(runToolTraces)
      },
      createdAt,
      isPreview: true
    }
  ]

  if (activeBranch) {
    const branchToolTraces = runToolTraces.filter((trace) => (activeBranch.toolCallIds || []).includes(trace.id))
    const branchGateIds = uniqueStrings([
      ...(activeBranch.gateResultIds || []),
      ...activeEpisodes.value.flatMap((episode) => episode.gateResults || [])
    ])
    const branchArtifactIds = uniqueStrings([
      ...branchToolTraces.flatMap(toolTraceArtifactIds),
      ...activeEpisodes.value.flatMap((episode) => episode.artifactIds || [])
    ])
    events.push({
      id: `preview-branch-${activeBranch.id}`,
      runId: currentRun.id,
      branchId: activeBranch.id,
      eventType: 'branch.focused',
      actor: activeBranch.stageLabel || 'planner',
      summary: {
        status: activeBranch.status || activeBranch.quality?.status || 'inspectable',
        reason: activeBranch.nextStepTitle || activeBranch.choiceReason || '',
        branch_title: activeBranch.title || activeBranch.id,
        branch_type: activeBranch.branchType || activeBranch.choiceLabel || '',
        quality_status: activeBranch.quality?.status || activeBranch.status || '',
        score: activeBranch.score ?? '',
        evidenceIds: activeBranch.evidenceIds || activeBranch.evidenceRefs?.map((item) => item.evidenceId || item.id) || [],
        toolCallIds: activeBranch.toolCallIds || [],
        temporalFactIds: activeBranch.temporalFactIds || activeBranch.timelineRefs?.map((item) => item.id) || [],
        requiredPermissions: uniqueStrings(branchToolTraces.map((trace) => trace.permission)),
        gateResultIds: branchGateIds,
        artifactIds: branchArtifactIds,
        toolDetails: summarizeToolTraces(branchToolTraces),
        gateDetails: summarizeGatesForIds(branchGateIds),
        artifactDetails: summarizeArtifactsForTraces(branchToolTraces)
      },
      createdAt,
      isPreview: true
    })
  }

  if (toolCount) {
    events.push({
      id: `preview-tool-${activeBranchId.value}`,
      runId: currentRun.id,
      branchId: activeBranchId.value,
      eventType: 'tool.pending',
      actor: 'executor',
      summary: {
        tool_count: toolCount,
        status: 'approval_required',
        toolCallIds: activeToolTraces.value.map((trace) => trace.id).filter(Boolean),
        requiredPermissions: uniqueStrings(activeToolTraces.value.map((trace) => trace.permission)),
        artifactIds: uniqueStrings(activeToolTraces.value.flatMap(toolTraceArtifactIds)),
        toolDetails: summarizeToolTraces(activeToolTraces.value),
        artifactDetails: summarizeArtifactsForTraces(activeToolTraces.value)
      },
      createdAt,
      isPreview: true
    })
  }

  if (skillCount) {
    events.push({
      id: 'preview-skill-candidates',
      runId: currentRun.id,
      branchId: activeBranchId.value,
      eventType: 'skill.candidate',
      actor: 'evolution',
      summary: {
        skill_count: skillCount,
        status: 'candidate',
        requiredPermissions: Array.from(
          new Set(agentRun.value.skillProposals.flatMap((skill) => skill.requiredPermissions || []))
        ),
        evidenceRunIds: Array.from(
          new Set(agentRun.value.skillProposals.flatMap((skill) => skill.evidenceRunIds || []))
        ),
        steps: uniqueStrings(agentRun.value.skillProposals.flatMap((skill) => skill.steps || []))
      },
      createdAt,
      isPreview: true
    })
  }

  return events
})
const visibleLedgerEvents = computed(() => {
  const events = ledgerEvents.value.length ? ledgerEvents.value : previewLedgerEvents.value
  return [...events].sort((left, right) => {
    const leftTime = Date.parse(left.createdAt || '') || 0
    const rightTime = Date.parse(right.createdAt || '') || 0
    return rightTime - leftTime
  })
})
const eventKind = (event = {}) => {
  const [kind = 'event'] = String(event.eventType || 'event').split('.')
  return ['run', 'branch', 'tool', 'skill', 'artifact'].includes(kind) ? kind : 'event'
}
const ledgerEventFilters = computed(() => {
  const events = visibleLedgerEvents.value
  const baseFilters = [
    { id: 'all', label: 'All' },
    { id: 'run', label: 'Run' },
    { id: 'branch', label: 'Branch' },
    { id: 'tool', label: 'Tool' },
    { id: 'skill', label: 'Skill' },
    { id: 'artifact', label: 'Artifact' }
  ]
  return baseFilters.map((filter) => ({
    ...filter,
    count: filter.id === 'all' ? events.length : events.filter((event) => eventKind(event) === filter.id).length
  }))
})
const eventActorOptions = computed(() =>
  Array.from(
    new Set(visibleLedgerEvents.value.map((event) => String(event.actor || 'local-workbench').trim()).filter(Boolean))
  ).sort((left, right) => left.localeCompare(right))
)
const hasEventAuditFilters = computed(() =>
  activeEventFilter.value !== 'all' || Boolean(eventAuditQuery.value.trim()) || Boolean(eventAuditActor.value)
)
const eventAuditSearchText = (event = {}) =>
  [
    event.id,
    event.runId,
    event.branchId,
    event.eventType,
    event.actor || 'local-workbench',
    formatEventSummary(event),
    JSON.stringify(event.summary || {})
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
const filteredLedgerEvents = computed(() => {
  const query = eventAuditQuery.value.trim().toLowerCase()
  return visibleLedgerEvents.value.filter((event) => {
    if (activeEventFilter.value !== 'all' && eventKind(event) !== activeEventFilter.value) return false
    if (eventAuditActor.value && String(event.actor || 'local-workbench') !== eventAuditActor.value) return false
    if (query && !eventAuditSearchText(event).includes(query)) return false
    return true
  })
})
const eventAuditFilterSummary = computed(() => {
  const loaded = visibleLedgerEvents.value.length
  const matched = filteredLedgerEvents.value.length
  const total = ledgerEventsTotal.value || loaded
  return `${matched}/${loaded} matched${total > loaded ? ` / ${total} total` : ''}`
})
const selectedLedgerEvent = computed(() =>
  filteredLedgerEvents.value.find((event) => event.id === selectedEventId.value) ||
  filteredLedgerEvents.value[0] ||
  (hasEventAuditFilters.value ? null : visibleLedgerEvents.value[0]) ||
  null
)
const chronologicalLedgerEvents = computed(() => {
  const events = visibleLedgerEvents.value
  const eventTimes = events
    .map((event) => Date.parse(event.createdAt || '') || 0)
    .filter(Boolean)
  const hasDistinctTimes = new Set(eventTimes).size > 1
  return hasDistinctTimes ? [...events].reverse() : events
})
const evidenceRailFocusTypes = new Set(['evidence', 'wiki', 'graph', 'timeline'])
const activeEvidenceLayer = computed(() =>
  evidenceRailFocusTypes.has(inspectorFocus.value.type)
    ? inspectorFocus.value.layer || inspectorFocus.value.type
    : ''
)
const activeEvidenceId = computed(() =>
  evidenceRailFocusTypes.has(inspectorFocus.value.type) ? inspectorFocus.value.id : ''
)
const activeTimelineId = computed(() => inspectorFocus.value.type === 'timeline' ? inspectorFocus.value.id : '')
const focusedDossier = computed(() => buildFocusedDossier(inspectorFocus.value))

const hydrateRun = (nextRun) => {
  agentRun.value = nextRun
  worldlineStore.hydrate(nextRun)
}

const normalizeErrorMessage = (error) => {
  if (!error) return '未知错误'
  return error?.message || String(error)
}

const formatSummaryKey = (key = '') =>
  String(key)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())

const formatSummaryValue = (value) => {
  if (value === undefined || value === null || value === '') return ''
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

const formatEventSummary = (event = {}) => {
  const summary = event.summary
  if (!summary) return '事件已记录，等待更多摘要字段。'
  if (typeof summary === 'string') return summary

  const preferred = [
    summary.title ? `Run: ${summary.title}` : '',
    summary.branch_title ? `Branch: ${summary.branch_title}` : '',
    summary.branch_count !== undefined ? `${summary.branch_count} branches` : '',
    summary.tool_count !== undefined ? `${summary.tool_count} tool calls` : '',
    summary.skill_count !== undefined ? `${summary.skill_count} skill candidates` : '',
    summary.status ? `Status: ${summary.status}` : '',
    summary.quality_status ? `Quality: ${summary.quality_status}` : '',
    summary.reason || '',
    summary.name ? `Skill: ${summary.name}` : '',
    summary.skill_id ? `Skill ID: ${summary.skill_id}` : ''
  ].filter(Boolean)

  if (preferred.length) {
    return preferred.join(' / ')
  }

  return Object.entries(summary)
    .map(([key, value]) => {
      const formattedValue = formatSummaryValue(value)
      return formattedValue ? `${formatSummaryKey(key)}: ${formattedValue}` : ''
    })
    .filter(Boolean)
    .join(' / ') || '事件已记录。'
}

const countList = (value) => Array.isArray(value) ? value.filter(Boolean).length : 0
const formatEpisodeCost = (cost = {}) => {
  if (!cost || typeof cost !== 'object') return 'not recorded'
  const parts = []
  if (cost.tokens !== undefined && cost.tokens !== null) parts.push(`${cost.tokens} tokens`)
  if (cost.ms !== undefined && cost.ms !== null) parts.push(`${cost.ms} ms`)
  return parts.join(' / ') || 'not recorded'
}
const episodeReplaySummary = (episode = {}) =>
  `${countList(episode.toolCalls)} tools / ${countList(episode.gateResults)} gates / ${countList(episode.artifactIds)} artifacts`
const episodeReplayChips = (episode = {}) => [
  { key: 'diffs', label: 'Diffs', value: countList(episode.diffs) },
  { key: 'screenshots', label: 'Screenshots', value: countList(episode.screenshots) },
  { key: 'cost', label: 'Cost', value: formatEpisodeCost(episode.cost) }
].filter((chip) => chip.key === 'cost' || chip.value > 0)
const skillGenomeChips = (skill = {}) => [
  { key: 'version', label: skill.version || 'candidate' },
  { key: 'gates', label: `Gates ${countList(skill.gateResultIds)}` },
  { key: 'artifacts', label: `Artifacts ${countList(skill.artifactIds)}` },
  { key: 'criteria', label: `Criteria ${countList(skill.acceptanceCriteria)}` }
].filter((chip) => chip.label)

const eventLinkChips = (event = {}) => {
  const summary = event.summary || {}
  const chips = [
    { key: 'branch', label: `Branch ${countList(summary.branch_ids)}`, count: countList(summary.branch_ids) },
    { key: 'episode', label: `Episode ${summary.episode_count ?? countList(summary.episodeIds)}`, count: summary.episode_count ?? countList(summary.episodeIds) },
    { key: 'skill', label: `Skill ${summary.skill_proposal_count ?? countList(summary.skillProposalIds)}`, count: summary.skill_proposal_count ?? countList(summary.skillProposalIds) },
    { key: 'evidence', label: `Evidence ${countList(summary.evidenceIds)}`, count: countList(summary.evidenceIds) },
    { key: 'tool', label: `Tool ${countList(summary.toolCallIds)}`, count: countList(summary.toolCallIds) },
    { key: 'timeline', label: `Timeline ${countList(summary.temporalFactIds)}`, count: countList(summary.temporalFactIds) },
    { key: 'gate', label: `Gate ${countList(summary.gateResultIds)}`, count: countList(summary.gateResultIds) },
    { key: 'artifact', label: `Artifact ${countList(summary.artifactIds)}`, count: countList(summary.artifactIds) },
    {
      key: 'permission',
      label: `Permission ${countList(summary.requiredPermissions)}`,
      count: countList(summary.requiredPermissions)
    },
    { key: 'run-evidence', label: `Run Evidence ${countList(summary.evidenceRunIds)}`, count: countList(summary.evidenceRunIds) }
  ]
  return chips.filter((chip) => chip.count > 0)
}

const replayStepChips = (event = {}) => {
  const summary = event.summary || {}
  const chips = [
    { key: 'branch', label: `Branch ${countList(summary.branch_ids) || (event.branchId ? 1 : 0)}`, count: countList(summary.branch_ids) || (event.branchId ? 1 : 0) },
    { key: 'episode', label: `Episode ${summary.episode_count ?? countList(summary.episodeIds)}`, count: summary.episode_count ?? countList(summary.episodeIds) },
    { key: 'skill', label: `Skill ${summary.skill_proposal_count ?? summary.skill_count ?? countList(summary.skillProposalIds)}`, count: summary.skill_proposal_count ?? summary.skill_count ?? countList(summary.skillProposalIds) },
    { key: 'evidence', label: `Evidence ${summary.evidence_count ?? countList(summary.evidenceIds)}`, count: summary.evidence_count ?? countList(summary.evidenceIds) },
    { key: 'tool', label: `Tool ${summary.tool_count ?? countList(summary.toolCallIds)}`, count: summary.tool_count ?? countList(summary.toolCallIds) },
    { key: 'gate', label: `Gate ${countList(summary.gateResultIds)}`, count: countList(summary.gateResultIds) },
    { key: 'artifact', label: `Artifact ${countList(summary.artifactIds)}`, count: countList(summary.artifactIds) },
    { key: 'time', label: `Time ${summary.temporal_fact_count ?? countList(summary.temporalFactIds)}`, count: summary.temporal_fact_count ?? countList(summary.temporalFactIds) },
    { key: 'permission', label: `Permission ${countList(summary.requiredPermissions)}`, count: countList(summary.requiredPermissions) }
  ]
  return chips.filter((chip) => Number(chip.count) > 0)
}

const replayStepSummary = (event = {}) => {
  const summary = event.summary || {}
  const branchLabel = event.branchId ? eventBranchTitle(event.branchId) : summary.branch_title || ''
  const status = summary.status || summary.quality_status || eventKind(event)
  return [branchLabel, status, summary.reason || summary.title || 'run delta']
    .filter(Boolean)
    .join(' / ')
}

const replayTimelineSteps = computed(() =>
  chronologicalLedgerEvents.value.map((event, index) => ({
    id: `replay-step-${event.id || index}`,
    event,
    index: index + 1,
    indexLabel: String(index + 1).padStart(2, '0'),
    label: eventTypeLabel(event.eventType),
    summary: replayStepSummary(event),
    chips: replayStepChips(event)
  }))
)

const cloneSerializable = (value, fallback = null) => {
  try {
    return JSON.parse(JSON.stringify(value ?? fallback))
  } catch {
    return fallback
  }
}

const summarizeBranchForExport = (branch = {}) => ({
  id: branch.id,
  title: branch.title,
  status: branch.status || branch.quality?.status || '',
  choiceLabel: branch.choiceLabel || '',
  score: branch.score ?? '',
  evidenceIds: cloneSerializable(branch.evidenceIds || [], []),
  toolCallIds: cloneSerializable(branch.toolCallIds || [], []),
  gateResultIds: cloneSerializable(branch.gateResultIds || [], []),
  artifactIds: cloneSerializable(branch.artifactIds || [], []),
  temporalFactIds: cloneSerializable(branch.temporalFactIds || [], [])
})

const createReplayExportArtifact = () => {
  const currentRun = run.value || {}
  const selectedEvent = selectedLedgerEvent.value
  const artifacts = dedupeArtifacts(summarizeArtifactsForTraces(agentRun.value.toolTraces || []))
  const replayTimeline = replayTimelineSteps.value.map((step) => ({
    id: step.id,
    index: step.index,
    label: step.label,
    summary: step.summary,
    eventId: step.event.id,
    eventType: step.event.eventType,
    branchId: step.event.branchId || '',
    chips: step.chips.map((chip) => chip.label)
  }))

  return {
    protocol: AGENT_WORKBENCH_PROTOCOL,
    exportedAt: new Date().toISOString(),
    run: {
      id: currentRun.id || ledgerRunId.value || 'local-preview',
      title: currentRun.title || 'Agent Workbench',
      goal: currentRun.goal || '',
      status: currentRun.status || ledgerState.value,
      ledgerRunId: ledgerRunId.value || '',
      branchCount: worldlineStore.branchCount,
      episodeCount: agentRun.value.episodes.length,
      toolCount: agentRun.value.toolTraces.length,
      gateCount: agentRun.value.gateResults.length,
      artifactCount: artifacts.length,
      skillCount: agentRun.value.skillProposals.length
    },
    selectedEvent: selectedEvent
      ? {
          id: selectedEvent.id,
          runId: selectedEvent.runId || currentRun.id || '',
          eventType: selectedEvent.eventType || '',
          label: eventTypeLabel(selectedEvent.eventType),
          actor: selectedEvent.actor || 'local-workbench',
          branchId: selectedEvent.branchId || '',
          branchTitle: selectedEvent.branchId ? eventBranchTitle(selectedEvent.branchId) : '',
          createdAt: selectedEvent.createdAt || '',
          summaryText: formatEventSummary(selectedEvent),
          summary: cloneSerializable(selectedEvent.summary || {}, {})
        }
      : null,
    focus: cloneSerializable(inspectorFocus.value, {}),
    focusedDossier: cloneSerializable(focusedDossier.value, null),
    replayTimeline,
    counts: {
      branches: worldlineStore.branchCount,
      episodes: agentRun.value.episodes.length,
      tools: agentRun.value.toolTraces.length,
      gates: agentRun.value.gateResults.length,
      artifacts: artifacts.length,
      skills: agentRun.value.skillProposals.length,
      evidence: worldlineStore.evidenceRefs.length,
      wiki: worldlineStore.wikiRefs.length,
      graph: worldlineStore.entityRefs.length,
      timeline: worldlineStore.timelineRefs.length
    },
    worldline: {
      branches: worldlineStore.branches.map(summarizeBranchForExport),
      evidenceRefs: cloneSerializable(worldlineStore.evidenceRefs, []),
      wikiRefs: cloneSerializable(worldlineStore.wikiRefs, []),
      entityRefs: cloneSerializable(worldlineStore.entityRefs, []),
      timelineRefs: cloneSerializable(worldlineStore.timelineRefs, [])
    },
    agent: {
      episodes: cloneSerializable(agentRun.value.episodes, []),
      toolTraces: cloneSerializable(agentRun.value.toolTraces, []),
      gateResults: cloneSerializable(agentRun.value.gateResults, []),
      artifacts: cloneSerializable(artifacts, []),
      skillProposals: cloneSerializable(agentRun.value.skillProposals, [])
    }
  }
}

const replayExportArtifact = computed(() => createReplayExportArtifact())
const replayExportMarkdown = computed(() => formatReplayExportMarkdown(replayExportArtifact.value))

const formatReplayList = (items = [], fallback = 'none') => {
  const values = Array.isArray(items) ? items.filter(Boolean).map(String) : []
  return values.length ? values.join(' / ') : fallback
}

const formatReplayExportMarkdown = (artifact = {}) => {
  const selectedEvent = artifact.selectedEvent
  const dossier = artifact.focusedDossier
  const lines = [
    '# Worldline Replay Export',
    '',
    `Protocol: ${artifact.protocol || AGENT_WORKBENCH_PROTOCOL}`,
    `Exported: ${artifact.exportedAt || ''}`,
    `Run: ${artifact.run?.title || artifact.run?.id || 'local-preview'}`,
    `Status: ${artifact.run?.status || 'preview'}`,
    `Selected Event: ${selectedEvent?.label || 'none'}`,
    `Focused Dossier: ${dossier?.title || 'none'}`,
    '',
    '## Counts',
    `Branches: ${artifact.counts?.branches ?? 0}`,
    `Episodes: ${artifact.counts?.episodes ?? 0}`,
    `Tools: ${artifact.counts?.tools ?? 0}`,
    `Gates: ${artifact.counts?.gates ?? 0}`,
    `Artifacts: ${artifact.counts?.artifacts ?? 0}`,
    `Skills: ${artifact.counts?.skills ?? 0}`,
    `Evidence: ${artifact.counts?.evidence ?? 0}`,
    `Wiki: ${artifact.counts?.wiki ?? 0}`,
    `Graph: ${artifact.counts?.graph ?? 0}`,
    `Timeline: ${artifact.counts?.timeline ?? 0}`,
    '',
    '## Selected Event',
    selectedEvent
      ? `${selectedEvent.label}: ${selectedEvent.summaryText || selectedEvent.id}`
      : 'No selected event.',
    '',
    '## Focused Dossier',
    dossier
      ? `${dossier.badge || 'focus'}: ${dossier.summary || dossier.title}`
      : 'No focused dossier selected.',
    '',
    '## Replay Timeline',
    ...(artifact.replayTimeline || []).map((step) =>
      `${step.index}. ${step.label} - ${step.summary || step.eventId} (${formatReplayList(step.chips, 'no chips')})`
    )
  ]

  return lines.join('\n')
}

const safeExportFilePart = (value = '') =>
  String(value || 'local')
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'local'

const downloadReplayExport = () => {
  const artifact = createReplayExportArtifact()
  const filename = `worldline-replay-${safeExportFilePart(artifact.run?.id || artifact.run?.title)}.json`
  const blob = new Blob([JSON.stringify(artifact, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
  exportMessage.value = `JSON export prepared: ${filename}.`
}

const createEventAuditExport = () => ({
  schema: 'worldline.run_event_audit.v0.1',
  runId: ledgerRunId.value || run.value.id || 'local-preview',
  title: run.value.title || '',
  exportedAt: new Date().toISOString(),
  filters: {
    kind: activeEventFilter.value,
    query: eventAuditQuery.value,
    actor: eventAuditActor.value
  },
  counts: {
    loaded: visibleLedgerEvents.value.length,
    matched: filteredLedgerEvents.value.length,
    total: ledgerEventsTotal.value || visibleLedgerEvents.value.length
  },
  events: filteredLedgerEvents.value.map((event) => ({
    id: event.id,
    runId: event.runId || ledgerRunId.value || '',
    branchId: event.branchId || '',
    branchTitle: event.branchId ? eventBranchTitle(event.branchId) : '',
    eventType: event.eventType || 'event',
    actor: event.actor || 'local-workbench',
    createdAt: event.createdAt || '',
    summaryText: formatEventSummary(event),
    summary: cloneSerializable(event.summary || {}, {})
  }))
})

const downloadEventAuditExport = () => {
  if (!filteredLedgerEvents.value.length) {
    eventAuditMessage.value = 'No matching events to export.'
    return
  }
  const artifact = createEventAuditExport()
  const filename = `worldline-run-events-${safeExportFilePart(artifact.runId)}-${safeExportFilePart(activeEventFilter.value)}.json`
  const blob = new Blob([JSON.stringify(artifact, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
  eventAuditMessage.value = `Event audit JSON prepared: ${filename}.`
}

const clearEventAuditFilters = () => {
  activeEventFilter.value = 'all'
  eventAuditQuery.value = ''
  eventAuditActor.value = ''
  eventAuditMessage.value = ''
}

const copyReplayExportMarkdown = async () => {
  const markdown = formatReplayExportMarkdown(createReplayExportArtifact())
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(markdown)
    exportMessage.value = 'Markdown copied to clipboard.'
  } catch {
    exportPreviewOpen.value = true
    exportMessage.value = 'Clipboard unavailable; preview remains available.'
  }
}

const toggleReplayExportPreview = () => {
  exportPreviewOpen.value = !exportPreviewOpen.value
  exportMessage.value = exportPreviewOpen.value
    ? 'Markdown preview rendered locally.'
    : ''
}

const setSavedReplayArtifacts = (items = []) => {
  const seen = new Set()
  savedReplayArtifacts.value = (items || [])
    .filter((item) => item && typeof item === 'object')
    .filter((item) => {
      const key = item.id || item.label || JSON.stringify(item)
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
}

const artifactListFromRegisterResult = (result = {}) =>
  Array.isArray(result.artifacts) ? result.artifacts : [result.artifact].filter(Boolean)

const mergeSavedReplayArtifacts = (items = []) => {
  setSavedReplayArtifacts([
    ...savedReplayArtifacts.value,
    ...artifactListFromRegisterResult({ artifacts: items })
  ])
}

const replayArtifactRegistryPayload = (artifact = createReplayExportArtifact()) => {
  const selectedEvent = artifact.selectedEvent || {}
  const eventId = selectedEvent.id || 'run-preview'
  return {
    id: `replay-export-${eventId}`,
    kind: 'replay_export',
    format: 'json+markdown',
    label: `Replay Export: ${artifact.run?.title || artifact.run?.id || 'Worldline run'}`,
    eventId,
    branchId: selectedEvent.branchId || '',
    summary: `${artifact.replayTimeline?.length || 0} replay steps / ${artifact.counts?.artifacts || 0} artifacts`,
    content: artifact,
    markdown: formatReplayExportMarkdown(artifact)
  }
}

const primarySavedReplayArtifact = computed(() =>
  savedReplayArtifacts.value.find((artifact) =>
    artifact?.kind === 'replay_export' ||
    artifact?.type === 'replay_export' ||
    String(artifact?.id || '').startsWith('replay-export-')
  ) || null
)
const savedHandoffArtifact = computed(() =>
  savedReplayArtifacts.value.find((artifact) =>
    artifact?.kind === 'agent_handoff_capsule' ||
    artifact?.type === 'agent_handoff_capsule' ||
    String(artifact?.id || '').startsWith('agent-handoff-')
  ) || null
)
const pendingReplayArtifactPayload = computed(() => replayArtifactRegistryPayload(replayExportArtifact.value))
const registryArtifactKind = (artifact = {}) =>
  String(artifact.kind || artifact.type || '').trim() ||
  (String(artifact.id || '').startsWith('replay-export-') ? 'replay_export' : '') ||
  (String(artifact.id || '').startsWith('agent-handoff-') ? 'agent_handoff_capsule' : '') ||
  (String(artifact.id || '').startsWith('resource-detail-diff-') ? 'resource_detail_diff' : '') ||
  (String(artifact.id || '').startsWith('resource-detail-') ? 'resource_detail_snapshot' : '') ||
  'artifact'
const isResourceDetailSnapshotArtifact = (artifact = {}) =>
  registryArtifactKind(artifact) === 'resource_detail_snapshot'
const registryArtifactType = (artifact = {}) => {
  const kind = registryArtifactKind(artifact)
  if (kind === 'replay_export') return 'replay'
  if (kind === 'agent_handoff_capsule') return 'handoff'
  if (kind === 'resource_detail_diff') return 'diff'
  return 'other'
}
const registryArtifactTypeLabel = (artifact = {}) => {
  const labels = {
    replay: 'Replay',
    handoff: 'Handoff',
    diff: 'Diff',
    other: 'Artifact'
  }
  return labels[registryArtifactType(artifact)] || 'Artifact'
}
const artifactRegistryItems = computed(() => {
  const plannedItems = [
    { ...pendingReplayArtifactPayload.value, registryState: 'planned' },
    { ...handoffArtifactRegistryPayload(agentHandoffCapsule.value), registryState: 'planned' }
  ]
  const byId = new Map()
  plannedItems.forEach((artifact) => {
    if (artifact?.id) byId.set(artifact.id, artifact)
  })
  savedReplayArtifacts.value.forEach((artifact) => {
    if (!artifact?.id) return
    byId.set(artifact.id, { ...artifact, registryState: 'saved' })
  })
  return Array.from(byId.values())
})
const artifactRegistryFilters = computed(() => {
  const items = artifactRegistryItems.value
  const countByType = (type) => items.filter((artifact) => registryArtifactType(artifact) === type).length
  return [
    { id: 'all', label: '全部', count: items.length },
    { id: 'replay', label: '回放', count: countByType('replay') },
    { id: 'handoff', label: '交接', count: countByType('handoff') },
    { id: 'diff', label: '差异', count: countByType('diff') },
    { id: 'other', label: '其他', count: countByType('other') }
  ]
})
const filteredArtifactRegistryItems = computed(() => {
  if (artifactRegistryFilter.value === 'all') return artifactRegistryItems.value
  return artifactRegistryItems.value.filter((artifact) => registryArtifactType(artifact) === artifactRegistryFilter.value)
})
const registryArtifactRunId = (artifact = {}) =>
  artifact.runId ||
  artifact.run_id ||
  ledgerRunId.value ||
  replayExportArtifact.value.run?.id ||
  run.value.id ||
  'local-preview'
const registryArtifactUri = (artifact = {}) =>
  `worldline-run-ledger://${registryArtifactRunId(artifact)}/artifacts/${artifact.id || 'artifact'}`
const registryArtifactMcpArgs = (artifact = {}) => ({
  run_id: registryArtifactRunId(artifact),
  artifact_id: artifact.id || 'artifact',
  include_content: false,
  audit_db_id: ''
})
const resourceDetailReplayArgs = (artifact = {}) => ({
  ...registryArtifactMcpArgs(artifact),
  include_content: true
})
const gateMcpRunId = (gate = {}) =>
  gate.runId ||
  gate.run_id ||
  ledgerRunId.value ||
  replayExportArtifact.value.run?.id ||
  run.value.id ||
  'local-preview'
const gateMcpUri = (gate = {}) =>
  `worldline-run-ledger://${gateMcpRunId(gate)}/gates/${gate.id || 'gate'}`
const gateMcpArgs = (gate = {}) => ({
  run_id: gateMcpRunId(gate),
  gate_id: gate.id || 'gate',
  audit_db_id: ''
})
const evidenceMcpRunId = (evidence = {}) =>
  evidence.runId ||
  evidence.run_id ||
  ledgerRunId.value ||
  replayExportArtifact.value.run?.id ||
  run.value.id ||
  'local-preview'
const evidenceMcpTarget = (evidence = {}) => {
  const evidenceId = String(evidence.evidenceId || evidence.id || '').trim()
  const sourceId = String(
    evidence.sourceRef?.id ||
      evidence.sourceId ||
      evidence.source_id ||
      evidence.sourceUri ||
      sourceTargetId(evidence) ||
      ''
  ).trim()
  return { evidenceId, sourceId }
}
const evidenceMcpUri = (evidence = {}, mode = 'evidence') => {
  const { evidenceId, sourceId } = evidenceMcpTarget(evidence)
  const targetId = mode === 'source'
    ? sourceId || evidenceId || 'source'
    : evidenceId || sourceId || 'evidence'
  const segment = mode === 'source' ? 'sources' : 'evidence'
  return `worldline-run-ledger://${evidenceMcpRunId(evidence)}/${segment}/${targetId}`
}
const evidenceMcpArgs = (evidence = {}, mode = 'evidence') => {
  const { evidenceId, sourceId } = evidenceMcpTarget(evidence)
  const args = {
    run_id: evidenceMcpRunId(evidence),
    audit_db_id: ''
  }
  if (mode === 'source') {
    args.source_id = sourceId || evidenceId || 'source'
  } else {
    args.evidence_id = evidenceId || sourceId || 'evidence'
  }
  return args
}
const knowledgeMcpRunId = (item = {}) =>
  item.runId ||
  item.run_id ||
  ledgerRunId.value ||
  replayExportArtifact.value.run?.id ||
  run.value.id ||
  'local-preview'
const knowledgeMcpKind = (item = {}, fallback = 'wiki') => {
  const value = String(item.kind || item.targetType || fallback || 'wiki').trim().toLowerCase()
  if (value === 'entity') return 'graph'
  if (value === 'time') return 'timeline'
  return ['wiki', 'graph', 'timeline'].includes(value) ? value : 'wiki'
}
const knowledgeMcpId = (item = {}, kind = 'wiki') =>
  String(
    item.id ||
      item.itemId ||
      item.item_id ||
      item.slug ||
      item.name ||
      item.label ||
      (kind === 'wiki' ? 'wiki' : kind === 'graph' ? 'entity' : 'fact')
  ).trim()
const knowledgeMcpUri = (item = {}, fallbackKind = 'wiki') => {
  const kind = knowledgeMcpKind(item, fallbackKind)
  return `worldline-run-ledger://${knowledgeMcpRunId(item)}/${kind}/${knowledgeMcpId(item, kind)}`
}
const knowledgeMcpArgs = (item = {}, fallbackKind = 'wiki') => {
  const kind = knowledgeMcpKind(item, fallbackKind)
  return {
    run_id: knowledgeMcpRunId(item),
    kind,
    item_id: knowledgeMcpId(item, kind),
    audit_db_id: ''
  }
}
const mcpSourceLabels = {
  registry: 'Registry',
  'registry-replay': 'Registry Replay',
  'registry-diff': 'Registry Diff',
  'mcp-readable': 'MCP Readable',
  'artifact-rail': 'Artifact Rail',
  'gate-panel': 'Gate Panel',
  'focus-dossier': 'Focus Dossier',
  'run-manifest': 'Run Manifest'
}
const createArtifactMcpCall = (artifact = {}, source = 'artifact') => {
  const args = registryArtifactMcpArgs(artifact)
  const uri = registryArtifactUri(artifact)
  return {
    source,
    sourceLabel: mcpSourceLabels[source] || source,
    label: artifact.label || artifact.title || artifact.id || 'artifact',
    tool: MCP_RUN_ARTIFACT_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_ARTIFACT_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const createResourceDetailReplayMcpCall = (artifact = {}) => {
  const args = resourceDetailReplayArgs(artifact)
  const uri = registryArtifactUri(artifact)
  return {
    source: 'registry-replay',
    sourceLabel: mcpSourceLabels['registry-replay'],
    label: artifact.label || artifact.title || artifact.id || 'resource detail',
    tool: MCP_RUN_ARTIFACT_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_ARTIFACT_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const createResourceDetailDiffMcpCall = (artifact = {}) => {
  const args = resourceDetailReplayArgs(artifact)
  const uri = registryArtifactUri(artifact)
  return {
    source: 'registry-diff',
    sourceLabel: mcpSourceLabels['registry-diff'],
    label: artifact.label || artifact.title || artifact.id || 'resource detail',
    tool: MCP_RUN_ARTIFACT_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_ARTIFACT_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const createGateMcpCall = (gate = {}, source = 'gate') => {
  const args = gateMcpArgs(gate)
  const uri = gateMcpUri(gate)
  return {
    source,
    sourceLabel: mcpSourceLabels[source] || source,
    label: gate.label || gate.title || gate.id || 'gate',
    tool: MCP_RUN_GATE_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_GATE_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const createEvidenceMcpCall = (evidence = {}, source = 'evidence', mode = 'evidence') => {
  const args = evidenceMcpArgs(evidence, mode)
  const uri = evidenceMcpUri(evidence, mode)
  const label = mode === 'source'
    ? evidence.sourceRef?.label || evidence.sourceUri || args.source_id || 'source'
    : evidence.title || evidence.label || evidence.evidenceId || evidence.id || 'evidence'
  return {
    source,
    sourceLabel: mcpSourceLabels[source] || source,
    label,
    tool: MCP_RUN_EVIDENCE_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_EVIDENCE_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const createKnowledgeMcpCall = (item = {}, source = 'knowledge', fallbackKind = 'wiki') => {
  const args = knowledgeMcpArgs(item, fallbackKind)
  const uri = knowledgeMcpUri(item, fallbackKind)
  const label = item.title || item.name || item.label || item.slug || args.item_id || args.kind
  return {
    source,
    sourceLabel: mcpSourceLabels[source] || source,
    label,
    tool: MCP_RUN_KNOWLEDGE_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_KNOWLEDGE_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const createRunManifestMcpCall = (source = 'run-manifest') => {
  const args = runMcpManifestArgs.value
  const uri = runMcpManifestUri.value
  return {
    source,
    sourceLabel: mcpSourceLabels[source] || source,
    label: run.value.title || run.value.id || 'run manifest',
    tool: MCP_RUN_MANIFEST_TOOL,
    uri,
    args,
    instruction: [
      `Tool: ${MCP_RUN_MANIFEST_TOOL}`,
      `URI: ${uri}`,
      'Args:',
      JSON.stringify(args, null, 2)
    ].join('\n')
  }
}
const rememberMcpCall = (call = {}) => {
  lastMcpCall.value = call
  return call
}
const copyArtifactMcpCall = async (artifact = {}, source = 'artifact', setMessage = () => {}) => {
  const call = rememberMcpCall(createArtifactMcpCall(artifact, source))
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(call.instruction)
    setMessage(`MCP read call copied for ${call.label}.`)
  } catch {
    setMessage(`Clipboard unavailable; MCP read call is visible for ${call.label}.`)
  }
  return call
}
const copyGateMcpCall = async (gate = {}, source = 'gate', setMessage = () => {}) => {
  const call = rememberMcpCall(createGateMcpCall(gate, source))
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(call.instruction)
    setMessage(`MCP read call copied for ${call.label}.`)
  } catch {
    setMessage(`Clipboard unavailable; MCP read call is visible for ${call.label}.`)
  }
  return call
}
const copyEvidenceMcpCall = async (evidence = {}, source = 'evidence', mode = 'evidence', setMessage = () => {}) => {
  const call = rememberMcpCall(createEvidenceMcpCall(evidence, source, mode))
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(call.instruction)
    setMessage(`MCP read call copied for ${call.label}.`)
  } catch {
    setMessage(`Clipboard unavailable; MCP read call is visible for ${call.label}.`)
  }
  return call
}
const copyKnowledgeMcpCall = async (item = {}, source = 'knowledge', fallbackKind = 'wiki', setMessage = () => {}) => {
  const call = rememberMcpCall(createKnowledgeMcpCall(item, source, fallbackKind))
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(call.instruction)
    setMessage(`MCP read call copied for ${call.label}.`)
  } catch {
    setMessage(`Clipboard unavailable; MCP read call is visible for ${call.label}.`)
  }
  return call
}
const copyRunManifestMcpCall = async () => {
  const call = rememberMcpCall(createRunManifestMcpCall('run-manifest'))
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(call.instruction)
    runManifestMessage.value = `MCP run manifest copied for ${call.label}.`
  } catch {
    runManifestMessage.value = `Clipboard unavailable; MCP run manifest is visible for ${call.label}.`
  }
  return call
}
const loadBackendRunManifest = async () => {
  if (!ledgerRunId.value) {
    runManifestMessage.value = '请先把当前任务保存到后端账本，再载入资源清单。'
    return null
  }
  return await runLedgerOperation(async () => {
    runManifestBusy.value = true
    runManifestError.value = ''
    try {
      const result = await worldlineRunApi.getRunManifest(ledgerRunId.value, {
        include_resources: true,
        limit: 50
      })
      backendRunManifest.value = result
      runManifestMessage.value =
        `后端清单已载入：${backendRunManifestTotal.value} 个资源，分布在 ${backendRunManifestCounts.value.length} 个分区。`
      return result
    } catch (error) {
      const message = normalizeErrorMessage(error)
      runManifestError.value = message
      backendRunManifest.value = null
      runManifestMessage.value = `后端清单暂不可用：${message}`
      throw error
    } finally {
      runManifestBusy.value = false
    }
  })
}
const inspectBackendManifestResource = async (resource = {}) => {
  if (!ledgerRunId.value) {
    resourceDrilldownMessage.value = '请先保存当前任务，再检查后端资源。'
    return null
  }
  const args = resource.args || {}
  const tool = resource.tool || ''
  const runId = args.run_id || ledgerRunId.value
  const params = { limit: 20 }
  resourceDrilldownTarget.value = resource.key || resource.uri || ''
  return await runLedgerOperation(async () => {
    resourceDrilldownBusy.value = true
    try {
      let result = null
      if (tool === MCP_RUN_ARTIFACT_TOOL || resource.sectionKey === 'artifacts') {
        result = await worldlineRunApi.inspectRunArtifact(runId, {
          artifact_id: args.artifact_id || resource.id || '',
          include_content: true,
          ...params
        })
      } else if (tool === MCP_RUN_GATE_TOOL || resource.sectionKey === 'gates') {
        result = await worldlineRunApi.inspectRunGates(runId, {
          gate_id: args.gate_id || resource.id || '',
          ...params
        })
      } else if (tool === MCP_RUN_EVIDENCE_TOOL || resource.sectionKey === 'evidence' || resource.sectionKey === 'sources') {
        result = await worldlineRunApi.inspectRunEvidence(runId, {
          evidence_id: args.evidence_id || '',
          source_id: args.source_id || '',
          ...params
        })
      } else if (tool === MCP_RUN_KNOWLEDGE_TOOL || ['wiki', 'graph', 'timeline'].includes(resource.sectionKey)) {
        result = await worldlineRunApi.inspectRunKnowledge(runId, {
          kind: args.kind || resource.sectionKey || 'all',
          item_id: args.item_id || resource.id || '',
          ...params
        })
      } else {
        throw new Error(`Unsupported manifest resource tool: ${tool || resource.section}`)
      }
      resourceDrilldownResult.value = {
        resource,
        tool,
        uri: resource.uri || '',
        response: result
      }
      resourceDetailCompareResult.value = null
      resourceDetailCompareMessage.value = ''
      const selected = result?.selected || result?.items?.[0] || {}
      resourceDrilldownMessage.value =
        `已载入 ${resource.section || '资源'}：${selected.label || selected.title || selected.name || selected.id || result?.status || '详情'}。`
      return result
    } catch (error) {
      const message = normalizeErrorMessage(error)
      resourceDrilldownResult.value = null
      resourceDrilldownMessage.value = `资源详情读取失败：${message}`
      throw error
    } finally {
      resourceDrilldownBusy.value = false
    }
  })
}
const savedResourceDetailSnapshot = (artifactReadResult = {}) => {
  const selected = artifactReadResult?.selected || artifactReadResult?.items?.[0] || {}
  const content = selected?.content && typeof selected.content === 'object' ? selected.content : null
  return content?.schema === 'worldline.resource_detail_snapshot.v0.1' ? content : null
}

const resourceDetailPayloadForDiff = (value = {}) => {
  const snapshot = savedResourceDetailSnapshot(value)
  if (snapshot) return cloneSerializable(snapshot.response || snapshot.selected || {}, {})
  const selected = value?.selected || value?.items?.[0]
  if (selected?.content && typeof selected.content === 'object') {
    return cloneSerializable(selected.content.response || selected.content, {})
  }
  return cloneSerializable(value?.response || value || {}, {})
}

const diffScalarValue = (value) => {
  if (value === undefined) return 'undefined'
  if (value === null) return 'null'
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return JSON.stringify(value)
}

const flattenDetailForDiff = (value, prefix = 'response', entries = []) => {
  if (Array.isArray(value)) {
    if (!value.length) entries.push([prefix, '[]'])
    value.forEach((item, index) => flattenDetailForDiff(item, `${prefix}[${index}]`, entries))
    return entries
  }
  if (value && typeof value === 'object') {
    const keys = Object.keys(value).sort()
    if (!keys.length) entries.push([prefix, '{}'])
    keys.forEach((key) => flattenDetailForDiff(value[key], `${prefix}.${key}`, entries))
    return entries
  }
  entries.push([prefix, diffScalarValue(value)])
  return entries
}

const compareDetailPayloads = (currentPayload = {}, savedPayload = {}) => {
  const currentMap = new Map(flattenDetailForDiff(currentPayload))
  const savedMap = new Map(flattenDetailForDiff(savedPayload))
  const paths = Array.from(new Set([...currentMap.keys(), ...savedMap.keys()])).sort()
  const rows = []
  const summary = { added: 0, removed: 0, changed: 0, unchanged: 0 }
  paths.forEach((path) => {
    const hasCurrent = currentMap.has(path)
    const hasSaved = savedMap.has(path)
    if (!hasSaved && hasCurrent) {
      summary.added += 1
      rows.push({ path, type: 'added', typeLabel: '当前新增' })
    } else if (hasSaved && !hasCurrent) {
      summary.removed += 1
      rows.push({ path, type: 'removed', typeLabel: '当前缺失' })
    } else if (currentMap.get(path) !== savedMap.get(path)) {
      summary.changed += 1
      rows.push({ path, type: 'changed', typeLabel: '值变化' })
    } else {
      summary.unchanged += 1
    }
  })
  return {
    summary,
    rows,
    preview: rows.slice(0, 8),
    totalPaths: paths.length
  }
}

const restoreResourceDetailFromSnapshot = (artifact = {}, artifactReadResult = {}) => {
  const selected = artifactReadResult?.selected || artifactReadResult?.items?.[0] || {}
  const snapshot = savedResourceDetailSnapshot(artifactReadResult)
  const replayArgs = resourceDetailReplayArgs(artifact)
  const resource = snapshot?.resource || {
    id: selected.id || artifact.id || '',
    key: `registry-resource-detail:${artifact.id || selected.id || 'artifact'}`,
    section: artifact.label || selected.label || 'Resource Detail Snapshot',
    sectionKey: 'artifacts',
    uri: selected.uri || registryArtifactUri(artifact),
    tool: MCP_RUN_ARTIFACT_TOOL,
    args: replayArgs
  }
  const response = snapshot?.response || selected?.content || artifactReadResult
  resourceDrilldownTarget.value = resource.key || resource.uri || ''
  resourceDrilldownResult.value = {
    resource,
    tool: resource.tool || MCP_RUN_ARTIFACT_TOOL,
    uri: resource.uri || registryArtifactUri(artifact),
    response
  }
  resourceDetailCompareResult.value = null
  resourceDetailCompareMessage.value = ''
  const label = snapshot?.selected?.label || selected.label || artifact.label || artifact.id || 'Resource Detail'
  resourceDrilldownMessage.value = snapshot
    ? `已从快照恢复资源详情：${label}。`
    : `已载入已保存 Artifact 详情：${label}。`
  return { selected, snapshot, label }
}

const replayResourceDetailArtifact = async (artifact = {}) => {
  if (!isResourceDetailSnapshotArtifact(artifact)) return null
  if (artifact.registryState !== 'saved') {
    artifactRegistryMessage.value = '请先保存资源详情证据，再从后端账本读取。'
    return null
  }
  return await runLedgerOperation(async () => {
    const artifactId = artifact.id || ''
    const runId = registryArtifactRunId(artifact)
    resourceDetailReplayBusyId.value = artifactId
    resourceDrilldownBusy.value = true
    try {
      const call = rememberMcpCall(createResourceDetailReplayMcpCall(artifact))
      const result = await worldlineRunApi.inspectRunArtifact(runId, {
        artifact_id: call.args.artifact_id,
        include_content: true,
        limit: 20
      })
      const restored = restoreResourceDetailFromSnapshot(artifact, result)
      artifactRegistryMessage.value = `已读取 ${restored.label} 到资源详情。`
      return result
    } catch (error) {
      const message = normalizeErrorMessage(error)
      resourceDrilldownResult.value = null
      resourceDrilldownMessage.value = `Resource detail replay unavailable: ${message}`
      throw error
    } finally {
      resourceDetailReplayBusyId.value = ''
      resourceDrilldownBusy.value = false
    }
  })
}

const compareResourceDetailSnapshotArtifact = async (artifact = {}) => {
  if (!isResourceDetailSnapshotArtifact(artifact)) return null
  if (!resourceDrilldownResult.value) {
    resourceDetailCompareMessage.value = '请先检查或读取一个资源详情，再对比已保存快照。'
    return null
  }
  if (artifact.registryState !== 'saved') {
    resourceDetailCompareMessage.value = '请先保存资源详情证据，再进行对比。'
    return null
  }
  return await runLedgerOperation(async () => {
    const artifactId = artifact.id || ''
    const runId = registryArtifactRunId(artifact)
    resourceDetailCompareBusyId.value = artifactId
    try {
      const call = rememberMcpCall(createResourceDetailDiffMcpCall(artifact))
      const savedResult = await worldlineRunApi.inspectRunArtifact(runId, {
        artifact_id: call.args.artifact_id,
        include_content: true,
        limit: 20
      })
      const currentPayload = resourceDetailPayloadForDiff(resourceDrilldownResult.value)
      const savedPayload = resourceDetailPayloadForDiff(savedResult)
      const diff = compareDetailPayloads(currentPayload, savedPayload)
      const saved = savedResourceDetailSnapshot(savedResult)
      const currentSelected = currentPayload?.selected || currentPayload?.response?.selected || {}
      const savedSelected = saved?.selected || savedPayload?.selected || savedPayload?.response?.selected || {}
      const currentLabel = currentSelected.label || currentSelected.title || currentSelected.id || 'Current detail'
      const savedLabel = savedSelected.label || artifact.label || artifact.id || 'Saved snapshot'
      resourceDetailCompareResult.value = {
        title: `${currentLabel} vs ${savedLabel}`,
        artifactId,
        currentLabel,
        savedLabel,
        ...diff
      }
      resourceDetailCompareMessage.value =
        `已对比当前资源详情与 ${savedLabel}：${diff.summary.changed} 项变化，${diff.summary.added} 项新增，${diff.summary.removed} 项缺失。`
      artifactRegistryMessage.value = `已对比 ${savedLabel} 与当前资源详情。`
      return savedResult
    } catch (error) {
      const message = normalizeErrorMessage(error)
      resourceDetailCompareResult.value = null
      resourceDetailCompareMessage.value = `资源详情对比暂不可用：${message}`
      throw error
    } finally {
      resourceDetailCompareBusyId.value = ''
    }
  })
}
const eventTokenResourceUri = (sectionKey = '', itemId = '') =>
  `worldline-run-ledger://${ledgerRunId.value || run.value.id || 'local-preview'}/${sectionKey}/${itemId}`

const eventTokenBackendResource = (item = {}) => {
  const itemId = String(item.targetId || item.id || '').trim()
  if (!itemId) return null
  const runId = ledgerRunId.value || item.runId || ''
  if (!runId) return null
  const sectionKey = item.resourceSectionKey || item.sectionKey || item.targetType
  const base = {
    id: itemId,
    key: `event-token:${sectionKey}:${itemId}`,
    section: item.label || itemId,
    sectionKey,
    uri: eventTokenResourceUri(sectionKey, itemId),
    args: { run_id: runId }
  }

  if (sectionKey === 'artifact') {
    return {
      ...base,
      section: 'Event Artifact',
      sectionKey: 'artifacts',
      tool: MCP_RUN_ARTIFACT_TOOL,
      args: { ...base.args, artifact_id: itemId }
    }
  }

  if (sectionKey === 'gate') {
    return {
      ...base,
      section: 'Event Gate',
      sectionKey: 'gates',
      tool: MCP_RUN_GATE_TOOL,
      args: { ...base.args, gate_id: itemId }
    }
  }

  if (sectionKey === 'evidence' || sectionKey === 'source') {
    return {
      ...base,
      section: sectionKey === 'source' ? 'Event Source' : 'Event Evidence',
      sectionKey,
      tool: MCP_RUN_EVIDENCE_TOOL,
      args: {
        ...base.args,
        evidence_id: sectionKey === 'evidence' ? itemId : '',
        source_id: sectionKey === 'source' ? itemId : ''
      }
    }
  }

  if (['wiki', 'graph', 'timeline'].includes(sectionKey)) {
    return {
      ...base,
      section: `Event ${formatSummaryKey(sectionKey)}`,
      sectionKey,
      tool: MCP_RUN_KNOWLEDGE_TOOL,
      args: {
        ...base.args,
        kind: sectionKey,
        item_id: itemId
      }
    }
  }

  return null
}

const inspectEventTokenResource = async (item = {}) => {
  const resource = eventTokenBackendResource(item)
  if (!resource || !canUseRunLedger.value || !ledgerRunId.value) return null
  return await inspectBackendManifestResource(resource)
}
const lastMcpArgsPreview = computed(() =>
  lastMcpCall.value ? JSON.stringify(lastMcpCall.value.args, null, 2) : ''
)
const focusDossierMcpPreview = computed(() =>
  lastMcpCall.value?.source === 'focus-dossier' ? lastMcpCall.value : null
)
const focusDossierMcpArgsPreview = computed(() =>
  focusDossierMcpPreview.value ? JSON.stringify(focusDossierMcpPreview.value.args, null, 2) : ''
)
const mcpReadableRunId = computed(() =>
  primarySavedReplayArtifact.value?.runId ||
  ledgerRunId.value ||
  replayExportArtifact.value.run?.id ||
  'local-preview'
)
const mcpReadableArtifactId = computed(() =>
  primarySavedReplayArtifact.value?.id ||
  pendingReplayArtifactPayload.value.id ||
  'replay-export'
)
const mcpReadableArtifactUri = computed(() =>
  `worldline-run-ledger://${mcpReadableRunId.value}/artifacts/${mcpReadableArtifactId.value}`
)
const mcpReadableState = computed(() =>
  primarySavedReplayArtifact.value ? 'registered' : 'pending'
)
const mcpReadableLabel = computed(() =>
  primarySavedReplayArtifact.value ? 'Registered' : 'Save required'
)
const mcpReadableArgs = computed(() => ({
  run_id: mcpReadableRunId.value,
  artifact_id: mcpReadableArtifactId.value,
  include_content: false,
  audit_db_id: ''
}))
const mcpReadableArgsPreview = computed(() => JSON.stringify(mcpReadableArgs.value, null, 2))
const mcpReadableHint = computed(() =>
  primarySavedReplayArtifact.value
    ? 'External Agents can inspect this saved replay artifact through the controlled worldline MCP boundary.'
    : 'Save Artifact with admin access before external Agents can read this planned artifact URI.'
)
const runMcpManifestRunId = computed(() => mcpReadableRunId.value)
const runMcpManifestUri = computed(() =>
  `worldline-run-ledger://${runMcpManifestRunId.value}/manifest`
)
const runMcpManifestArgs = computed(() => ({
  run_id: runMcpManifestRunId.value,
  include_resources: true,
  limit: 50,
  audit_db_id: ''
}))
const runMcpManifestArgsPreview = computed(() => JSON.stringify(runMcpManifestArgs.value, null, 2))
const runMcpManifestCounts = computed(() => {
  const sourceCount = uniqueStrings(
    worldlineStore.evidenceRefs
      .map((evidence) => sourceTargetId(evidence))
      .filter(Boolean)
  ).length
  return [
    { key: 'artifacts', label: 'Artifacts', count: artifactRegistryItems.value.length },
    { key: 'gates', label: 'Gates', count: agentRun.value.gateResults.length },
    { key: 'evidence', label: 'Evidence', count: worldlineStore.evidenceRefs.length },
    { key: 'sources', label: 'Sources', count: sourceCount },
    { key: 'wiki', label: 'Wiki', count: worldlineStore.wikiRefs.length },
    { key: 'graph', label: 'Graph', count: worldlineStore.entityRefs.length },
    { key: 'timeline', label: 'Time', count: worldlineStore.timelineRefs.length }
  ]
})
const runMcpManifestTotal = computed(() =>
  runMcpManifestCounts.value.reduce((total, item) => total + item.count, 0)
)
const backendRunManifestStatus = computed(() => {
  if (runManifestBusy.value) return 'loading'
  if (runManifestError.value) return 'failed'
  if (backendRunManifest.value?.status === 'ok') return 'loaded'
  if (!ledgerRunId.value) return 'pending'
  if (!canUseRunLedger.value) return 'locked'
  return 'ready'
})
const backendRunManifestStatusLabel = computed(() => {
  const labels = {
    loading: '载入中',
    failed: '失败',
    loaded: '已载入',
    pending: '需先保存',
    locked: '需管理员',
    ready: '可载入'
  }
  return labels[backendRunManifestStatus.value] || '可载入'
})
const backendRunManifestCounts = computed(() => {
  const manifest = backendRunManifest.value || {}
  const sections = manifest.sections || {}
  return Object.keys(RUN_MANIFEST_SECTION_LABELS)
    .map((key) => {
      const section = sections[key] || {}
      const count = Number(section.count ?? manifest.resourceCounts?.[key] ?? 0)
      return {
        key,
        label: RUN_MANIFEST_SECTION_LABELS[key],
        count: Number.isFinite(count) ? count : 0,
        tool: section.tool || '',
        resources: Array.isArray(section.resources) ? section.resources : []
      }
    })
    .filter((item) => item.count > 0 || item.resources.length)
})
const backendRunManifestTotal = computed(() =>
  backendRunManifestCounts.value.reduce((total, item) => total + item.count, 0)
)
const backendRunManifestTools = computed(() =>
  (backendRunManifest.value?.tools || [])
    .map((tool) => ({
      name: tool.name || '',
      writeScope: tool.write_scope || tool.writeScope || 'none'
    }))
    .filter((tool) => tool.name)
)
const backendRunManifestResources = computed(() =>
  backendRunManifestCounts.value
    .flatMap((section) =>
      section.resources.slice(0, 2).map((resource) => ({
        key: `${section.key}:${resource.id || resource.uri || resource.label}`,
        id: resource.id || resource.evidenceId || '',
        tool: resource.tool || section.tool || '',
        args: resource.args || {},
        sectionKey: section.key,
        section: section.label,
        uri: resource.uri || resource.id || resource.label || 'worldline-run-ledger://resource'
      }))
    )
    .slice(0, 6)
)
const resourceDrilldownPreview = computed(() =>
  resourceDrilldownResult.value ? JSON.stringify(resourceDrilldownResult.value.response, null, 2) : ''
)
const resourceDrilldownSummaryCards = computed(() => {
  const response = resourceDrilldownResult.value?.response || {}
  const selected = response.selected || response.items?.[0] || {}
  const itemCount = Number(response.total ?? (Array.isArray(response.items) ? response.items.length : selected?.id ? 1 : 0))
  return [
    { key: 'resource', label: '资源', value: selected.label || selected.title || selected.id || resourceDrilldownResult.value?.resource?.id || '未命名资源' },
    { key: 'count', label: '返回', value: Number.isFinite(itemCount) ? `${itemCount} 项` : '未知' },
    { key: 'content', label: '内容', value: response.content_included === true ? '已包含正文' : '摘要/索引' }
  ]
})
const backendRunManifestSummary = computed(() => {
  if (runManifestError.value) return `Backend manifest failed: ${runManifestError.value}`
  if (backendRunManifest.value?.status === 'ok') {
    return `${backendRunManifestTotal.value} backend resources from ${backendRunManifestTools.value.length} read tools.`
  }
  if (!ledgerRunId.value) return 'Save this run to the backend ledger before loading the API manifest.'
  if (!canUseRunLedger.value) return 'Admin access is required to inspect the backend run manifest.'
  return 'Load the backend manifest to compare server-derived resources with the local preview.'
})

const modalBody = (value = '') => {
  if (value === undefined || value === null || value === '') return '暂无可展示内容。'
  if (typeof value === 'string') return value
  return JSON.stringify(value, null, 2)
}

const openDetailModal = ({ title = '详情', subtitle = '', body = '' } = {}) => {
  detailModalTitle.value = title
  detailModalSubtitle.value = subtitle
  detailModalBody.value = modalBody(body)
  detailModalOpen.value = true
}

const closeDetailModal = () => {
  detailModalOpen.value = false
}

const openMcpReadableArgsModal = () => {
  openDetailModal({
    title: 'MCP 读取参数',
    subtitle: mcpReadableArtifactUri.value,
    body: mcpReadableArgsPreview.value
  })
}

const openRunManifestArgsModal = () => {
  openDetailModal({
    title: 'Run Manifest 参数',
    subtitle: runMcpManifestUri.value,
    body: runMcpManifestArgsPreview.value
  })
}

const openResourceDetailResponseModal = () => {
  openDetailModal({
    title: '资源详情后端响应',
    subtitle: resourceDrilldownResult.value?.uri || resourceDrilldownResult.value?.resource?.uri || '',
    body: resourceDrilldownPreview.value
  })
}

const openLastMcpArgsModal = () => {
  openDetailModal({
    title: '最近 MCP 调用参数',
    subtitle: lastMcpCall.value?.uri || '',
    body: lastMcpArgsPreview.value
  })
}

const copyMcpReadInstruction = async () => {
  await copyArtifactMcpCall(
    {
      id: mcpReadableArtifactId.value,
      label: primarySavedReplayArtifact.value?.label || pendingReplayArtifactPayload.value.label || mcpReadableArtifactId.value,
      runId: mcpReadableRunId.value
    },
    'mcp-readable',
    (message) => {
      mcpReadMessage.value = message
    }
  )
}

const copyRegistryArtifactMcpCall = async (artifact = {}) => {
  await copyArtifactMcpCall(artifact, 'registry', (message) => {
    artifactRegistryMessage.value = message
  })
}

const copyArtifactRailMcpCall = async (artifact = {}) => {
  await copyArtifactMcpCall(artifact, 'artifact-rail', (message) => {
    artifactRailMessage.value = message
  })
}

const copyGateRunMcpCall = async (gate = {}) => {
  await copyGateMcpCall(gate, 'gate-panel', (message) => {
    gatePanelMessage.value = message
  })
}

const copyFocusDossierMcpCall = async (item = {}) => {
  if (item.targetType === 'gate') {
    const gate =
      findGateResult(item.targetId) || {
        id: item.targetId || item.label || 'gate',
        label: String(item.label || item.targetId || 'gate').replace(/^Gate:\s*/i, ''),
        branchId: item.branchId || ''
      }
    await copyGateMcpCall(gate, 'focus-dossier', (message) => {
      focusDossierMcpMessage.value = message
    })
    return
  }

  if (item.targetType === 'evidence' || item.targetType === 'source') {
    const evidence =
      item.targetType === 'source'
        ? findSourceEvidence(item.targetId)
        : findEvidenceRef(item.targetId)
    const fallbackEvidence = evidence || {
      id: item.targetType === 'evidence' ? item.targetId || item.label || 'evidence' : '',
      evidenceId: item.targetType === 'evidence' ? item.targetId || item.label || 'evidence' : '',
      title: String(item.label || item.targetId || item.targetType).replace(/^(Evidence|Source):\s*/i, ''),
      sourceUri: item.targetType === 'source' ? item.targetId || '' : '',
      sourceRef: item.targetType === 'source' ? { id: item.targetId || '' } : {}
    }
    await copyEvidenceMcpCall(
      fallbackEvidence,
      'focus-dossier',
      item.targetType === 'source' ? 'source' : 'evidence',
      (message) => {
        focusDossierMcpMessage.value = message
      }
    )
    return
  }

  if (['wiki', 'graph', 'timeline'].includes(item.targetType)) {
    const knowledge =
      item.targetType === 'wiki'
        ? findWikiRef(item.targetId)
        : item.targetType === 'graph'
          ? findEntityRef(item.targetId)
          : findTimelineRef(item.targetId)
    const fallbackKnowledge = knowledge || {
      id: item.targetId || item.label || item.targetType,
      label: String(item.label || item.targetId || item.targetType).replace(/^(Wiki|Graph|Time):\s*/i, ''),
      targetType: item.targetType
    }
    await copyKnowledgeMcpCall(
      { ...fallbackKnowledge, targetType: item.targetType },
      'focus-dossier',
      item.targetType,
      (message) => {
        focusDossierMcpMessage.value = message
      }
    )
    return
  }

  const artifact =
    findArtifactDetail(item.targetId) ||
    normalizeArtifactDetail({
      id: item.targetId || item.label || 'artifact',
      label: String(item.label || item.targetId || 'artifact').replace(/^Artifact:\s*/i, ''),
      branchId: item.branchId || ''
    })
  await copyArtifactMcpCall(artifact, 'focus-dossier', (message) => {
    focusDossierMcpMessage.value = message
  })
}

const compactDossierForHandoff = (dossier = {}) => {
  if (!dossier || typeof dossier !== 'object') return null
  return {
    type: dossier.type || '',
    title: dossier.title || '',
    badge: dossier.badge || '',
    summary: dossier.summary || '',
    links: (Array.isArray(dossier.links) ? dossier.links : [])
      .slice(0, 8)
      .map((link) => ({
        label: link.label || '',
        targetType: link.targetType || '',
        targetId: link.targetId || '',
        canFocus: Boolean(link.canFocus)
      }))
  }
}

const agentHandoffCapsule = computed(() => {
  const artifact = replayExportArtifact.value
  const selectedEvent = artifact.selectedEvent || {}
  const summary = selectedEvent.summary || {}
  const checkpoints = (artifact.replayTimeline || []).slice(0, 8).map((step) => ({
    index: step.index,
    event_id: step.eventId,
    event_type: step.eventType,
    label: step.label,
    summary: step.summary,
    chips: step.chips || []
  }))

  return {
    protocol: AGENT_HANDOFF_PROTOCOL,
    intent: 'Inspect the replay artifact through the controlled Worldline MCP boundary, summarize the branch state, and propose the next verifiable worldline action before any write.',
    created_at: artifact.exportedAt,
    source: {
      run_id: mcpReadableRunId.value,
      run_title: artifact.run?.title || '',
      run_status: artifact.run?.status || '',
      event_id: selectedEvent.id || '',
      event_type: selectedEvent.eventType || '',
      event_label: selectedEvent.label || 'Run Preview',
      branch_id: selectedEvent.branchId || '',
      branch_title: selectedEvent.branchTitle || '',
      artifact_id: mcpReadableArtifactId.value,
      artifact_uri: mcpReadableArtifactUri.value,
      artifact_state: mcpReadableState.value,
      focused_dossier: compactDossierForHandoff(artifact.focusedDossier)
    },
    mcp: {
      tool: MCP_RUN_ARTIFACT_TOOL,
      uri: mcpReadableArtifactUri.value,
      args: cloneSerializable(mcpReadableArgs.value, {}),
      include_content_default: false,
      audit_hint: 'Set audit_db_id when the receiving Agent has an active knowledge database context.'
    },
    boundary: {
      write_scope: 'none',
      allowed_actions: [
        'read saved replay artifact metadata',
        'summarize evidence and quality state',
        'propose next branch or gate',
        'request explicit approval before writes'
      ],
      forbidden_actions: [
        'direct database writes',
        'unrestricted filesystem writes',
        'tool execution outside Worldline service boundary'
      ]
    },
    quality: {
      replay_steps: artifact.replayTimeline?.length || 0,
      evidence_count: artifact.counts?.evidence || 0,
      artifact_count: artifact.counts?.artifacts || 0,
      selected_gate_ids: uniqueStrings(summary.gateResultIds || summary.gateIds || []),
      selected_evidence_ids: uniqueStrings(summary.evidenceIds || summary.evidenceRunIds || []),
      selected_artifact_ids: uniqueStrings(summary.artifactIds || []),
      rollback: 'If evidence or gate coverage is insufficient, return to branch decision and do not execute writes.'
    },
    checkpoints
  }
})
const agentHandoffCapsulePreview = computed(() => JSON.stringify(agentHandoffCapsule.value, null, 2))

const toggleHandoffCapsulePreview = () => {
  handoffPreviewOpen.value = !handoffPreviewOpen.value
  handoffMessage.value = handoffPreviewOpen.value
    ? 'Handoff capsule preview rendered locally.'
    : ''
}

const copyHandoffCapsule = async () => {
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error('Clipboard API unavailable')
    }
    await navigator.clipboard.writeText(agentHandoffCapsulePreview.value)
    handoffMessage.value = 'Agent handoff capsule copied.'
  } catch {
    handoffPreviewOpen.value = true
    handoffMessage.value = 'Clipboard unavailable; handoff capsule preview remains visible.'
  }
}

const formatAgentHandoffMarkdown = (capsule = {}) => {
  const source = capsule.source || {}
  const mcp = capsule.mcp || {}
  const boundary = capsule.boundary || {}
  const quality = capsule.quality || {}
  const lines = [
    '# Worldline Agent Handoff Capsule',
    '',
    `Protocol: ${capsule.protocol || AGENT_HANDOFF_PROTOCOL}`,
    `Run: ${source.run_title || source.run_id || 'local-preview'}`,
    `Selected Event: ${source.event_label || source.event_id || 'none'}`,
    `Artifact URI: ${source.artifact_uri || mcp.uri || ''}`,
    `MCP Tool: ${mcp.tool || MCP_RUN_ARTIFACT_TOOL}`,
    `Write Scope: ${boundary.write_scope || 'none'}`,
    `Include Content: ${mcp.args?.include_content === true ? 'true' : 'false'}`,
    '',
    '## Intent',
    capsule.intent || '',
    '',
    '## Quality',
    `Replay Steps: ${quality.replay_steps ?? 0}`,
    `Evidence: ${quality.evidence_count ?? 0}`,
    `Artifacts: ${quality.artifact_count ?? 0}`,
    `Rollback: ${quality.rollback || ''}`,
    '',
    '## Checkpoints',
    ...((capsule.checkpoints || []).map((step) =>
      `${step.index}. ${step.label || step.event_type || step.event_id} - ${step.summary || step.event_id}`
    ))
  ]
  return lines.join('\n')
}

const handoffArtifactRegistryPayload = (capsule = agentHandoffCapsule.value) => {
  const source = capsule.source || {}
  const eventId = source.event_id || 'run-preview'
  const label = source.event_label || source.run_title || 'Worldline handoff'
  return {
    id: `agent-handoff-${eventId}`,
    kind: 'agent_handoff_capsule',
    format: 'json+markdown',
    label: `Agent Handoff: ${label}`,
    eventId,
    branchId: source.branch_id || '',
    summary: `${capsule.quality?.replay_steps || 0} replay steps / ${capsule.boundary?.write_scope || 'none'} write scope`,
    content: capsule,
    markdown: formatAgentHandoffMarkdown(capsule)
  }
}

const createResourceDetailArtifactContent = () => {
  const detail = resourceDrilldownResult.value || {}
  const resource = detail.resource || {}
  const response = detail.response || {}
  const selected = response.selected || response.items?.[0] || {}
  const selectedEvent = selectedLedgerEvent.value || {}
  return {
    schema: 'worldline.resource_detail_snapshot.v0.1',
    exportedAt: new Date().toISOString(),
    run: {
      id: ledgerRunId.value || run.value.id || '',
      title: run.value.title || ''
    },
    resource: {
      id: resource.id || selected.id || '',
      key: resource.key || '',
      section: resource.section || '',
      sectionKey: resource.sectionKey || '',
      uri: detail.uri || resource.uri || '',
      tool: detail.tool || resource.tool || '',
      args: cloneSerializable(resource.args || {}, {})
    },
    selected: cloneSerializable(selected, {}),
    selectedEvent: {
      id: selectedEvent.id || '',
      eventType: selectedEvent.eventType || '',
      branchId: selectedEvent.branchId || '',
      actor: selectedEvent.actor || '',
      summary: cloneSerializable(selectedEvent.summary || {}, {})
    },
    focusedDossier: cloneSerializable(focusedDossier.value, null),
    response: cloneSerializable(response, {})
  }
}

const formatResourceDetailArtifactMarkdown = (artifact = {}) => {
  const resource = artifact.resource || {}
  const selected = artifact.selected || {}
  const event = artifact.selectedEvent || {}
  return [
    '# Worldline Resource Detail Snapshot',
    '',
    `Run: ${artifact.run?.title || artifact.run?.id || 'unknown'}`,
    `Resource: ${selected.label || selected.title || selected.name || selected.id || resource.id || 'resource'}`,
    `Tool: ${resource.tool || ''}`,
    `URI: ${resource.uri || ''}`,
    `Event: ${event.eventType || event.id || 'none'}`,
    `Branch: ${event.branchId || 'run scope'}`,
    '',
    '## Selected',
    '```json',
    JSON.stringify(selected, null, 2),
    '```',
    '',
    '## Response',
    '```json',
    JSON.stringify(artifact.response || {}, null, 2),
    '```'
  ].join('\n')
}

const resourceDetailArtifactRegistryPayload = () => {
  const content = createResourceDetailArtifactContent()
  const resource = content.resource || {}
  const selected = content.selected || {}
  const event = content.selectedEvent || {}
  const label = selected.label || selected.title || selected.name || selected.id || resource.id || resource.section || 'Resource Detail'
  const artifactId = `resource-detail-${safeExportFilePart(content.run?.id || 'run')}-${safeExportFilePart(selected.id || resource.id || resource.sectionKey || 'detail')}`
  return {
    id: artifactId,
    kind: 'resource_detail_snapshot',
    format: 'json+markdown',
    label: `Resource Detail: ${label}`,
    eventId: event.id || '',
    branchId: event.branchId || '',
    summary: `${resource.section || 'Resource'} via ${resource.tool || 'inspect'}`,
    content,
    markdown: formatResourceDetailArtifactMarkdown(content)
  }
}

const createResourceDetailDiffArtifactContent = () => {
  const diff = resourceDetailCompareResult.value || {}
  const detail = resourceDrilldownResult.value || {}
  const resource = detail.resource || {}
  const response = detail.response || {}
  const selected = response.selected || response.items?.[0] || {}
  return {
    schema: 'worldline.resource_detail_diff.v0.1',
    exportedAt: new Date().toISOString(),
    run: {
      id: ledgerRunId.value || run.value.id || '',
      title: run.value.title || ''
    },
    current: {
      label: diff.currentLabel || selected.label || selected.title || selected.id || 'Current detail',
      resource: {
        id: resource.id || selected.id || '',
        key: resource.key || '',
        section: resource.section || '',
        sectionKey: resource.sectionKey || '',
        uri: detail.uri || resource.uri || '',
        tool: detail.tool || resource.tool || '',
        args: cloneSerializable(resource.args || {}, {})
      },
      selected: cloneSerializable(selected, {})
    },
    saved: {
      label: diff.savedLabel || 'Saved snapshot',
      artifactId: diff.artifactId || '',
      uri: diff.artifactId ? registryArtifactUri({ id: diff.artifactId, runId: ledgerRunId.value || run.value.id || '' }) : ''
    },
    summary: cloneSerializable(diff.summary || {}, {}),
    totalPaths: Number(diff.totalPaths || 0),
    rows: cloneSerializable(diff.rows || [], []),
    preview: cloneSerializable(diff.preview || [], []),
    source: {
      savedArtifactId: diff.artifactId || '',
      compareMessage: resourceDetailCompareMessage.value || '',
      lastMcpCall: cloneSerializable(lastMcpCall.value, null)
    }
  }
}

const formatResourceDetailDiffArtifactMarkdown = (artifact = {}) => {
  const summary = artifact.summary || {}
  const preview = Array.isArray(artifact.preview) ? artifact.preview : []
  const rows = preview.length ? preview : Array.isArray(artifact.rows) ? artifact.rows.slice(0, 12) : []
  return [
    '# Worldline Resource Detail Diff',
    '',
    `Run: ${artifact.run?.title || artifact.run?.id || 'unknown'}`,
    `Current: ${artifact.current?.label || 'Current detail'}`,
    `Saved: ${artifact.saved?.label || artifact.saved?.artifactId || 'Saved snapshot'}`,
    `Saved Artifact: ${artifact.saved?.artifactId || ''}`,
    '',
    '## Summary',
    '',
    `Added: ${summary.added ?? 0}`,
    `Removed: ${summary.removed ?? 0}`,
    `Changed: ${summary.changed ?? 0}`,
    `Unchanged: ${summary.unchanged ?? 0}`,
    `Total Paths: ${artifact.totalPaths ?? 0}`,
    '',
    '## Preview',
    '',
    ...(rows.length ? rows.map((row) => `- ${row.path || 'path'}: ${row.typeLabel || row.type || 'delta'}`) : ['- No changed paths in preview.']),
    '',
    '## Diff JSON',
    '',
    '```json',
    JSON.stringify({
      current: artifact.current,
      saved: artifact.saved,
      summary: artifact.summary,
      rows: artifact.rows
    }, null, 2),
    '```'
  ].join('\n')
}

const resourceDetailDiffArtifactRegistryPayload = () => {
  const content = createResourceDetailDiffArtifactContent()
  const saved = content.saved || {}
  const current = content.current || {}
  const artifactId = [
    'resource-detail-diff',
    safeExportFilePart(content.run?.id || 'run'),
    safeExportFilePart(saved.artifactId || current.resource?.id || 'detail')
  ].join('-')
  return {
    id: artifactId,
    kind: 'resource_detail_diff',
    format: 'json+markdown',
    label: `Resource Detail Diff: ${current.label || 'Current'} vs ${saved.label || 'Saved'}`,
    branchId: selectedLedgerEvent.value?.branchId || '',
    eventId: selectedLedgerEvent.value?.id || '',
    summary: `${content.summary.changed || 0} changed / ${content.summary.added || 0} added / ${content.summary.removed || 0} removed`,
    content,
    markdown: formatResourceDetailDiffArtifactMarkdown(content)
  }
}

const formatDecisionScore = (value) => {
  if (value === undefined || value === null || value === '') return ''
  const numericValue = Number(value)
  if (Number.isFinite(numericValue) && numericValue <= 1) {
    return `${Math.round(numericValue * 100)}%`
  }
  return String(value)
}

const eventDecisionSnapshot = (event = {}) => {
  const summary = event.summary || {}
  if (!summary || typeof summary !== 'object') return []
  const items = [
    { label: 'Status', value: summary.status },
    { label: 'Branch', value: summary.branch_title },
    { label: 'Type', value: summary.branch_type },
    { label: 'Quality', value: summary.quality_status },
    { label: 'Score', value: formatDecisionScore(summary.score) },
    { label: 'Reason', value: summary.reason }
  ]
  return items.filter((item) => item.value !== undefined && item.value !== null && item.value !== '')
}

const eventDecisionStatusLabel = (event = {}) =>
  event.summary?.status || eventTypeLabel(event.eventType)

const listField = (event = {}, key = '') => {
  const value = event.summary?.[key]
  return Array.isArray(value) ? Array.from(new Set(value.filter(Boolean).map(String))) : []
}

const detailField = (event = {}, key = '') => {
  const value = event.summary?.[key]
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') : []
}
const detailById = (items = [], value = '') =>
  items.find((item) => String(item.id || item.artifactId || item.gateId || '') === value) || null

const itemStableId = (item = {}) => String(item.evidenceId || item.id || item.slug || item.name || item.title || '')
const branchContainsToken = (branch = {}, field = '', value = '') =>
  Array.isArray(branch[field]) && branch[field].map(String).includes(value)
const findBranchById = (branchId = '') =>
  worldlineStore.branches.find((branch) => branch.id === branchId) || null
const findBranchForToken = (field = '', value = '') =>
  worldlineStore.branches.find((branch) => branchContainsToken(branch, field, value)) || null
const findEvidenceRef = (value = '') =>
  worldlineStore.evidenceRefs.find((item) => itemStableId(item) === value || item.id === value || item.evidenceId === value)
const findWikiRef = (value = '') =>
  worldlineStore.wikiRefs.find((item) => itemStableId(item) === value || item.id === value || item.slug === value)
const findEntityRef = (value = '') =>
  worldlineStore.entityRefs.find((item) => itemStableId(item) === value || item.id === value || item.name === value)
const findTimelineRef = (value = '') =>
  worldlineStore.timelineRefs.find((item) => itemStableId(item) === value || item.id === value)
const sourceTargetId = (evidence = {}) =>
  String(evidence.evidenceId || evidence.id || evidence.sourceRef?.id || evidence.sourceUri || '')
const findSourceEvidence = (value = '') =>
  worldlineStore.evidenceRefs.find((item) =>
    sourceTargetId(item) === value ||
    item.sourceRef?.id === value ||
    item.sourceUri === value
  )
const findToolTrace = (value = '', event = selectedLedgerEvent.value || {}) =>
  (agentRun.value.toolTraces || []).find((trace) => trace.id === value) ||
  detailById(detailField(event, 'toolDetails'), value)
const findEpisode = (value = '') =>
  (agentRun.value.episodes || []).find((episode) => episode.id === value) || null
const findRunManifestEvent = (value = '') =>
  visibleLedgerEvents.value.find((event) => event.id === value || event.runId === value) ||
  selectedLedgerEvent.value ||
  null
const episodesForToken = (field = '', value = '') =>
  (agentRun.value.episodes || []).filter((episode) =>
    Array.isArray(episode[field]) && episode[field].map(String).includes(String(value))
  )
const findToolTraceByPermission = (value = '', event = selectedLedgerEvent.value || {}) =>
  (agentRun.value.toolTraces || []).find((trace) => trace.permission === value) ||
  detailField(event, 'toolDetails').find((trace) => trace.permission === value)
const findToolTracesByPermission = (value = '', event = selectedLedgerEvent.value || {}) => {
  const traces = [
    ...(agentRun.value.toolTraces || []).filter((trace) => trace.permission === value),
    ...detailField(event, 'toolDetails').filter((trace) => trace.permission === value)
  ]
  const seen = new Set()
  return traces.filter((trace) => {
    const key = trace.id || trace.name || `${trace.permission}-${trace.branchId || ''}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}
const findGateResult = (value = '', event = selectedLedgerEvent.value || {}) =>
  detailById(gatesForEvent(event), value) ||
  allGateDetails.value.find((gate) => gate.id === value)
const findArtifactDetail = (value = '', event = selectedLedgerEvent.value || {}) =>
  detailById(artifactsForEvent(event), value) ||
  allArtifactDetails.value.find((artifact) => artifact.id === value)
const findSkillProposal = (value = '') =>
  (agentRun.value.skillProposals || []).find((skill) => skill.id === value) || null
const findSkillByEvidenceRun = (value = '') =>
  (agentRun.value.skillProposals || []).find((skill) =>
    Array.isArray(skill.evidenceRunIds) && skill.evidenceRunIds.map(String).includes(value)
  )
const skillBranchId = computed(() =>
  worldlineStore.branches.find((branch) => branch.branchType === 'skill_proposal')?.id || ''
)
const skillSourceBranchId = (skill = {}) =>
  skill.sourceBranchId || skill.branchId || skillBranchId.value || ''
const skillSourceBranchTitle = (skill = {}) => {
  const branchId = skillSourceBranchId(skill)
  return branchId ? eventBranchTitle(branchId) : 'run scope'
}
const skillsForBranch = (branchId = '') =>
  (agentRun.value.skillProposals || []).filter((skill) => skillSourceBranchId(skill) === branchId)

const dedupeGates = (items = []) => {
  const seen = new Set()
  return items
    .map((item) => normalizeGateDetail(item))
    .filter((item) => {
      if (!item.id || seen.has(item.id)) return false
      seen.add(item.id)
      return true
    })
}
const allGateDetails = computed(() => dedupeGates(agentRun.value.gateResults || []))
const gateDetailsForIds = (gateIds = [], fallbackDetails = []) => {
  const localById = new Map(allGateDetails.value.map((gate) => [gate.id, gate]))
  const fallbackById = new Map(fallbackDetails.map((gate) => [gate.id, gate]))
  return uniqueStrings(gateIds).map((gateId) =>
    normalizeGateDetail(
      mergeArtifactDetail(
        localById.get(gateId) || {},
        fallbackById.get(gateId) || (localById.has(gateId)
          ? {}
          : {
              id: gateId,
              label: gateId,
              summary: '该质量门当前只有结构化 ID，等待后端补充 gateDetails。'
            })
      )
    )
  )
}
const gatesForEvent = (event = {}) => {
  const detailItems = dedupeGates(detailField(event, 'gateDetails'))
  const detailIds = detailItems.map((gate) => gate.id)
  return gateDetailsForIds(uniqueStrings([...listField(event, 'gateResultIds'), ...detailIds]), detailItems)
}
const activeGateDetails = computed(() => {
  const activeGateIds = uniqueStrings([
    ...(worldlineStore.activeBranch?.gateResultIds || []),
    ...activeEpisodes.value.flatMap((episode) => episode.gateResults || [])
  ])
  return gateDetailsForIds(activeGateIds)
})
const selectedEventGateDetails = computed(() =>
  selectedLedgerEvent.value ? gatesForEvent(selectedLedgerEvent.value) : []
)
const visibleGateDetails = computed(() => {
  const scopes = {
    branch: activeGateDetails.value,
    event: selectedEventGateDetails.value,
    all: allGateDetails.value
  }
  return scopes[gateScope.value] || activeGateDetails.value
})
const gateScopeOptions = computed(() => [
  { id: 'branch', label: 'Branch', count: activeGateDetails.value.length },
  { id: 'event', label: 'Event', count: selectedEventGateDetails.value.length },
  { id: 'all', label: 'All', count: allGateDetails.value.length }
])

const dedupeArtifacts = (items = []) => {
  const seen = new Set()
  return items
    .map((item) => normalizeArtifactDetail(item))
    .filter((item) => {
      if (!item.id || seen.has(item.id)) return false
      seen.add(item.id)
      return true
    })
}
const mergeArtifactDetail = (base = {}, override = {}) => {
  const merged = { ...base }
  Object.entries(override).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      merged[key] = value
    }
  })
  return merged
}
const allArtifactDetails = computed(() =>
  dedupeArtifacts([
    ...summarizeArtifactsForTraces(agentRun.value.toolTraces || []),
    ...savedReplayArtifacts.value.map(normalizeRegistryArtifactDetail)
  ])
)
const artifactDetailsForIds = (artifactIds = [], fallbackDetails = []) => {
  const localById = new Map(allArtifactDetails.value.map((artifact) => [artifact.id, artifact]))
  const fallbackById = new Map(fallbackDetails.map((artifact) => [artifact.id, artifact]))
  return uniqueStrings(artifactIds).map((artifactId) => {
    const fallback = fallbackById.get(artifactId)
    const local = localById.get(artifactId)
    const trace = fallback?.toolCallId ? findToolTrace(fallback.toolCallId) : null
    return normalizeArtifactDetail(
      mergeArtifactDetail(local || {}, fallback || (local
        ? {}
        : {
            id: artifactId,
            label: artifactId,
            summary: '该产物当前只有结构化 ID，等待后端补充 artifactDetails。'
          })),
      trace || {}
    )
  })
}
const artifactsForEvent = (event = {}) => {
  const detailItems = dedupeArtifacts(detailField(event, 'artifactDetails'))
  const detailIds = detailItems.map((artifact) => artifact.id)
  return artifactDetailsForIds(uniqueStrings([...listField(event, 'artifactIds'), ...detailIds]), detailItems)
}
const activeArtifactDetails = computed(() => {
  const activeIds = uniqueStrings([
    ...activeToolTraces.value.flatMap(toolTraceArtifactIds),
    ...activeEpisodes.value.flatMap((episode) => episode.artifactIds || [])
  ])
  return artifactDetailsForIds(activeIds)
})
const selectedEventArtifactDetails = computed(() =>
  selectedLedgerEvent.value ? artifactsForEvent(selectedLedgerEvent.value) : []
)
const visibleArtifactDetails = computed(() => {
  const scopes = {
    branch: activeArtifactDetails.value,
    event: selectedEventArtifactDetails.value,
    all: allArtifactDetails.value
  }
  return scopes[artifactScope.value] || activeArtifactDetails.value
})
const artifactScopeOptions = computed(() => [
  { id: 'branch', label: 'Branch', count: activeArtifactDetails.value.length },
  { id: 'event', label: 'Event', count: selectedEventArtifactDetails.value.length },
  { id: 'all', label: 'All', count: allArtifactDetails.value.length }
])

const resolveEventTokenTarget = (sectionKey = '', value = '', event = selectedLedgerEvent.value || {}) => {
  if (sectionKey === 'branch') {
    const branch = findBranchById(value)
    return {
      canFocus: Boolean(branch),
      targetType: 'branch',
      targetId: branch?.id || value,
      branchId: branch?.id || ''
    }
  }

  if (sectionKey === 'episode') {
    const episode = findEpisode(value)
    return {
      canFocus: Boolean(episode),
      targetType: 'episode',
      targetId: episode?.id || value,
      branchId: episode?.branchId || ''
    }
  }

  if (sectionKey === 'skill') {
    const skill = findSkillProposal(value)
    return {
      canFocus: Boolean(skill),
      targetType: 'skill',
      targetId: skill?.id || value,
      branchId: skill ? skillSourceBranchId(skill) : skillBranchId.value
    }
  }

  if (sectionKey === 'evidence') {
    const evidence = findEvidenceRef(value)
    return {
      canFocus: Boolean(evidence),
      targetType: 'evidence',
      targetId: evidence ? itemStableId(evidence) : value,
      layer: 'evidence',
      branchId: findBranchForToken('evidenceIds', value)?.id || ''
    }
  }

  if (sectionKey === 'tool') {
    const trace = findToolTrace(value, event)
    return {
      canFocus: Boolean(trace),
      targetType: 'tool',
      targetId: trace?.id || value,
      branchId: trace?.branchId || ''
    }
  }

  if (sectionKey === 'timeline') {
    const fact = findTimelineRef(value)
    return {
      canFocus: Boolean(fact),
      targetType: 'timeline',
      targetId: fact?.id || value,
      layer: 'timeline',
      branchId: findBranchForToken('temporalFactIds', value)?.id || ''
    }
  }

  if (sectionKey === 'permission') {
    const trace = findToolTraceByPermission(value, event)
    return {
      canFocus: Boolean(trace),
      targetType: 'permission',
      targetId: value,
      branchId: trace?.branchId || ''
    }
  }

  if (sectionKey === 'gate') {
    const gate = findGateResult(value, event)
    return {
      canFocus: Boolean(gate),
      targetType: 'gate',
      targetId: gate?.id || value,
      branchId: gate?.branchId || findBranchForToken('gateResultIds', value)?.id || ''
    }
  }

  if (sectionKey === 'artifact') {
    const artifact = findArtifactDetail(value, event)
    const trace = artifact?.toolCallId ? findToolTrace(artifact.toolCallId, event) : null
    return {
      canFocus: Boolean(artifact),
      targetType: 'artifact',
      targetId: artifact?.id || value,
      branchId: trace?.branchId || ''
    }
  }

  if (sectionKey === 'run-evidence') {
    const skill = findSkillByEvidenceRun(value)
    return {
      canFocus: Boolean(skill),
      targetType: 'skill',
      targetId: skill?.id || value,
      branchId: skill ? skillSourceBranchId(skill) : skillBranchId.value
    }
  }

  return {
    canFocus: false,
    targetType: sectionKey,
    targetId: value,
    branchId: ''
  }
}

const makeEventDetailItems = (event = {}, sectionKey = '', summaryKey = '') =>
  listField(event, summaryKey).map((value) => {
    const target = resolveEventTokenTarget(sectionKey, value, event)
    return {
      id: value,
      label: value,
      sectionKey,
      token: `${sectionKey}:${value}`,
      ...target
    }
  })

const eventDetailSections = (event = {}) => [
  { key: 'branch', label: 'Branches', items: makeEventDetailItems(event, 'branch', 'branch_ids') },
  { key: 'episode', label: 'Episodes', items: makeEventDetailItems(event, 'episode', 'episodeIds') },
  { key: 'skill', label: 'Skill Proposals', items: makeEventDetailItems(event, 'skill', 'skillProposalIds') },
  { key: 'evidence', label: 'Linked Evidence', items: makeEventDetailItems(event, 'evidence', 'evidenceIds') },
  { key: 'tool', label: 'Tool Calls', items: makeEventDetailItems(event, 'tool', 'toolCallIds') },
  { key: 'timeline', label: 'Timeline Facts', items: makeEventDetailItems(event, 'timeline', 'temporalFactIds') },
  { key: 'gate', label: 'Quality Gates', items: makeEventDetailItems(event, 'gate', 'gateResultIds') },
  { key: 'artifact', label: 'Artifacts', items: makeEventDetailItems(event, 'artifact', 'artifactIds') },
  { key: 'permission', label: 'Permissions', items: makeEventDetailItems(event, 'permission', 'requiredPermissions') },
  { key: 'run-evidence', label: 'Evidence Runs', items: makeEventDetailItems(event, 'run-evidence', 'evidenceRunIds') }
]

const eventTypeLabel = (eventType = '') => {
  const labels = {
    'run.created': 'Run Created',
    'run.previewed': 'Run Preview',
    'branch.approved': 'Branch Approved',
    'branch.rejected': 'Branch Rejected',
    'branch.focused': 'Branch Focused',
    'tool.pending': 'Tool Pending',
    'skill.proposed': 'Skill Proposed',
    'skill.candidate': 'Skill Candidate',
    'artifact.registered': 'Artifact Registered'
  }
  return labels[eventType] || formatSummaryKey(eventType || 'event')
}

const formatEventTime = (value = '') => {
  if (!value) return 'now'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const eventBranchTitle = (branchId = '') =>
  worldlineStore.branches.find((branch) => branch.id === branchId)?.title || branchId

const compactList = (items = []) => items.filter(Boolean).map(String)
const joinList = (items = [], fallback = 'none') => {
  const values = compactList(items)
  return values.length ? values.join(' / ') : fallback
}
const makeDossierLink = ({
  label = '',
  targetType = '',
  targetId = '',
  branchId = '',
  layer = '',
  token = '',
  canFocus = true
} = {}) => ({
  label: label || targetId,
  targetType,
  targetId,
  branchId,
  layer,
  token: token || (targetType && targetId ? `${targetType}:${targetId}` : ''),
  canFocus: Boolean(canFocus && targetType && targetId)
})
const normalizeDossierItems = (items = []) =>
  items
    .filter(Boolean)
    .map((item, index) => {
      if (typeof item === 'string') {
        const label = item.trim()
        if (!label) return null
        return {
          key: `text:${label}:${index}`,
          label,
          targetType: '',
          targetId: '',
          branchId: '',
          layer: '',
          token: '',
          canFocus: false
        }
      }

      const targetId = String(item.targetId || item.id || '').trim()
      const targetType = String(item.targetType || '').trim()
      const label = String(item.label || targetId || '').trim()
      if (!label) return null

      return {
        key: item.key || `${targetType || 'item'}:${targetId || label}:${index}`,
        label,
        targetType,
        targetId,
        branchId: item.branchId || '',
        layer: item.layer || '',
        token: item.token || (targetType && targetId ? `${targetType}:${targetId}` : ''),
        canFocus: Boolean(item.canFocus && targetType && targetId)
      }
    })
    .filter(Boolean)
const dossierToolLink = (toolId = '', fallbackBranchId = '') => {
  const trace = findToolTrace(toolId)
  return makeDossierLink({
    label: `Tool: ${trace?.name || toolId}`,
    targetType: 'tool',
    targetId: trace?.id || toolId,
    branchId: trace?.branchId || fallbackBranchId,
    canFocus: Boolean(trace)
  })
}
const dossierArtifactLink = (artifactId = '', fallbackBranchId = '') => {
  const artifact = findArtifactDetail(artifactId)
  return makeDossierLink({
    label: `Artifact: ${artifact?.label || artifactId}`,
    targetType: 'artifact',
    targetId: artifact?.id || artifactId,
    branchId: artifact?.branchId || fallbackBranchId,
    canFocus: Boolean(artifact)
  })
}
const dossierBranchLink = (branchId = '') => {
  const branch = findBranchById(branchId)
  return makeDossierLink({
    label: `Branch: ${branch?.title || branchId}`,
    targetType: 'branch',
    targetId: branch?.id || branchId,
    branchId: branch?.id || branchId,
    canFocus: Boolean(branch)
  })
}
const dossierGateLink = (gateId = '', fallbackBranchId = '') => {
  const gate = findGateResult(gateId)
  return makeDossierLink({
    label: `Gate: ${gate?.label || gateId}`,
    targetType: 'gate',
    targetId: gate?.id || gateId,
    branchId: gate?.branchId || fallbackBranchId,
    canFocus: Boolean(gate)
  })
}
const dossierEpisodeLink = (episodeId = '', fallbackBranchId = '') => {
  const episode = findEpisode(episodeId)
  return makeDossierLink({
    label: `Episode: ${episode?.actor || episodeId}`,
    targetType: 'episode',
    targetId: episode?.id || episodeId,
    branchId: episode?.branchId || fallbackBranchId,
    canFocus: Boolean(episode)
  })
}
const dossierPermissionLink = (permission = '', fallbackBranchId = '') => {
  const trace = findToolTraceByPermission(permission)
  return makeDossierLink({
    label: `Permission: ${permission}`,
    targetType: 'permission',
    targetId: permission,
    branchId: trace?.branchId || fallbackBranchId,
    canFocus: Boolean(trace)
  })
}
const dossierEvidenceLink = (evidenceId = '', fallbackBranchId = '') => {
  const evidence = findEvidenceRef(evidenceId)
  return makeDossierLink({
    label: `Evidence: ${evidence?.title || evidence?.evidenceId || evidenceId}`,
    targetType: 'evidence',
    targetId: evidence ? String(evidence.evidenceId || evidence.id || evidenceId) : evidenceId,
    branchId: fallbackBranchId || findBranchForToken('evidenceIds', evidenceId)?.id || '',
    layer: 'evidence',
    canFocus: Boolean(evidence)
  })
}
const dossierGraphLink = (entityId = '', fallbackBranchId = '') => {
  const entity = findEntityRef(entityId)
  return makeDossierLink({
    label: `Graph: ${entity?.name || entityId}`,
    targetType: 'graph',
    targetId: entity ? String(entity.id || entity.name || entityId) : entityId,
    branchId: fallbackBranchId,
    layer: 'graph',
    canFocus: Boolean(entity)
  })
}
const dossierTimelineLink = (factId = '', fallbackBranchId = '') => {
  const fact = findTimelineRef(factId)
  return makeDossierLink({
    label: `Time: ${fact?.label || factId}`,
    targetType: 'timeline',
    targetId: fact ? String(fact.id || fact.label || factId) : factId,
    branchId: fallbackBranchId || findBranchForToken('temporalFactIds', factId)?.id || '',
    layer: 'timeline',
    canFocus: Boolean(fact)
  })
}
const dossierWikiLink = (wikiId = '', fallbackBranchId = '') => {
  const wiki = findWikiRef(wikiId)
  return makeDossierLink({
    label: `Wiki: ${wiki?.title || wiki?.slug || wikiId}`,
    targetType: 'wiki',
    targetId: wiki ? String(wiki.id || wiki.slug || wikiId) : wikiId,
    branchId: fallbackBranchId,
    layer: 'wiki',
    canFocus: Boolean(wiki)
  })
}
const sourceLineRange = (item = {}) => {
  if (item.lineStart && item.lineEnd) return `${item.lineStart}-${item.lineEnd}`
  if (item.lineStart) return String(item.lineStart)
  return ''
}
const sourceLocationLabel = (item = {}) => {
  const sourceUri = item.sourceUri || item.sourceRef?.sourceUri || ''
  const lineRange = sourceLineRange(item)
  return [sourceUri, lineRange ? `line ${lineRange}` : ''].filter(Boolean).join(': ')
}
const dossierSourceLink = (evidenceOrId = '', fallbackBranchId = '') => {
  const evidence = typeof evidenceOrId === 'object' ? evidenceOrId : findEvidenceRef(evidenceOrId)
  const targetId = evidence ? sourceTargetId(evidence) : String(evidenceOrId || '')
  const branchId = fallbackBranchId ||
    findBranchForToken('evidenceIds', evidence?.evidenceId || evidence?.id || targetId)?.id ||
    ''
  return makeDossierLink({
    label: `Source: ${sourceLocationLabel(evidence) || evidence?.sourceRef?.label || targetId}`,
    targetType: 'source',
    targetId,
    branchId,
    canFocus: Boolean(evidence?.sourceUri)
  })
}
const evidenceLocation = (item = {}) => {
  const parts = []
  if (item.sourceUri) parts.push(item.sourceUri)
  if (item.page) parts.push(`page ${item.page}`)
  if (item.lineStart && item.lineEnd) parts.push(`line ${item.lineStart}-${item.lineEnd}`)
  else if (item.lineStart) parts.push(`line ${item.lineStart}`)
  return parts.join(' / ') || 'metadata only'
}
const relatedEntitiesForEvidence = (evidenceId = '') =>
  worldlineStore.entityRefs.filter((entity) => entity.evidenceId === evidenceId)
const relatedTimelineForEvidence = (evidenceId = '') =>
  worldlineStore.timelineRefs.filter((fact) => fact.evidenceId === evidenceId)
const branchTitleForToolTrace = (trace = {}) =>
  trace.branchId ? eventBranchTitle(trace.branchId) : 'run scope'
const branchTitleForEpisode = (episode = {}) =>
  episode.branchId ? eventBranchTitle(episode.branchId) : 'run scope'
const branchEpisodes = (branchId = '') =>
  (agentRun.value.episodes || []).filter((episode) => episode.branchId === branchId)
const branchToolTraces = (branch = {}) => {
  const toolIds = uniqueStrings(branch.toolCallIds || [])
  return (agentRun.value.toolTraces || []).filter((trace) =>
    trace.branchId === branch.id || toolIds.includes(trace.id)
  )
}
const branchGateIdsForManifest = (branch = {}) =>
  uniqueStrings([
    ...(branch.gateResultIds || []),
    ...branchEpisodes(branch.id).flatMap((episode) => episode.gateResults || [])
  ])
const branchArtifactIdsForManifest = (branch = {}) =>
  uniqueStrings([
    ...branchToolTraces(branch).flatMap(toolTraceArtifactIds),
    ...branchEpisodes(branch.id).flatMap((episode) => episode.artifactIds || [])
  ])
const runSummaryBranchIds = (summary = {}) =>
  uniqueStrings(summary.branch_ids || summary.branchIds || worldlineStore.branches.map((branch) => branch.id))
const runSummaryEpisodeIds = (summary = {}) =>
  uniqueStrings(summary.episodeIds || (agentRun.value.episodes || []).map((episode) => episode.id))
const runSummarySkillIds = (summary = {}) =>
  uniqueStrings(summary.skillProposalIds || summary.skill_proposal_ids || (agentRun.value.skillProposals || []).map((skill) => skill.id))
const runSummaryEpisodeCount = (summary = {}) =>
  summary.episode_count ?? countList(runSummaryEpisodeIds(summary))
const runSummarySkillCount = (summary = {}) =>
  summary.skill_proposal_count ?? countList(runSummarySkillIds(summary))
const formatEpisodeDiff = (diff = {}, index = 0) => {
  if (typeof diff === 'string') return `Diff: ${diff}`
  const label = diff.path || diff.file || `diff-${index + 1}`
  const status = diff.status ? ` (${diff.status})` : ''
  const summary = diff.summary || diff.description || ''
  return `Diff: ${label}${status}${summary ? ` - ${summary}` : ''}`
}
const formatEpisodeScreenshot = (screenshot = {}, index = 0) => {
  if (typeof screenshot === 'string') return `Screenshot: ${screenshot}`
  const label = screenshot.path || screenshot.uri || `screenshot-${index + 1}`
  const viewport = screenshot.viewport ? ` [${screenshot.viewport}]` : ''
  const summary = screenshot.summary || screenshot.description || ''
  return `Screenshot: ${label}${viewport}${summary ? ` - ${summary}` : ''}`
}
const skillLinkedEpisodeIds = (skill = {}) =>
  uniqueStrings([
    ...(skill.episodeIds || []),
    ...(skill.gateResultIds || []).flatMap((gateId) => episodesForToken('gateResults', gateId).map((episode) => episode.id)),
    ...(skill.artifactIds || []).flatMap((artifactId) => episodesForToken('artifactIds', artifactId).map((episode) => episode.id))
  ])
const branchEvidenceIds = (branch = {}) => {
  const explicitIds = uniqueStrings(branch.evidenceIds || [])
  if (explicitIds.length) return explicitIds
  return uniqueStrings((branch.evidenceRefs || []).map((item) => item.evidenceId || item.id))
}
const branchTimelineIds = (branch = {}) => {
  const explicitIds = uniqueStrings(branch.temporalFactIds || [])
  if (explicitIds.length) return explicitIds
  return uniqueStrings((branch.timelineRefs || []).map((item) => item.id))
}
const branchWikiIds = (branch = {}) =>
  uniqueStrings((branch.wikiRefs || []).map((item) => item.id || item.slug))
const branchGraphIds = (branch = {}) =>
  uniqueStrings((branch.entityRefs || []).map((item) => item.id || item.name))
const selectedEventContainsGate = (gateId = '') =>
  Boolean(gateId && listField(selectedLedgerEvent.value || {}, 'gateResultIds').includes(gateId))
const gateSupportSummary = (gate = {}) => {
  const sourceBranch = findBranchById(gate.branchId) || findBranchForToken('gateResultIds', gate.id) || {}
  const branchId = sourceBranch.id || gate.branchId || ''
  const sourceEvidenceIds = branchEvidenceIds(sourceBranch)
  const sourceTimelineIds = branchTimelineIds(sourceBranch)
  const fallbackEvidenceIds = selectedEventContainsGate(gate.id)
    ? listField(selectedLedgerEvent.value || {}, 'evidenceIds')
    : []
  const fallbackTimelineIds = selectedEventContainsGate(gate.id)
    ? listField(selectedLedgerEvent.value || {}, 'temporalFactIds')
    : []
  const evidenceIds = uniqueStrings(sourceEvidenceIds.length ? sourceEvidenceIds : fallbackEvidenceIds)
    .filter((evidenceId) => Boolean(findEvidenceRef(evidenceId)))
  const timelineIds = uniqueStrings(sourceTimelineIds.length ? sourceTimelineIds : fallbackTimelineIds)
    .filter((factId) => Boolean(findTimelineRef(factId)))
  const entityIds = uniqueStrings(
    evidenceIds.flatMap((evidenceId) => relatedEntitiesForEvidence(evidenceId).map((entity) => entity.id || entity.name))
  ).filter((entityId) => Boolean(findEntityRef(entityId)))
  const sourceIds = uniqueStrings(
    evidenceIds
      .map((evidenceId) => findEvidenceRef(evidenceId))
      .filter((evidence) => evidence?.sourceUri)
      .map(sourceTargetId)
  )

  return {
    branchId,
    branchTitle: sourceBranch.title || (branchId ? eventBranchTitle(branchId) : 'selected event'),
    evidenceIds,
    sourceIds,
    timelineIds,
    entityIds
  }
}

const makeDossier = ({ type = '', title = '', badge = '', summary = '', meta = [], items = [] } = {}) => ({
  type,
  title: title || 'Focused target',
  badge: badge || type || 'focus',
  summary: summary || '该目标当前只有结构化 ID，等待后端补充更多详情。',
  meta: meta.filter((item) => item?.value !== undefined && item?.value !== null && item.value !== ''),
  items: normalizeDossierItems(items)
})

const buildFocusedDossier = (focus = {}) => {
  if (!focus.type || !focus.id) return null

  if (focus.type === 'run') {
    const event = findRunManifestEvent(focus.id)
    if (!event) return null
    const summary = event.summary || {}
    const branchIds = runSummaryBranchIds(summary)
    const episodeIds = runSummaryEpisodeIds(summary)
    const skillIds = runSummarySkillIds(summary)
    const gateIds = uniqueStrings(summary.gateResultIds || (agentRun.value.gateResults || []).map((gate) => gate.id))
    const artifactIds = uniqueStrings(summary.artifactIds || (agentRun.value.toolTraces || []).flatMap(toolTraceArtifactIds))
    return makeDossier({
      type: 'run',
      title: summary.title || run.value.title || event.runId || event.id,
      badge: 'Replay Manifest',
      summary: 'This manifest turns the run event summary into a replayable worldline ledger across branches, episodes, gates, artifacts, and skill proposals.',
      meta: [
        { label: 'Run ID', value: event.runId || run.value.id },
        { label: 'Event ID', value: event.id },
        { label: 'Branches', value: summary.branch_count ?? branchIds.length },
        { label: 'Episodes', value: runSummaryEpisodeCount(summary) },
        { label: 'Skills', value: runSummarySkillCount(summary) },
        { label: 'Evidence', value: summary.evidence_count ?? countList(summary.evidenceIds) },
        { label: 'Tools', value: summary.tool_count ?? countList(summary.toolCallIds) },
        { label: 'Timeline Facts', value: summary.temporal_fact_count ?? countList(summary.temporalFactIds) },
        { label: 'Gates', value: countList(gateIds) },
        { label: 'Artifacts', value: countList(artifactIds) }
      ],
      items: [
        ...branchIds.map(dossierBranchLink),
        ...episodeIds.map((episodeId) => dossierEpisodeLink(episodeId)),
        ...skillIds.map((skillId) => {
          const skill = findSkillProposal(skillId)
          return makeDossierLink({
            label: `Skill: ${skill?.name || skillId}`,
            targetType: 'skill',
            targetId: skill?.id || skillId,
            branchId: skill ? skillSourceBranchId(skill) : '',
            canFocus: Boolean(skill)
          })
        }),
        ...gateIds.map((gateId) => dossierGateLink(gateId)),
        ...artifactIds.map((artifactId) => dossierArtifactLink(artifactId))
      ]
    })
  }

  if (focus.type === 'branch') {
    const branch = findBranchById(focus.id)
    if (!branch) return null
    const branchEvidence = branchEvidenceIds(branch)
    const branchWiki = branchWikiIds(branch)
    const branchGraph = branchGraphIds(branch)
    const branchTimeline = branchTimelineIds(branch)
    const branchTools = branchToolTraces(branch)
    const branchEpisodeItems = branchEpisodes(branch.id)
    const gateIds = branchGateIdsForManifest(branch)
    const artifactIds = branchArtifactIdsForManifest(branch)
    const branchSkills = skillsForBranch(branch.id)
    return makeDossier({
      type: 'branch',
      title: branch.title || branch.id,
      badge: branch.status || branch.quality?.status || 'Branch',
      summary: branch.choiceReason || branch.hypothesis || branch.subtitle || 'This branch is part of the replayable worldline run.',
      meta: [
        { label: 'Branch ID', value: branch.id },
        { label: 'Type', value: branch.branchType || branch.choiceLabel || '' },
        { label: 'Status', value: branch.status || branch.quality?.status || '' },
        { label: 'Score', value: formatDecisionScore(branch.score) },
        { label: 'Evidence', value: branchEvidence.length },
        { label: 'Wiki', value: branchWiki.length },
        { label: 'Graph', value: branchGraph.length },
        { label: 'Timeline', value: branchTimeline.length },
        { label: 'Tools', value: branchTools.length },
        { label: 'Gates', value: gateIds.length },
        { label: 'Artifacts', value: artifactIds.length },
        { label: 'Episodes', value: branchEpisodeItems.length },
        { label: 'Skills', value: branchSkills.length }
      ],
      items: [
        ...branchEvidence.map((evidenceId) => dossierEvidenceLink(evidenceId, branch.id)),
        ...branchWiki.map((wikiId) => dossierWikiLink(wikiId, branch.id)),
        ...branchGraph.map((entityId) => dossierGraphLink(entityId, branch.id)),
        ...branchTimeline.map((factId) => dossierTimelineLink(factId, branch.id)),
        ...branchTools.map((trace) => dossierToolLink(trace.id, branch.id)),
        ...gateIds.map((gateId) => dossierGateLink(gateId, branch.id)),
        ...artifactIds.map((artifactId) => dossierArtifactLink(artifactId, branch.id)),
        ...branchEpisodeItems.map((episode) => dossierEpisodeLink(episode.id, branch.id)),
        ...branchSkills.map((skill) => makeDossierLink({
          label: `Skill: ${skill.name || skill.id}`,
          targetType: 'skill',
          targetId: skill.id,
          branchId: skillSourceBranchId(skill),
          canFocus: Boolean(skill.id)
        }))
      ]
    })
  }

  if (focus.type === 'evidence') {
    const evidence = findEvidenceRef(focus.id)
    if (!evidence) return null
    const relatedEntities = relatedEntitiesForEvidence(evidence.evidenceId || evidence.id)
    const relatedFacts = relatedTimelineForEvidence(evidence.evidenceId || evidence.id)
    return makeDossier({
      type: 'evidence',
      title: evidence.title || evidence.evidenceId || evidence.id,
      badge: evidence.typeLabel || evidence.type || 'Evidence',
      summary: evidence.summary,
      meta: [
        { label: 'Evidence ID', value: evidence.evidenceId || evidence.id },
        { label: 'Source', value: evidence.sourceUri || 'metadata only' },
        { label: 'Location', value: evidenceLocation(evidence) },
        { label: 'Graph Links', value: relatedEntities.length },
        { label: 'Timeline Links', value: relatedFacts.length }
      ],
      items: [
        dossierSourceLink(evidence, focus.branchId || findBranchForToken('evidenceIds', evidence.evidenceId || evidence.id)?.id || ''),
        ...relatedEntities.map((entity) => dossierGraphLink(entity.id || entity.name)),
        ...relatedFacts.map((fact) => dossierTimelineLink(fact.id))
      ]
    })
  }

  if (focus.type === 'source') {
    const evidence = findSourceEvidence(focus.id)
    if (!evidence) return null
    const sourceRef = evidence.sourceRef || {}
    const sourceId = sourceTargetId(evidence)
    const relatedEntities = relatedEntitiesForEvidence(evidence.evidenceId || evidence.id)
    const relatedFacts = relatedTimelineForEvidence(evidence.evidenceId || evidence.id)
    return makeDossier({
      type: 'source',
      title: sourceRef.label || evidence.sourceUri || evidence.title || sourceId,
      badge: sourceRef.kind || 'SourceAsset',
      summary: sourceRef.role || evidence.summary || 'This source anchor points to the file-level context behind the selected evidence.',
      meta: [
        { label: 'Source Asset', value: sourceRef.id || sourceId },
        { label: 'Source URI', value: evidence.sourceUri || 'metadata only' },
        { label: 'Line Range', value: sourceLineRange(evidence) || 'not recorded' },
        { label: 'Document Node', value: sourceRef.documentNodeLabel || sourceRef.documentNodeId || 'line anchor' },
        { label: 'Capability', value: sourceRef.capability || '' },
        { label: 'Evidence Anchor', value: evidence.evidenceId || evidence.id }
      ],
      items: [
        dossierEvidenceLink(evidence.evidenceId || evidence.id, focus.branchId || ''),
        ...relatedEntities.map((entity) => dossierGraphLink(entity.id || entity.name, focus.branchId || '')),
        ...relatedFacts.map((fact) => dossierTimelineLink(fact.id, focus.branchId || ''))
      ]
    })
  }

  if (focus.type === 'graph') {
    const entity = findEntityRef(focus.id)
    if (!entity) return null
    const evidence = entity.evidenceId ? findEvidenceRef(entity.evidenceId) : null
    return makeDossier({
      type: 'graph',
      title: entity.name || entity.id,
      badge: entity.type || 'Graph Entity',
      summary: entity.summary || (entity.confidence
        ? `Knowledge graph entity with ${Math.round(entity.confidence * 100)}% confidence.`
        : 'This entity is linked into the active branch evidence graph.'),
      meta: [
        { label: 'Entity ID', value: entity.id },
        { label: 'Type', value: entity.type || 'entity' },
        { label: 'Confidence', value: entity.confidence ? `${Math.round(entity.confidence * 100)}%` : 'not scored' },
        { label: 'Evidence', value: entity.evidenceId || 'none' }
      ],
      items: [
        evidence ? dossierEvidenceLink(entity.evidenceId) : ''
      ]
    })
  }

  if (focus.type === 'wiki') {
    const wiki = findWikiRef(focus.id)
    if (!wiki) return null
    return makeDossier({
      type: 'wiki',
      title: wiki.title || wiki.slug || wiki.id,
      badge: wiki.status || 'Wiki',
      summary: wiki.summary || 'This wiki page explains the active worldline branch.',
      meta: [
        { label: 'Wiki ID', value: wiki.id },
        { label: 'Slug', value: wiki.slug || '' },
        { label: 'Status', value: wiki.status || 'draft' },
        { label: 'Evidence Coverage', value: wiki.evidenceCoverage ? `${Math.round(wiki.evidenceCoverage * 100)}%` : 'not scored' }
      ],
      items: [
        wiki.slug ? `Slug: ${wiki.slug}` : ''
      ]
    })
  }

  if (focus.type === 'tool') {
    const trace = findToolTrace(focus.id)
    if (!trace) return null
    const linkedEpisodes = episodesForToken('toolCalls', trace.id)
    return makeDossier({
      type: 'tool',
      title: trace.name || trace.id,
      badge: trace.status || 'Tool',
      summary: trace.summary,
      meta: [
        { label: 'Tool ID', value: trace.id },
        { label: 'Permission', value: trace.permission || 'read' },
        { label: 'Branch', value: branchTitleForToolTrace(trace) },
        { label: 'Result', value: trace.result || 'pending' }
      ],
      items: [
        trace.permission ? `Permission: ${trace.permission}` : '',
        trace.failureReason ? `Failure: ${trace.failureReason}` : '',
        ...linkedEpisodes.map((episode) => dossierEpisodeLink(episode.id, trace.branchId || '')),
        ...toolTraceArtifactIds(trace).map((artifactId) => dossierArtifactLink(artifactId, trace.branchId || ''))
      ]
    })
  }

  if (focus.type === 'episode') {
    const episode = findEpisode(focus.id)
    if (!episode) return null
    return makeDossier({
      type: 'episode',
      title: `Episode Replay: ${episode.actor || episode.id}`,
      badge: branchTitleForEpisode(episode),
      summary: episode.output || 'This AgentEpisode records one replayable step in the active worldline run.',
      meta: [
        { label: 'Episode ID', value: episode.id },
        { label: 'Actor', value: episode.actor || 'agent' },
        { label: 'Branch', value: branchTitleForEpisode(episode) },
        { label: 'Input', value: episode.input || '' },
        { label: 'Tools', value: countList(episode.toolCalls) },
        { label: 'Gates', value: countList(episode.gateResults) },
        { label: 'Artifacts', value: countList(episode.artifactIds) },
        { label: 'Diffs', value: countList(episode.diffs) },
        { label: 'Screenshots', value: countList(episode.screenshots) },
        { label: 'Cost', value: formatEpisodeCost(episode.cost) }
      ],
      items: [
        ...(episode.toolCalls || []).map((toolId) => dossierToolLink(toolId, episode.branchId || '')),
        ...(episode.gateResults || []).map((gateId) => dossierGateLink(gateId, episode.branchId || '')),
        ...(episode.artifactIds || []).map((artifactId) => dossierArtifactLink(artifactId, episode.branchId || '')),
        ...(episode.diffs || []).map(formatEpisodeDiff),
        ...(episode.screenshots || []).map(formatEpisodeScreenshot)
      ]
    })
  }

  if (focus.type === 'permission') {
    const traces = findToolTracesByPermission(focus.id)
    if (!traces.length) return null
    return makeDossier({
      type: 'permission',
      title: focus.id,
      badge: 'Permission',
      summary: `${traces.length} tool call${traces.length > 1 ? 's' : ''} require this permission in the current run.`,
      meta: [
        { label: 'Permission', value: focus.id },
        { label: 'Tool Calls', value: traces.length },
        { label: 'Branches', value: joinList(Array.from(new Set(traces.map((trace) => branchTitleForToolTrace(trace))))) }
      ],
      items: traces.map((trace) => makeDossierLink({
        label: `Tool: ${trace.name || trace.id}`,
        targetType: 'tool',
        targetId: trace.id,
        branchId: trace.branchId || '',
        canFocus: Boolean(trace.id)
      }))
    })
  }

  if (focus.type === 'gate') {
    const gate = findGateResult(focus.id)
    if (!gate) return null
    const support = gateSupportSummary(gate)
    const linkedEpisodes = episodesForToken('gateResults', gate.id)
    return makeDossier({
      type: 'gate',
      title: gate.label || gate.name || gate.id,
      badge: gate.status || 'Gate',
      summary: gate.summary || gate.description || '该质量门已绑定到当前事件，用于判断分支是否能继续推进。',
      meta: [
        { label: 'Gate ID', value: gate.id },
        { label: 'Status', value: gate.status || 'pending' },
        { label: 'Value', value: gate.value || gate.score || 'n/a' },
        { label: 'Threshold', value: gate.threshold || 'not set' },
        { label: 'Input', value: gate.input || 'not recorded' },
        { label: 'Branch', value: gate.branchId ? eventBranchTitle(gate.branchId) : 'run scope' },
        { label: 'Support Source', value: support.branchTitle },
        { label: 'Evidence Links', value: support.evidenceIds.length },
        { label: 'Source Links', value: support.sourceIds.length },
        { label: 'Graph Links', value: support.entityIds.length },
        { label: 'Timeline Links', value: support.timelineIds.length },
        { label: 'Failure', value: gate.failureReason || '' },
        { label: 'Remediation', value: gate.remediation || '' }
      ],
      items: [
        gate.branchId ? `Branch: ${eventBranchTitle(gate.branchId)}` : '',
        ...linkedEpisodes.map((episode) => dossierEpisodeLink(episode.id, gate.branchId || '')),
        ...(gate.toolCallIds || []).map((toolId) => dossierToolLink(toolId, gate.branchId || '')),
        ...(gate.artifactIds || []).map((artifactId) => dossierArtifactLink(artifactId, gate.branchId || '')),
        ...support.evidenceIds.map((evidenceId) => dossierEvidenceLink(evidenceId, support.branchId)),
        ...support.evidenceIds.map((evidenceId) => dossierSourceLink(evidenceId, support.branchId)),
        ...support.entityIds.map((entityId) => dossierGraphLink(entityId, support.branchId)),
        ...support.timelineIds.map((factId) => dossierTimelineLink(factId, support.branchId))
      ]
    })
  }

  if (focus.type === 'artifact') {
    const artifact = findArtifactDetail(focus.id)
    if (!artifact) return null
    const trace = artifact.toolCallId ? findToolTrace(artifact.toolCallId) : null
    const artifactBranchId = artifact.branchId || trace?.branchId || ''
    const linkedEpisodes = episodesForToken('artifactIds', artifact.id)
    return makeDossier({
      type: 'artifact',
      title: artifact.label || artifact.title || artifact.id,
      badge: artifact.type || artifact.kind || 'Artifact',
      summary: artifact.summary || artifact.description || artifact.path || '该产物由事件摘要提供，当前页面用于保留工具执行证据线索。',
      meta: [
        { label: 'Artifact ID', value: artifact.id },
        { label: 'Type', value: artifact.type || artifact.kind || 'artifact' },
        { label: 'Path', value: artifact.path || artifact.uri || 'metadata only' },
        { label: 'Tool Call', value: artifact.toolCallId || 'unknown' },
        { label: 'Branch', value: artifactBranchId ? eventBranchTitle(artifactBranchId) : '' }
      ],
      items: [
        trace
          ? makeDossierLink({
              label: `Tool: ${trace.name || trace.id}`,
              targetType: 'tool',
              targetId: trace.id,
              branchId: trace.branchId || artifactBranchId,
              canFocus: Boolean(trace.id)
          })
          : artifact.toolName ? `Tool: ${artifact.toolName}` : '',
        ...linkedEpisodes.map((episode) => dossierEpisodeLink(episode.id, artifactBranchId)),
        artifact.path ? `Path: ${artifact.path}` : ''
      ]
    })
  }

  if (focus.type === 'timeline') {
    const fact = findTimelineRef(focus.id)
    if (!fact) return null
    const evidence = findEvidenceRef(fact.evidenceId || '')
    return makeDossier({
      type: 'timeline',
      title: fact.label || fact.id,
      badge: fact.status || 'Temporal Fact',
      summary: evidence?.summary || `${fact.validFrom || 'unknown'} -> ${fact.validTo || 'present'}`,
      meta: [
        { label: 'Fact ID', value: fact.id },
        { label: 'Valid From', value: fact.validFrom || 'unknown' },
        { label: 'Valid To', value: fact.validTo || 'present' },
        { label: 'Evidence', value: fact.evidenceId || 'none' }
      ],
      items: evidence
        ? [
            dossierEvidenceLink(evidence.evidenceId || evidence.id)
          ]
        : []
    })
  }

  if (focus.type === 'skill') {
    const skill = findSkillProposal(focus.id)
    if (!skill) return null
    const promotion = skill.promotion || {}
    const sourceBranchId = skillSourceBranchId(skill)
    const linkedEpisodeIds = skillLinkedEpisodeIds(skill)
    return makeDossier({
      type: 'skill',
      title: skill.name || skill.id,
      badge: `${Math.round((skill.evalScore || 0) * 100)}%`,
      summary: skill.trigger,
      meta: [
        { label: 'Skill ID', value: skill.id },
        { label: 'Version', value: skill.version || 'candidate' },
        { label: 'Status', value: skill.status || 'candidate' },
        { label: 'Promotion', value: promotion.status || 'manual_review' },
        { label: 'Threshold', value: promotion.threshold || '' },
        { label: 'Blocker', value: promotion.blocker || '' },
        { label: 'Source Branch', value: skillSourceBranchTitle(skill) },
        { label: 'Eval Score', value: formatDecisionScore(skill.evalScore) },
        { label: 'Permissions', value: joinList(skill.requiredPermissions || []) },
        { label: 'Evidence Runs', value: joinList(skill.evidenceRunIds || []) },
        { label: 'Gates', value: countList(skill.gateResultIds) },
        { label: 'Artifacts', value: countList(skill.artifactIds) },
        { label: 'Episodes', value: linkedEpisodeIds.length },
        { label: 'Criteria', value: countList(skill.acceptanceCriteria) }
      ],
      items: [
        ...(skill.requiredPermissions || []).map((permission) => dossierPermissionLink(permission, sourceBranchId)),
        ...(skill.gateResultIds || []).map((gateId) => dossierGateLink(gateId, sourceBranchId)),
        ...(skill.artifactIds || []).map((artifactId) => dossierArtifactLink(artifactId, sourceBranchId)),
        ...linkedEpisodeIds.map((episodeId) => dossierEpisodeLink(episodeId, sourceBranchId)),
        ...(skill.steps || []).map((step) => `Step: ${step}`),
        ...(skill.acceptanceCriteria || []).map((item) => `Criterion: ${item}`)
      ]
    })
  }

  return null
}

const mergeLedgerResult = (result = {}, message = '') => {
  const previous = agentRun.value || {}
  const previousRun = previous.run || {}
  const nextRunMeta = {
    ...previousRun,
    id: result.id || previousRun.id,
    title: result.title || previousRun.title,
    goal: result.goal || previousRun.goal,
    status: result.status || previousRun.status,
    createdBy: result.createdBy || previousRun.createdBy,
    createdAt: result.createdAt || previousRun.createdAt,
    updatedAt: result.updatedAt || previousRun.updatedAt,
    budget: result.budget || previousRun.budget,
    qualitySummary: result.qualitySummary || previousRun.qualitySummary
  }
  const nextRun = {
    ...previous,
    ...result,
    run: nextRunMeta,
    themeId: result.themeId || previous.themeId,
    moduleId: result.moduleId || previous.moduleId,
    knowledgeDbId: result.knowledgeDbId || previous.knowledgeDbId,
    knowledgeMode: result.knowledgeMode || previous.knowledgeMode,
    layers: result.layers || previous.layers || [],
    rootQuestion: result.rootQuestion || previous.rootQuestion,
    questionDraft: result.questionDraft || previous.questionDraft,
    sourceType: result.metadata?.source || previous.sourceType,
    tree: result.tree?.nodes?.length ? result.tree : previous.tree,
    snapshots: result.snapshots?.length ? result.snapshots : previous.snapshots,
    routeTrace: {
      ...(previous.routeTrace || {}),
      ...(result.routeTrace || {}),
      live_api: '/api/worldline/runs'
    },
    viewState: {
      ...(previous.viewState || {}),
      ...(result.viewState || {}),
      lastGeneratedFrom: 'worldline-run-ledger'
    },
    displayMeta: {
      ...(previous.displayMeta || {}),
      ...(result.displayMeta || {})
    },
    toolTraces: Array.isArray(result.toolTraces) ? result.toolTraces : previous.toolTraces || [],
    gateResults: Array.isArray(result.gateResults) ? result.gateResults : previous.gateResults || [],
    contract: result.contract || previous.contract || {}
  }

  ledgerRunId.value = result.id || nextRun.run?.id || ledgerRunId.value
  questionDraft.value = nextRun.rootQuestion || nextRun.run?.goal || questionDraft.value
  runMaintenanceTitle.value = nextRun.run?.title || nextRun.title || runMaintenanceTitle.value
  backendRunManifest.value = null
  runManifestError.value = ''
  resourceDrilldownResult.value = null
  resourceDrilldownMessage.value = ''
  runCompareResult.value = null
  runCompareMessage.value = ''
  runCompareTarget.value = ''
  if (Array.isArray(result.events)) {
    ledgerEvents.value = result.events
    ledgerEventsTotal.value = Math.max(ledgerEventsTotal.value, result.events.length)
  } else if (result.latestEvent) {
    const seen = new Set(ledgerEvents.value.map((event) => event.id))
    ledgerEvents.value = seen.has(result.latestEvent.id)
      ? ledgerEvents.value
      : [...ledgerEvents.value, result.latestEvent]
    ledgerEventsTotal.value = Math.max(ledgerEventsTotal.value, ledgerEvents.value.length)
  }
  if (Array.isArray(result.artifacts)) {
    setSavedReplayArtifacts(result.artifacts)
  }
  ledgerError.value = ''
  if (message) {
    ledgerMessage.value = message
  }
  hydrateRun(nextRun)
}

const makeLedgerPayload = () => {
  const payload = {
    ...agentRun.value,
    evidenceRefs: cloneSerializable(worldlineStore.evidenceRefs, []),
    wikiRefs: cloneSerializable(worldlineStore.wikiRefs, []),
    entityRefs: cloneSerializable(worldlineStore.entityRefs, []),
    timelineRefs: cloneSerializable(worldlineStore.timelineRefs, []),
    run: {
      ...(agentRun.value.run || {})
    }
  }
  if (ledgerRunId.value) {
    payload.run.id = ledgerRunId.value
  } else if (payload.run.id === 'run-agent-workbench-preview') {
    payload.run.id = ''
  }
  return payload
}

const requireLedgerAccess = () => {
  if (canUseRunLedger.value) {
    return true
  }
  ledgerMessage.value = userStore.isLoggedIn
    ? '当前账号不是管理员；继续使用本地预览，后端写操作已禁用。'
    : '请先登录管理员账号；当前继续使用本地预览。'
  return false
}

const runLedgerOperation = async (operation) => {
  if (!requireLedgerAccess()) return null
  ledgerBusy.value = true
  ledgerError.value = ''

  try {
    return await operation()
  } catch (error) {
    ledgerError.value = normalizeErrorMessage(error)
    ledgerMessage.value = `后端账本操作失败：${ledgerError.value}。当前世界线仍保留本地预览。`
    return null
  } finally {
    ledgerBusy.value = false
  }
}

const persistRunToLedger = async () => {
  const result = await worldlineRunApi.createRun(makeLedgerPayload())
  mergeLedgerResult(result, `已保存到后端 run ledger：${result.id}`)
  return result.id
}

const ensureLedgerRun = async () => {
  if (ledgerRunId.value) return ledgerRunId.value
  return await persistRunToLedger()
}

const syncRunToLedger = async () => {
  await runLedgerOperation(persistRunToLedger)
}

const runSelectorFilterParams = () => ({
  query: ledgerRunQuery.value,
  status: ledgerRunStatus.value,
  theme_id: ledgerRunThemeId.value,
  created_by: ledgerRunCreatedBy.value
})

const mergeLedgerRunPage = (currentItems = [], pageItems = []) => {
  const merged = [...currentItems]
  const knownIds = new Set(merged.map((item) => String(item.id || '')).filter(Boolean))
  for (const item of pageItems) {
    const id = String(item.id || '').trim()
    if (!id || knownIds.has(id)) continue
    merged.push(item)
    knownIds.add(id)
  }
  return merged
}

const refreshLedgerRuns = async ({ append = false } = {}) => {
  await runLedgerOperation(async () => {
    ledgerRunListBusy.value = true
    try {
      const offset = append ? ledgerRunList.value.length : 0
      const result = await worldlineRunApi.listRuns({
        limit: LEDGER_RUN_PAGE_SIZE,
        offset,
        ...runSelectorFilterParams()
      })
      const items = Array.isArray(result.items) ? result.items : []
      const nextItems = append ? mergeLedgerRunPage(ledgerRunList.value, items) : items
      ledgerRunList.value = nextItems
      const availableIds = new Set(nextItems.map((item) => String(item.id || '')).filter(Boolean))
      selectedLedgerRunIds.value = selectedLedgerRunIds.value.filter((id) => availableIds.has(String(id)))
      ledgerRunListTotal.value = Number(result.total ?? nextItems.length)
      ledgerRunListMessage.value = nextItems.length
        ? `Loaded ${nextItems.length}/${ledgerRunListTotal.value} backend runs${hasRunSelectorFilters.value ? ' with filters' : ''}.`
        : hasRunSelectorFilters.value
          ? 'No backend runs match the current filters.'
          : 'No backend runs found yet.'
      return result
    } finally {
      ledgerRunListBusy.value = false
    }
  })
}

const refreshLoadedLedgerRuns = async () => {
  const loadedLimit = Math.max(LEDGER_RUN_PAGE_SIZE, ledgerRunList.value.length)
  await runLedgerOperation(async () => {
    ledgerRunListBusy.value = true
    try {
      const result = await worldlineRunApi.listRuns({
        limit: loadedLimit,
        offset: 0,
        ...runSelectorFilterParams()
      })
      const items = Array.isArray(result.items) ? result.items : []
      ledgerRunList.value = items
      const availableIds = new Set(items.map((item) => String(item.id || '')).filter(Boolean))
      selectedLedgerRunIds.value = selectedLedgerRunIds.value.filter((id) => availableIds.has(String(id)))
      ledgerRunListTotal.value = Number(result.total ?? items.length)
      ledgerRunListMessage.value = items.length
        ? `Loaded ${items.length}/${ledgerRunListTotal.value} backend runs${hasRunSelectorFilters.value ? ' with filters' : ''}.`
        : hasRunSelectorFilters.value
          ? 'No backend runs match the current filters.'
          : 'No backend runs found yet.'
      return result
    } finally {
      ledgerRunListBusy.value = false
    }
  })
}

const loadMoreLedgerRuns = async () => {
  if (!canLoadMoreLedgerRuns.value) return null
  return await refreshLedgerRuns({ append: true })
}

const clearLedgerRunFilters = async () => {
  ledgerRunQuery.value = ''
  ledgerRunStatus.value = ''
  ledgerRunThemeId.value = ''
  ledgerRunCreatedBy.value = ''
  ledgerRunListMessage.value = '筛选已清空。'
  await refreshLedgerRuns()
}

const clearLedgerRunSelection = () => {
  selectedLedgerRunIds.value = []
}

const compareLedgerRun = async (rightRunId = '') => {
  const normalizedRightRunId = String(rightRunId || '').trim()
  if (!ledgerRunId.value) {
    runCompareMessage.value = '请先载入或保存当前后端任务，再对比已保存任务。'
    return null
  }
  if (!normalizedRightRunId || normalizedRightRunId === ledgerRunId.value) {
    runCompareMessage.value = '请选择另一个已保存任务进行对比。'
    return null
  }
  return await runLedgerOperation(async () => {
    runCompareBusy.value = true
    runCompareTarget.value = normalizedRightRunId
    try {
      const result = await worldlineRunApi.compareRuns({
        left_run_id: ledgerRunId.value,
        right_run_id: normalizedRightRunId
      })
      runCompareResult.value = result
      runCompareMessage.value = `已对比 ${result.left?.id || ledgerRunId.value} 与 ${result.right?.id || normalizedRightRunId}。`
      return result
    } finally {
      runCompareBusy.value = false
      runCompareTarget.value = ''
    }
  })
}

const renameActiveLedgerRun = async () => {
  if (!ledgerRunId.value) {
    runMaintenanceMessage.value = '请先载入或保存一个后端任务，再重命名。'
    return null
  }
  const title = String(runMaintenanceTitle.value || '').trim()
  if (!title) {
    runMaintenanceMessage.value = '请输入非空任务标题。'
    return null
  }
  return await runLedgerOperation(async () => {
    runMaintenanceBusy.value = true
    runMaintenanceTarget.value = ledgerRunId.value
    const eventRefreshLimit = loadedLedgerEventLimit()
    try {
      const result = await worldlineRunApi.renameRun(ledgerRunId.value, {
        title,
        reason: 'operator rename from Agent Workbench selector'
      })
      mergeLedgerResult(result, `已重命名后端任务：${result.title || title}`)
      runMaintenanceMessage.value = `任务已重命名为 ${result.title || title}。`
      await refreshActiveRunEventsAfterMutation(result.id || ledgerRunId.value, { limit: eventRefreshLimit })
      await refreshLoadedLedgerRuns()
      return result
    } finally {
      runMaintenanceBusy.value = false
      runMaintenanceTarget.value = ''
    }
  })
}

const archiveLedgerRun = async (runId = '', options = {}) => {
  const normalizedRunId = String(runId || '').trim()
  if (!normalizedRunId) return null
  return await runLedgerOperation(async () => {
    runMaintenanceBusy.value = true
    runMaintenanceTarget.value = normalizedRunId
    const eventRefreshLimit = loadedLedgerEventLimit()
    try {
      const result = await worldlineRunApi.archiveRun(normalizedRunId, {
        reason: 'operator archive from Agent Workbench selector'
      })
      if (normalizedRunId === ledgerRunId.value) {
        mergeLedgerResult(result, `已归档后端任务：${result.title || normalizedRunId}`)
        await refreshActiveRunEventsAfterMutation(normalizedRunId, { limit: eventRefreshLimit })
      } else {
        const items = ledgerRunList.value.map((item) =>
          item.id === normalizedRunId
            ? { ...item, title: result.title || item.title, status: result.status || 'archived' }
            : item
        )
        ledgerRunList.value = items
      }
      runMaintenanceMessage.value = `已归档任务 ${result.title || normalizedRunId}。`
      if (options.refresh !== false) await refreshLoadedLedgerRuns()
      return result
    } finally {
      runMaintenanceBusy.value = false
      runMaintenanceTarget.value = ''
    }
  })
}

const restoreLedgerRun = async (runId = '', options = {}) => {
  const normalizedRunId = String(runId || '').trim()
  if (!normalizedRunId) return null
  return await runLedgerOperation(async () => {
    runMaintenanceBusy.value = true
    runMaintenanceTarget.value = normalizedRunId
    const eventRefreshLimit = loadedLedgerEventLimit()
    try {
      const result = await worldlineRunApi.restoreRun(normalizedRunId, {
        reason: 'operator restore from Agent Workbench selector'
      })
      if (normalizedRunId === ledgerRunId.value) {
        mergeLedgerResult(result, `已恢复后端任务：${result.title || normalizedRunId}`)
        await refreshActiveRunEventsAfterMutation(normalizedRunId, { limit: eventRefreshLimit })
      } else {
        const items = ledgerRunList.value.map((item) =>
          item.id === normalizedRunId
            ? { ...item, title: result.title || item.title, status: result.status || 'ready' }
            : item
        )
        ledgerRunList.value = items
      }
      runMaintenanceMessage.value = `已恢复任务 ${result.title || normalizedRunId}。`
      if (options.refresh !== false) await refreshLoadedLedgerRuns()
      return result
    } finally {
      runMaintenanceBusy.value = false
      runMaintenanceTarget.value = ''
    }
  })
}

const archiveSelectedLedgerRuns = async () => {
  const targets = selectedArchiveRuns.value.map((item) => String(item.id || '').trim()).filter(Boolean)
  if (!targets.length) {
    runMaintenanceMessage.value = '请先选择未归档任务，再批量归档。'
    return []
  }
  runMaintenanceBusy.value = true
  runMaintenanceTarget.value = 'bulk-archive'
  const archived = []
  try {
    for (const runId of targets) {
      const result = await archiveLedgerRun(runId, { refresh: false })
      if (result) archived.push(result)
    }
    await refreshLoadedLedgerRuns()
    clearLedgerRunSelection()
    runMaintenanceMessage.value = `已归档 ${archived.length}/${targets.length} 个已选任务。`
    return archived
  } finally {
    runMaintenanceBusy.value = false
    runMaintenanceTarget.value = ''
  }
}

const restoreSelectedLedgerRuns = async () => {
  const targets = selectedRestoreRuns.value.map((item) => String(item.id || '').trim()).filter(Boolean)
  if (!targets.length) {
    runMaintenanceMessage.value = '请先选择已归档任务，再批量恢复。'
    return []
  }
  runMaintenanceBusy.value = true
  runMaintenanceTarget.value = 'bulk-restore'
  const restored = []
  try {
    for (const runId of targets) {
      const result = await restoreLedgerRun(runId, { refresh: false })
      if (result) restored.push(result)
    }
    await refreshLoadedLedgerRuns()
    clearLedgerRunSelection()
    runMaintenanceMessage.value = `已恢复 ${restored.length}/${targets.length} 个已选任务。`
    return restored
  } finally {
    runMaintenanceBusy.value = false
    runMaintenanceTarget.value = ''
  }
}

const loadLedgerRun = async (runId = '') => {
  const normalizedRunId = String(runId || '').trim()
  if (!normalizedRunId) return null
  return await runLedgerOperation(async () => {
    const result = await worldlineRunApi.getRun(normalizedRunId)
    mergeLedgerResult(result, `Loaded backend run: ${result.title || result.id || normalizedRunId}`)
    ledgerRunListMessage.value = `Active backend run: ${result.id || normalizedRunId}`
    ledgerEvents.value = []
    ledgerEventsTotal.value = 0
    await fetchLedgerEventsPage({ append: false })
    return result
  })
}

const refreshRunArtifacts = async () => {
  if (!ledgerRunId.value) return null
  const result = await worldlineRunApi.listRunArtifacts(ledgerRunId.value)
  setSavedReplayArtifacts(Array.isArray(result.items) ? result.items : [])
  artifactRegistryMessage.value = `Registry ${result.total ?? savedReplayArtifacts.value.length} artifacts.`
  return result
}

const mergeLedgerEventPage = (currentEvents = [], pageEvents = []) => {
  const merged = [...currentEvents]
  const knownIds = new Set(merged.map((event) => String(event.id || '')).filter(Boolean))
  for (const event of pageEvents) {
    const id = String(event.id || '').trim()
    if (!id || knownIds.has(id)) continue
    merged.push(event)
    knownIds.add(id)
  }
  return merged
}

const fetchLedgerEventsPage = async ({ append = false, limit = LEDGER_EVENT_PAGE_SIZE } = {}) => {
  if (!ledgerRunId.value) {
    ledgerMessage.value = '请先保存 run，再刷新事件流。'
    return null
  }
  ledgerEventsBusy.value = true
  try {
    const offset = append ? ledgerEvents.value.length : 0
    const result = await worldlineRunApi.listRunEvents(ledgerRunId.value, {
      limit,
      offset
    })
    const items = Array.isArray(result.items) ? result.items : []
    ledgerEvents.value = append ? mergeLedgerEventPage(ledgerEvents.value, items) : items
    ledgerEventsTotal.value = Number(result.total ?? ledgerEvents.value.length)
    await refreshRunArtifacts()
    ledgerMessage.value = `已加载 ${ledgerEvents.value.length}/${ledgerEventsTotal.value || ledgerEvents.value.length} 条 run ledger 事件。`
    return result
  } finally {
    ledgerEventsBusy.value = false
  }
}

const refreshLedgerEvents = async ({ append = false } = {}) => {
  await runLedgerOperation(async () => await fetchLedgerEventsPage({ append }))
}

const loadedLedgerEventLimit = () => Math.max(LEDGER_EVENT_PAGE_SIZE, ledgerEvents.value.length)

const fetchLoadedLedgerEventsWindow = async ({ limit = loadedLedgerEventLimit() } = {}) => {
  if (!ledgerRunId.value || !ledgerEvents.value.length) return null
  const result = await fetchLedgerEventsPage({
    append: false,
    limit
  })
  if (result) {
    ledgerMessage.value = `已刷新 ${ledgerEvents.value.length}/${ledgerEventsTotal.value || ledgerEvents.value.length} 条 run ledger 事件。`
  }
  return result
}

const refreshLoadedLedgerEvents = async () => {
  await runLedgerOperation(async () => await fetchLoadedLedgerEventsWindow())
}

const refreshActiveRunEventsAfterMutation = async (runId = '', options = {}) => {
  const normalizedRunId = String(runId || '').trim()
  if (!normalizedRunId || normalizedRunId !== ledgerRunId.value) return null
  return await fetchLoadedLedgerEventsWindow(options)
}

const loadMoreLedgerEvents = async () => {
  if (!canLoadMoreLedgerEvents.value) return null
  return await refreshLedgerEvents({ append: true })
}

const saveReplayExportArtifact = async () => {
  await runLedgerOperation(async () => {
    artifactSaveBusy.value = true
    try {
      const runId = await ensureLedgerRun()
      if (!runId) return null
      const eventRefreshLimit = loadedLedgerEventLimit()
      const artifact = createReplayExportArtifact()
      const result = await worldlineRunApi.registerRunArtifact(runId, replayArtifactRegistryPayload(artifact))
      const registeredArtifacts = artifactListFromRegisterResult(result)
      mergeLedgerResult(result, `Replay artifact registered: ${result.artifact?.id || 'artifact'}`)
      mergeSavedReplayArtifacts(registeredArtifacts)
      const savedLabel = result.artifact?.label || result.artifact?.id || 'replay artifact'
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
      mergeSavedReplayArtifacts(registeredArtifacts)
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      return result
    } finally {
      artifactSaveBusy.value = false
    }
  })
}

const saveAgentHandoffCapsule = async () => {
  await runLedgerOperation(async () => {
    handoffSaveBusy.value = true
    try {
      const runId = await ensureLedgerRun()
      if (!runId) return null
      const eventRefreshLimit = loadedLedgerEventLimit()
      const payload = handoffArtifactRegistryPayload(agentHandoffCapsule.value)
      const result = await worldlineRunApi.registerRunArtifact(runId, payload)
      const registeredArtifacts = artifactListFromRegisterResult(result)
      mergeLedgerResult(result, `Agent handoff registered: ${result.artifact?.id || 'handoff'}`)
      mergeSavedReplayArtifacts(registeredArtifacts)
      const savedLabel = result.artifact?.label || result.artifact?.id || 'agent handoff'
      handoffMessage.value = `Saved ${savedLabel} to run ledger.`
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
      mergeSavedReplayArtifacts(registeredArtifacts)
      handoffMessage.value = `Saved ${savedLabel} to run ledger.`
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      return result
    } finally {
      handoffSaveBusy.value = false
    }
  })
}

const saveResourceDetailArtifact = async () => {
  if (!resourceDrilldownResult.value) {
    resourceDrilldownMessage.value = 'Inspect a backend resource before saving its detail.'
    return null
  }
  await runLedgerOperation(async () => {
    resourceDetailSaveBusy.value = true
    try {
      const runId = await ensureLedgerRun()
      if (!runId) return null
      const eventRefreshLimit = loadedLedgerEventLimit()
      const inspectedResourceDetail = resourceDrilldownResult.value
      const inspectedResourceTarget = resourceDrilldownTarget.value
      const payload = resourceDetailArtifactRegistryPayload()
      const result = await worldlineRunApi.registerRunArtifact(runId, payload)
      const registeredArtifacts = artifactListFromRegisterResult(result)
      mergeLedgerResult(result, `Resource detail artifact registered: ${result.artifact?.id || payload.id}`)
      mergeSavedReplayArtifacts(registeredArtifacts)
      const savedLabel = result.artifact?.label || payload.label
      resourceDrilldownResult.value = inspectedResourceDetail
      resourceDrilldownTarget.value = inspectedResourceTarget
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      resourceDrilldownMessage.value = `已保存资源详情证据：${savedLabel}。`
      await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
      mergeSavedReplayArtifacts(registeredArtifacts)
      resourceDrilldownResult.value = inspectedResourceDetail
      resourceDrilldownTarget.value = inspectedResourceTarget
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      resourceDrilldownMessage.value = `已保存资源详情证据：${savedLabel}。`
      return result
    } finally {
      resourceDetailSaveBusy.value = false
    }
  })
}

const saveResourceDetailDiffArtifact = async () => {
  if (!resourceDetailCompareResult.value) {
    resourceDetailCompareMessage.value = '请先完成资源详情对比，再保存差异证据。'
    return null
  }
  await runLedgerOperation(async () => {
    resourceDetailDiffSaveBusy.value = true
    try {
      const runId = await ensureLedgerRun()
      if (!runId) return null
      const eventRefreshLimit = loadedLedgerEventLimit()
      const inspectedResourceDetail = resourceDrilldownResult.value
      const inspectedResourceTarget = resourceDrilldownTarget.value
      const compareResult = resourceDetailCompareResult.value
      const compareMessage = resourceDetailCompareMessage.value
      const payload = resourceDetailDiffArtifactRegistryPayload()
      const result = await worldlineRunApi.registerRunArtifact(runId, payload)
      const registeredArtifacts = artifactListFromRegisterResult(result)
      mergeLedgerResult(result, `Resource detail diff artifact registered: ${result.artifact?.id || payload.id}`)
      mergeSavedReplayArtifacts(registeredArtifacts)
      const savedLabel = result.artifact?.label || payload.label
      resourceDrilldownResult.value = inspectedResourceDetail
      resourceDrilldownTarget.value = inspectedResourceTarget
      resourceDetailCompareResult.value = compareResult
      resourceDetailCompareMessage.value = compareMessage
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
      mergeSavedReplayArtifacts(registeredArtifacts)
      resourceDrilldownResult.value = inspectedResourceDetail
      resourceDrilldownTarget.value = inspectedResourceTarget
      resourceDetailCompareResult.value = compareResult
      resourceDetailCompareMessage.value = compareMessage
      artifactRegistryMessage.value = `Saved ${savedLabel} to run ledger.`
      return result
    } finally {
      resourceDetailDiffSaveBusy.value = false
    }
  })
}

const approveActiveBranch = async (action = {}) => {
  await runLedgerOperation(async () => {
    const branch = worldlineStore.activeBranch
    if (!branch) {
      ledgerMessage.value = '请先选择要审批的分支。'
      return null
    }
    const runId = await ensureLedgerRun()
    const eventRefreshLimit = loadedLedgerEventLimit()
    const result = await worldlineRunApi.approveBranch(runId, branch.id, {
      reason: action.description || `Approved from Agent Workbench: ${branch.title}`
    })
    mergeLedgerResult(result, `已批准分支：${branch.title}`)
    await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
    worldlineStore.setHandoff({
      target: 'agent-workbench',
      label: `已批准 ${branch.title}`
    })
    return result
  })
}

const rejectActiveBranch = async (action = {}) => {
  await runLedgerOperation(async () => {
    const branch = worldlineStore.activeBranch
    if (!branch) {
      ledgerMessage.value = '请先选择要拒绝的分支。'
      return null
    }
    const runId = await ensureLedgerRun()
    const eventRefreshLimit = loadedLedgerEventLimit()
    const result = await worldlineRunApi.rejectBranch(runId, branch.id, {
      reason: action.description || `Rejected from Agent Workbench: ${branch.title}`
    })
    mergeLedgerResult(result, `已拒绝分支：${branch.title}`)
    await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
    worldlineStore.setHandoff({
      target: 'agent-workbench',
      label: `已拒绝 ${branch.title}`
    })
    return result
  })
}

const submitSkillProposal = async (skill = {}) => {
  await runLedgerOperation(async () => {
    const runId = await ensureLedgerRun()
    const eventRefreshLimit = loadedLedgerEventLimit()
    const result = await worldlineRunApi.proposeSkill(runId, {
      ...skill,
      branchId: activeBranchId.value,
      evidenceRunIds: Array.from(new Set([...(skill.evidenceRunIds || []), runId]))
    })
    mergeLedgerResult(result, `已提交技能候选：${skill.name}`)
    await refreshActiveRunEventsAfterMutation(runId, { limit: eventRefreshLimit })
    return result
  })
}

const regenerateRun = () => {
  ledgerRunId.value = ''
  ledgerEvents.value = []
  ledgerEventsTotal.value = 0
  ledgerEventsBusy.value = false
  ledgerError.value = ''
  ledgerRunListMessage.value = ''
  backendRunManifest.value = null
  resourceDrilldownResult.value = null
  resourceDrilldownMessage.value = ''
  resourceDetailSaveBusy.value = false
  resourceDetailReplayBusyId.value = ''
  resourceDetailCompareBusyId.value = ''
  resourceDetailCompareResult.value = null
  resourceDetailCompareMessage.value = ''
  runCompareResult.value = null
  runCompareMessage.value = ''
  runCompareTarget.value = ''
  runMaintenanceTitle.value = ''
  runMaintenanceMessage.value = ''
  runMaintenanceTarget.value = ''
  clearLedgerRunSelection()
  artifactRegistryMessage.value = ''
  setSavedReplayArtifacts([])
  ledgerMessage.value = '本地预览已重建；管理员登录后可保存到后端 run ledger。'
  hydrateRun(createAgentWorkbenchRun({ question: questionDraft.value }))
}

const syncSelectedEventForBranch = (branchId = '') => {
  if (!branchId) return
  const branchEvent = visibleLedgerEvents.value.find((event) => event.branchId === branchId)
  if (branchEvent?.id) {
    selectedEventId.value = branchEvent.id
  }
}

const selectBranch = (branchId, { syncEvent = true } = {}) => {
  worldlineStore.setSelectedNode(branchId)
  if (syncEvent) {
    syncSelectedEventForBranch(branchId)
  }
}

const selectLedgerEvent = (event = {}) => {
  selectedEventId.value = event.id || ''
  if (event.branchId) {
    selectBranch(event.branchId, { syncEvent: false })
  }
}

const selectReplayStep = (step = {}) => {
  if (step.event) {
    selectLedgerEvent(step.event)
  }
}

const eventCanOpenManifest = (event = {}) => {
  const summary = event.summary || {}
  return Boolean(event.runId || summary.title || countList(summary.branch_ids) || summary.branch_count)
}

const escapeAttributeValue = (value = '') =>
  String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"')

const scrollToInspectorTarget = async (target = {}) => {
  await nextTick()
  const attributeName = target.targetType === 'permission'
    ? 'data-inspector-permission-target'
    : 'data-inspector-target'
  const selectorValue = target.targetType === 'permission'
    ? `permission:${target.targetId}`
    : `${target.targetType}:${target.targetId}`
  const selector = `[${attributeName}="${escapeAttributeValue(selectorValue)}"]`
  const targetElement = (evidenceRailFocusTypes.has(target.targetType)
    ? document.querySelector(`.evidence-rail ${selector}`)
    : null) ||
    document.querySelector(selector) ||
    document.querySelector('[data-inspector-dossier="true"]')
  targetElement?.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
}

const itemExistsInList = (items = [], itemId = '') =>
  Boolean(itemId && items.some((item) => item.id === itemId))

const chooseArtifactScopeForTarget = (artifact = {}) => {
  if (itemExistsInList(selectedEventArtifactDetails.value, artifact.id)) return 'event'
  if (itemExistsInList(activeArtifactDetails.value, artifact.id)) return 'branch'
  if (itemExistsInList(allArtifactDetails.value, artifact.id)) return 'all'
  return artifactScope.value
}

const chooseGateScopeForTarget = (gate = {}) => {
  if (itemExistsInList(selectedEventGateDetails.value, gate.id)) return 'event'
  if (itemExistsInList(activeGateDetails.value, gate.id)) return 'branch'
  if (itemExistsInList(allGateDetails.value, gate.id)) return 'all'
  return gateScope.value
}

const focusInspectorTarget = async ({
  targetType = '',
  targetId = '',
  branchId = '',
  layer = '',
  token = '',
  label = ''
} = {}) => {
  if (branchId) {
    selectBranch(branchId, { syncEvent: false })
  }

  const target = {
    canFocus: true,
    targetType,
    targetId,
    token: token || `${targetType}:${targetId}`,
    branchId,
    layer
  }
  inspectorFocus.value = {
    type: targetType,
    id: targetId,
    token: target.token,
    layer
  }
  focusDossierMcpMessage.value = ''
  inspectorFocusMessage.value = `Focused ${label || targetId}.`
  await scrollToInspectorTarget(target)
}

const focusRunManifest = async (event = selectedLedgerEvent.value || {}) => {
  if (!event?.id) return
  selectedEventId.value = event.id
  await focusInspectorTarget({
    targetType: 'run',
    targetId: event.id,
    branchId: '',
    label: event.summary?.title || event.runId || event.id
  })
}

const focusEventDetailToken = async (item = {}) => {
  if (!item.canFocus) {
    inspectorFocusMessage.value = `${item.label} 当前页面暂无可定位目标。`
    return
  }

  if (item.branchId) {
    selectBranch(item.branchId, { syncEvent: false })
  }

  inspectorFocus.value = {
    type: item.targetType,
    id: item.targetId,
    token: item.token,
    layer: item.layer || ''
  }
  inspectorFocusMessage.value = `已定位 ${item.label}。`
  await scrollToInspectorTarget(item)
  await inspectEventTokenResource(item)
}

const focusDossierItem = async (item = {}) => {
  focusDossierMcpMessage.value = ''
  if (!item.canFocus) {
    inspectorFocusMessage.value = `${item.label} has no focus target.`
    return
  }

  if (item.targetType === 'artifact') {
    const artifact = findArtifactDetail(item.targetId)
    if (!artifact) {
      inspectorFocusMessage.value = `${item.label} has no artifact detail.`
      return
    }
    const branchId = artifact.branchId || item.branchId || ''
    if (branchId) {
      selectBranch(branchId, { syncEvent: false })
    }
    artifactScope.value = chooseArtifactScopeForTarget({ ...artifact, branchId })
    await focusArtifactRailItem({ ...artifact, branchId })
    return
  }

  if (item.targetType === 'gate') {
    const gate = findGateResult(item.targetId)
    if (!gate) {
      inspectorFocusMessage.value = `${item.label} has no gate detail.`
      return
    }
    const branchId = gate.branchId || item.branchId || ''
    if (branchId) {
      selectBranch(branchId, { syncEvent: false })
    }
    gateScope.value = chooseGateScopeForTarget({ ...gate, branchId })
    await focusGateRunItem({ ...gate, branchId })
    return
  }

  if (item.targetType === 'tool') {
    const trace = findToolTrace(item.targetId)
    if (!trace) {
      inspectorFocusMessage.value = `${item.label} has no tool trace.`
      return
    }
    await focusInspectorTarget({
      targetType: 'tool',
      targetId: trace.id,
      branchId: trace.branchId || item.branchId || '',
      token: item.token || `tool:${trace.id}`,
      label: trace.name || trace.id
    })
    return
  }

  await focusInspectorTarget(item)
}

const focusEpisodeCard = async (episode = {}) => {
  if (!episode.id) return
  await focusInspectorTarget({
    targetType: 'episode',
    targetId: episode.id,
    branchId: episode.branchId || '',
    label: episode.actor || episode.id
  })
}

const focusSkillCard = async (skill = {}) => {
  if (!skill.id) return
  await focusInspectorTarget({
    targetType: 'skill',
    targetId: skill.id,
    branchId: skillSourceBranchId(skill),
    label: skill.name || skill.id
  })
}

const focusEvidenceRailItem = async ({ layer = '', itemId = '', item = {} } = {}) => {
  if (!evidenceRailFocusTypes.has(layer) || !itemId) {
    return
  }
  await focusInspectorTarget({
    targetType: layer,
    targetId: itemId,
    layer,
    label: item.title || item.name || item.label || item.slug || itemId
  })
}

const focusArtifactRailItem = async (artifact = {}) => {
  if (artifact.branchId) {
    selectBranch(artifact.branchId, { syncEvent: false })
  }

  const target = {
    canFocus: true,
    targetType: 'artifact',
    targetId: artifact.id,
    token: `artifact:${artifact.id}`,
    branchId: artifact.branchId || ''
  }
  inspectorFocus.value = {
    type: 'artifact',
    id: artifact.id,
    token: target.token,
    layer: ''
  }
  inspectorFocusMessage.value = `已定位 ${artifact.label || artifact.id}。`
  await scrollToInspectorTarget(target)
}

const focusRegisteredArtifact = async (artifact = {}) => {
  artifactScope.value = 'all'
  await focusArtifactRailItem(normalizeRegistryArtifactDetail(artifact))
}

const focusGateRunItem = async (gate = {}) => {
  if (gate.branchId) {
    selectBranch(gate.branchId, { syncEvent: false })
  }

  const target = {
    canFocus: true,
    targetType: 'gate',
    targetId: gate.id,
    token: `gate:${gate.id}`,
    branchId: gate.branchId || ''
  }
  inspectorFocus.value = {
    type: 'gate',
    id: gate.id,
    token: target.token,
    layer: ''
  }
  inspectorFocusMessage.value = `已定位 ${gate.label || gate.id}。`
  await scrollToInspectorTarget(target)
}

const isFocusedToken = (item = {}) =>
  inspectorFocus.value.token === item.token ||
  (inspectorFocus.value.type === item.targetType && inspectorFocus.value.id === item.targetId)

const isFocusedDossierItem = (item = {}) =>
  item.canFocus &&
  inspectorFocus.value.type === item.targetType &&
  inspectorFocus.value.id === item.targetId

const isToolTraceFocused = (trace = {}) =>
  (inspectorFocus.value.type === 'tool' && inspectorFocus.value.id === trace.id) ||
  (inspectorFocus.value.type === 'permission' && inspectorFocus.value.id === trace.permission)

const isGateFocused = (gate = {}) =>
  inspectorFocus.value.type === 'gate' && inspectorFocus.value.id === gate.id

const isArtifactFocused = (artifact = {}) =>
  inspectorFocus.value.type === 'artifact' && inspectorFocus.value.id === artifact.id

const isEpisodeFocused = (episode = {}) =>
  inspectorFocus.value.type === 'episode' && inspectorFocus.value.id === episode.id

const isBranchFocused = (branch = {}) =>
  inspectorFocus.value.type === 'branch' && inspectorFocus.value.id === branch.id

const isSkillFocused = (skill = {}) =>
  inspectorFocus.value.type === 'skill' && inspectorFocus.value.id === skill.id

const handleCanvasSelect = (nodeId) => {
  selectBranch(nodeId)
}

const handleBranchAction = async (action = {}) => {
  const branch = worldlineStore.activeBranch
  if (!branch) return

  if (action.targetType === 'approve') {
    await approveActiveBranch(action)
    return
  }

  if (action.targetType === 'reject') {
    await rejectActiveBranch(action)
    return
  }

  worldlineStore.setHandoff({
    target: 'agent-workbench',
    label: `已选择 ${branch.title}`
  })
  ledgerMessage.value = action.targetType === 'trace'
    ? `正在查看 ${branch.title} 的工具轨迹、证据和质量门。`
    : `已选择 ${branch.title}`
}

onMounted(() => {
  hydrateRun(agentRun.value)
  runMaintenanceTitle.value = run.value.title || agentRun.value.title || ''
})
</script>

<style scoped lang="less">
.agent-workbench {
  min-height: 100vh;
  overflow-x: hidden;
  padding: 18px 18px 26px;
  color: var(--wl-text);
  background:
    radial-gradient(circle at 10% 18%, rgba(var(--wl-gold-rgb), 0.12), transparent 26%),
    radial-gradient(circle at 86% 14%, rgba(var(--wl-cyan-rgb), 0.14), transparent 30%),
    linear-gradient(180deg, var(--wl-bg-1), var(--wl-bg-0) 74%, #05080d);
}

.agent-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  max-width: 1840px;
  margin: 0 auto 14px;
  align-items: flex-start;
}

.agent-header h1 {
  margin: 0;
  color: var(--wl-text);
  font-size: clamp(1.75rem, 2.8vw, 2.7rem);
  font-weight: 900;
  line-height: 1.15;
}

.agent-header p:last-child {
  max-width: 820px;
  margin: 8px 0 0;
  color: var(--wl-muted);
  line-height: 1.65;
}

.eyebrow {
  margin: 0 0 7px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.agent-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.agent-actions a,
.primary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  font-weight: 800;
  text-decoration: none;
}

.agent-actions a.router-link-active,
.primary-action {
  border-color: var(--wl-border-gold);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.92), rgba(var(--wl-cyan-rgb), 0.7));
  color: var(--wl-ink);
}

.agent-shell {
  display: grid;
  grid-template-columns: minmax(230px, 280px) minmax(0, 1fr) minmax(300px, 380px);
  gap: 14px;
  max-width: 1840px;
  margin: 0 auto;
  align-items: start;
}

.run-rail,
.inspect-rail,
.stage-column {
  display: grid;
  min-width: 0;
  gap: 12px;
}

.rail-panel {
  min-width: 0;
  padding: 14px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius);
  background: var(--wl-panel);
  box-shadow: var(--wl-shadow-soft);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.panel-head > span {
  color: var(--wl-muted-soft);
  font-size: 12px;
  font-weight: 800;
}

.run-card h2 {
  margin: 0;
  color: var(--wl-text);
  font-size: 18px;
}

.run-card p,
.trace-item p,
.skill-item p,
.empty-copy {
  color: var(--wl-muted);
  font-size: 13px;
  line-height: 1.65;
}

.run-stats,
.gate-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.run-stats div,
.gate-item {
  min-height: 70px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
}

.run-stats strong,
.gate-item strong {
  display: block;
  color: var(--wl-text);
  font-size: 22px;
  font-weight: 900;
}

.run-stats span,
.gate-item span {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.ledger-status {
  margin-top: 12px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
}

.ledger-status > div {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
}

.ledger-status strong {
  color: var(--wl-text);
  font-size: 13px;
  font-weight: 900;
  white-space: nowrap;
}

.ledger-status span {
  min-width: 0;
  overflow: hidden;
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ledger-status p {
  margin: 7px 0 0;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.55;
}

.ledger-status.is-synced {
  border-color: rgba(112, 240, 187, 0.32);
  background: rgba(112, 240, 187, 0.08);
}

.ledger-status.is-failed {
  border-color: rgba(255, 98, 116, 0.34);
  background: rgba(255, 98, 116, 0.08);
}

.ledger-status.is-locked {
  border-color: rgba(var(--wl-gold-rgb), 0.28);
  background: rgba(var(--wl-gold-rgb), 0.08);
}

.ledger-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}

.run-selector {
  display: grid;
  gap: 8px;
  margin-top: 10px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.run-selector-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.run-selector-title {
  display: grid;
  min-width: 0;
  gap: 2px;
}

.run-selector-title .eyebrow {
  margin: 0;
}

.run-selector-title strong {
  overflow: hidden;
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-selector p {
  margin: 0;
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 750;
  line-height: 1.5;
}

.run-selector-filters,
.run-maintenance {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
}

.run-selector-filters input,
.run-selector-filters select,
.run-maintenance input {
  width: 100%;
  min-width: 0;
  min-height: 30px;
  padding: 0 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.2);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.74);
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 750;
}

.run-selector-filters input::placeholder {
  color: rgba(189, 220, 226, 0.52);
}

.run-maintenance {
  grid-template-columns: minmax(0, 1fr) auto;
}

.run-selector-bulk {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
  align-items: center;
}

.run-selector-bulk > span {
  grid-column: 1 / -1;
  min-width: 0;
  overflow: hidden;
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-selector-refresh.secondary {
  border-color: rgba(var(--wl-cyan-rgb), 0.16);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-muted-soft);
}

.run-selector-refresh,
.run-selector-load,
.run-selector-compare,
.run-selector-archive {
  min-width: 0;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.22);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text-soft);
  cursor: pointer;
}

.run-selector-refresh {
  display: inline-flex;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 0 8px;
  font-size: 11px;
  font-weight: 850;
}

.run-selector-refresh span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-selector-list {
  display: grid;
  gap: 6px;
}

.run-selector-pagination {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 6px;
  align-items: center;
}

.run-selector-pagination > span {
  min-width: 0;
  overflow: hidden;
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-selector-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  width: 100%;
  gap: 6px;
  padding: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.run-selector-item.active {
  border-color: rgba(var(--wl-gold-rgb), 0.45);
  background: rgba(var(--wl-gold-rgb), 0.12);
}

.run-selector-pick {
  display: inline-flex;
  width: 24px;
  min-width: 24px;
  min-height: 36px;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.36);
}

.run-selector-pick input {
  width: 14px;
  height: 14px;
  accent-color: var(--wl-gold);
}

.run-selector-load {
  display: grid;
  gap: 3px;
  padding: 7px 8px;
  text-align: left;
}

.run-selector-compare,
.run-selector-archive {
  display: inline-flex;
  min-height: 36px;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.run-selector-archive.restore {
  border-color: rgba(var(--wl-gold-rgb), 0.34);
  background: rgba(var(--wl-gold-rgb), 0.1);
  color: var(--wl-gold);
}

.run-selector-load span,
.run-selector-load small,
.run-selector-compare span,
.run-selector-archive span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-selector-load span {
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 850;
}

.run-selector-load small {
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 750;
}

.run-selector-refresh:disabled,
.run-selector-load:disabled,
.run-selector-compare:disabled,
.run-selector-archive:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

.run-diff-panel {
  display: grid;
  gap: 8px;
  padding: 9px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.22);
  border-radius: var(--wl-radius-sm);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.08), rgba(var(--wl-cyan-rgb), 0.04));
}

.resource-detail-diff-panel {
  display: grid;
  gap: 8px;
  padding: 9px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.22);
  border-radius: var(--wl-radius-sm);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.07), rgba(var(--wl-cyan-rgb), 0.04));
}

.resource-detail-diff-panel > p {
  margin: 0;
  color: var(--wl-muted);
  font-size: 11px;
  font-weight: 750;
  line-height: 1.5;
}

.resource-detail-diff-panel .run-diff-head {
  align-items: flex-start;
}

.resource-detail-diff-panel .run-diff-head strong {
  white-space: normal;
}

.resource-detail-diff-panel .run-diff-head span {
  flex: 0 0 auto;
  white-space: nowrap;
}

.resource-detail-diff-panel .run-diff-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
}

.resource-detail-diff-panel .run-diff-row small {
  max-width: 88px;
}

.run-diff-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.run-diff-head div {
  display: grid;
  min-width: 0;
  gap: 2px;
}

.run-diff-head .eyebrow {
  margin: 0;
}

.run-diff-head strong,
.run-diff-head span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-diff-head strong {
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 900;
}

.run-diff-head span {
  color: #fff0bc;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.run-diff-counts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 5px;
  margin: 0;
}

.run-diff-counts div {
  display: grid;
  gap: 2px;
  padding: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.48);
}

.run-diff-counts dt {
  color: var(--wl-muted-soft);
  font-size: 9px;
  font-weight: 850;
  text-transform: uppercase;
}

.run-diff-counts dd {
  margin: 0;
  color: var(--wl-text);
  font-size: 15px;
  font-weight: 900;
}

.run-diff-timeline {
  display: grid;
  gap: 5px;
}

.run-diff-row {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.42);
}

.run-diff-row span,
.run-diff-row small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-diff-row span {
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 850;
}

.run-diff-row small {
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 800;
}

.replay-export-panel {
  display: grid;
  gap: 9px;
  margin-top: 12px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.22);
  border-radius: var(--wl-radius-sm);
  background: linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.08), rgba(var(--wl-cyan-rgb), 0.045));
}

.replay-export-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.replay-export-head .eyebrow {
  margin: 0;
}

.replay-export-head span,
.replay-export-message {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
}

.replay-export-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 7px;
}

.replay-export-preview {
  max-height: 210px;
  margin: 0;
  overflow: auto;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.82);
  color: var(--wl-text-soft);
  font-size: 11px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.replay-export-message {
  margin: 0;
  line-height: 1.5;
}

.replay-export-registry {
  display: grid;
  gap: 6px;
}

.registry-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.registry-head strong {
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.registry-head span {
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 850;
}

.registry-filters {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 5px;
}

.registry-filter-button,
.registry-artifact-button,
.registry-mcp-button {
  min-width: 0;
  overflow: hidden;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-text-soft);
  text-align: left;
  cursor: pointer;
}

.registry-filter-button {
  display: inline-flex;
  min-height: 25px;
  align-items: center;
  justify-content: space-between;
  gap: 5px;
  padding: 0 7px;
  font-size: 10px;
  font-weight: 850;
}

.registry-filter-button.active {
  border-color: rgba(var(--wl-gold-rgb), 0.42);
  background: rgba(var(--wl-gold-rgb), 0.13);
  color: #fff7de;
}

.registry-filter-button span,
.registry-filter-button small,
.registry-artifact-button span,
.registry-artifact-button small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.registry-filter-button small {
  color: var(--wl-muted-soft);
  font-size: 9px;
  font-weight: 900;
}

.registry-artifact-button {
  display: grid;
  gap: 3px;
  padding: 7px 8px;
}

.registry-artifact-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 5px;
}

.registry-artifact-button span {
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 850;
}

.registry-artifact-button small {
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 850;
}

.registry-mcp-button {
  display: inline-flex;
  min-height: 26px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 0 7px;
  color: var(--wl-muted);
  font-size: 10px;
  font-weight: 850;
}

.registry-mcp-button span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mcp-readable-panel {
  display: grid;
  gap: 7px;
  padding: 9px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
}

.mcp-readable-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.mcp-readable-head .eyebrow {
  margin: 0;
}

.mcp-readable-status {
  flex: 0 0 auto;
  padding: 3px 7px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.26);
  border-radius: 999px;
  color: var(--wl-gold);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.mcp-readable-status.registered {
  border-color: rgba(112, 240, 187, 0.34);
  color: #8ff2c9;
}

.mcp-readable-meta {
  display: grid;
  gap: 6px;
  margin: 0;
}

.mcp-readable-meta div {
  min-width: 0;
}

.mcp-readable-meta dt {
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.mcp-readable-meta dd {
  min-width: 0;
  margin: 2px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-family: var(--wl-mono);
  font-size: 10px;
  line-height: 1.45;
}

.mcp-readable-args {
  max-height: 112px;
  margin: 0;
  overflow: auto;
  padding: 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.72);
  color: var(--wl-text-soft);
  font-size: 10px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.mcp-readable-copy {
  display: inline-flex;
  min-width: 0;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.2);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 850;
  cursor: pointer;
}

.mcp-readable-copy:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

.mcp-readable-copy.secondary {
  background: rgba(255, 255, 255, 0.035);
  color: var(--wl-muted);
}

.mcp-readable-panel p {
  margin: 0;
  color: var(--wl-muted);
  font-size: 11px;
  line-height: 1.5;
}

.run-mcp-manifest {
  display: grid;
  gap: 7px;
  padding: 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.18);
}

.run-mcp-manifest-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.run-mcp-manifest-head strong {
  color: var(--wl-gold);
  font-size: 10px;
  font-weight: 950;
  letter-spacing: 0;
  text-transform: uppercase;
}

.run-mcp-manifest-head span {
  flex: 0 0 auto;
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 900;
}

.run-mcp-manifest-counts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  margin: 0;
}

.run-mcp-manifest-counts div {
  min-width: 0;
  padding: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.12);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.05);
}

.run-mcp-manifest-counts dt {
  color: var(--wl-muted-soft);
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
}

.run-mcp-manifest-counts dd {
  margin: 2px 0 0;
  color: var(--wl-text);
  font-size: 13px;
  font-weight: 950;
}

.run-manifest-api-inspector {
  display: grid;
  gap: 7px;
  padding: 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.045), rgba(var(--wl-cyan-rgb), 0.035)),
    rgba(0, 0, 0, 0.2);
}

.run-manifest-api-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.run-manifest-api-head strong {
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 950;
  letter-spacing: 0;
  text-transform: uppercase;
}

.run-manifest-api-status {
  flex: 0 0 auto;
  padding: 2px 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.2);
  border-radius: 999px;
  color: var(--wl-muted);
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
}

.run-manifest-api-status.loaded {
  border-color: rgba(112, 240, 187, 0.32);
  color: #8ff2c9;
}

.run-manifest-api-status.failed {
  border-color: rgba(255, 105, 105, 0.34);
  color: #ffaaaa;
}

.run-manifest-api-status.ready {
  border-color: rgba(var(--wl-gold-rgb), 0.3);
  color: var(--wl-gold);
}

.run-manifest-api-tools {
  display: flex;
  min-width: 0;
  flex-wrap: wrap;
  gap: 5px;
}

.run-manifest-api-tools span {
  max-width: 100%;
  overflow: hidden;
  padding: 2px 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: 999px;
  color: var(--wl-text-soft);
  font-family: var(--wl-mono);
  font-size: 9px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-manifest-api-resources {
  display: grid;
  gap: 5px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.run-manifest-api-resources li {
  display: grid;
  min-width: 0;
  gap: 5px;
  padding: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.12);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.42);
}

.run-manifest-resource-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.run-manifest-resource-head span {
  min-width: 0;
  overflow: hidden;
  color: var(--wl-gold);
  font-size: 9px;
  font-weight: 900;
  text-overflow: ellipsis;
  text-transform: uppercase;
  white-space: nowrap;
}

.run-manifest-resource-head button {
  flex: 0 0 auto;
  min-height: 22px;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  font-size: 9px;
  font-weight: 900;
  cursor: pointer;
}

.run-manifest-resource-head button:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

.run-manifest-api-resources code {
  min-width: 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-family: var(--wl-mono);
  font-size: 9px;
  line-height: 1.35;
}

.run-manifest-resource-detail {
  display: grid;
  gap: 7px;
  padding: 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-gold-rgb), 0.045);
}

.run-resource-detail-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
  margin: 0;
}

.run-resource-detail-summary div {
  min-width: 0;
  padding: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.13);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.42);
}

.run-resource-detail-summary dt {
  color: rgba(var(--wl-gold-rgb), 0.78);
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
}

.run-resource-detail-summary dd {
  min-width: 0;
  margin: 2px 0 0;
  overflow: hidden;
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.run-resource-detail-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.last-mcp-call {
  display: grid;
  gap: 7px;
  padding: 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.07), rgba(var(--wl-cyan-rgb), 0.045)),
    rgba(0, 0, 0, 0.22);
}

.last-mcp-call-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.last-mcp-call-head strong {
  color: var(--wl-gold);
  font-size: 10px;
  font-weight: 950;
  letter-spacing: 0;
  text-transform: uppercase;
}

.last-mcp-call-head span {
  flex: 0 0 auto;
  padding: 2px 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.22);
  border-radius: 999px;
  color: var(--wl-text-soft);
  font-size: 9px;
  font-weight: 900;
}

.last-mcp-call > p {
  color: var(--wl-text-soft);
  font-weight: 850;
}

.last-mcp-call-meta {
  display: grid;
  gap: 6px;
  margin: 0;
}

.last-mcp-call-meta div {
  min-width: 0;
}

.last-mcp-call-meta dt {
  color: rgba(var(--wl-gold-rgb), 0.76);
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
}

.last-mcp-call-meta dd {
  min-width: 0;
  margin: 2px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-family: var(--wl-mono);
  font-size: 10px;
  line-height: 1.45;
}

.agent-handoff-panel {
  display: grid;
  gap: 8px;
  padding: 9px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.2);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.08), rgba(var(--wl-cyan-rgb), 0.05)),
    rgba(255, 255, 255, 0.025);
}

.agent-handoff-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.agent-handoff-head .eyebrow {
  margin: 0;
}

.agent-handoff-head span {
  flex: 0 0 auto;
  padding: 3px 7px;
  border: 1px solid rgba(112, 240, 187, 0.28);
  border-radius: 999px;
  color: #8ff2c9;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.agent-handoff-panel p {
  margin: 0;
  color: var(--wl-muted);
  font-size: 11px;
  line-height: 1.5;
}

.agent-handoff-meta {
  display: grid;
  gap: 6px;
  margin: 0;
}

.agent-handoff-meta div {
  min-width: 0;
}

.agent-handoff-meta dt {
  color: rgba(var(--wl-gold-rgb), 0.76);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.agent-handoff-meta dd {
  min-width: 0;
  margin: 2px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 800;
  line-height: 1.45;
}

.agent-handoff-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}

.agent-handoff-action {
  display: inline-flex;
  min-width: 0;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.2);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-size: 11px;
  font-weight: 850;
}

.agent-handoff-action span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-handoff-action.save {
  border-color: rgba(var(--wl-gold-rgb), 0.28);
  background: rgba(var(--wl-gold-rgb), 0.09);
  color: #fff7de;
}

.agent-handoff-action:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

.handoff-capsule-preview {
  max-height: 180px;
  margin: 0;
  overflow: auto;
  padding: 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.74);
  color: var(--wl-text-soft);
  font-size: 10px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.sync-action,
.replay-export-action,
.manifest-action,
.skill-action {
  display: inline-flex;
  min-width: 0;
  min-height: 34px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.24);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 850;
  cursor: pointer;
}

.sync-action span,
.replay-export-action span,
.manifest-action span,
.skill-action span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sync-action:not(.secondary) {
  border-color: rgba(var(--wl-gold-rgb), 0.42);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff7de;
}

.sync-action:disabled,
.replay-export-action:disabled,
.manifest-action:disabled,
.skill-action:disabled {
  cursor: default;
  opacity: 0.58;
}

.sync-action:disabled,
.replay-export-action:disabled,
.manifest-action:disabled,
.skill-action:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

textarea {
  width: 100%;
  min-height: 142px;
  resize: vertical;
  padding: 12px;
  border: 1px solid var(--wl-border);
  border-radius: var(--wl-radius-sm);
  background: rgba(2, 5, 10, 0.76);
  color: var(--wl-text);
  line-height: 1.6;
}

.primary-action {
  width: 100%;
  margin-top: 10px;
  cursor: pointer;
}

.branch-list {
  display: grid;
  gap: 8px;
}

.branch-button {
  width: 100%;
  min-height: 56px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.035);
  color: var(--wl-text-soft);
  text-align: left;
  cursor: pointer;
}

.branch-button span,
.artifact-item strong,
.trace-item strong,
.skill-item strong {
  display: block;
  color: var(--wl-text);
  font-weight: 850;
}

.branch-button small,
.artifact-item small,
.trace-item small,
.skill-item small,
.episode-card small {
  color: var(--wl-muted-soft);
  font-weight: 750;
}

.branch-button.active {
  border-color: var(--wl-border-gold);
  background: rgba(var(--wl-gold-rgb), 0.11);
  box-shadow: var(--wl-focus-ring);
}

.branch-button.focused {
  border-color: rgba(var(--wl-gold-rgb), 0.58);
  background: rgba(var(--wl-gold-rgb), 0.09);
  box-shadow:
    inset 0 0 0 1px rgba(var(--wl-gold-rgb), 0.14),
    0 0 18px rgba(var(--wl-gold-rgb), 0.12);
}

.contract-panel dl {
  display: grid;
  gap: 8px;
  margin: 0;
}

.contract-panel div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  color: var(--wl-muted);
}

.contract-panel dt {
  color: var(--wl-text-soft);
  font-weight: 800;
}

.contract-panel dd {
  margin: 0;
}

.episode-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.episode-card,
.artifact-item,
.trace-item,
.skill-item {
  padding: 12px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.035);
}

.episode-card {
  display: grid;
  width: 100%;
  gap: 7px;
  color: var(--wl-text-soft);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
}

.skill-item {
  cursor: pointer;
  outline: none;
}

.skill-item:hover,
.skill-item:focus-visible {
  border-color: rgba(var(--wl-gold-rgb), 0.42);
  background: rgba(var(--wl-gold-rgb), 0.075);
}

.episode-card:hover,
.episode-card:focus-visible,
.episode-card.active {
  border-color: rgba(var(--wl-gold-rgb), 0.48);
  background: rgba(var(--wl-gold-rgb), 0.105);
  box-shadow: 0 0 0 1px rgba(var(--wl-gold-rgb), 0.12);
  outline: none;
}

.episode-card .episode-actor {
  display: inline-flex;
  justify-self: start;
  margin-bottom: 8px;
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.episode-card strong {
  display: block;
  color: var(--wl-text);
  line-height: 1.55;
}

.episode-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.episode-metrics span {
  display: inline-flex;
  min-height: 20px;
  align-items: center;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 900;
  line-height: 18px;
}

.artifact-panel,
.gate-panel,
.trace-panel,
.skill-panel,
.event-panel {
  display: grid;
  gap: 10px;
}

.artifact-scope,
.gate-scope {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}

.artifact-scope-button,
.gate-scope-button {
  display: inline-flex;
  min-width: 0;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-muted-soft);
  cursor: pointer;
}

.artifact-scope-button.active,
.gate-scope-button.active {
  border-color: rgba(var(--wl-gold-rgb), 0.42);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff4cc;
}

.artifact-scope-button span,
.artifact-scope-button small,
.gate-scope-button span,
.gate-scope-button small {
  overflow: hidden;
  color: inherit;
  font-size: 11px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-scope-button small,
.gate-scope-button small {
  font-size: 10px;
  opacity: 0.82;
}

.artifact-mcp-message {
  margin: 0;
  padding: 8px 9px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-muted);
  font-size: 11px;
  font-weight: 750;
  line-height: 1.45;
}

.artifact-list,
.gate-run-list {
  display: grid;
  gap: 8px;
}

.artifact-row,
.gate-run-row {
  display: grid;
  gap: 5px;
}

.artifact-item,
.gate-run-item {
  display: grid;
  width: 100%;
  gap: 6px;
  color: var(--wl-text-soft);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
}

.artifact-type,
.gate-run-status {
  justify-self: start;
  max-width: 100%;
  min-height: 20px;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.075);
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 900;
  line-height: 18px;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}

.artifact-item strong,
.artifact-item small,
.artifact-item em,
.gate-run-item strong,
.gate-run-item p,
.gate-run-item em,
.gate-run-meta dd {
  min-width: 0;
  overflow-wrap: anywhere;
}

.artifact-mcp-button,
.gate-mcp-button {
  display: inline-flex;
  min-width: 0;
  min-height: 27px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-muted);
  cursor: pointer;
  font-size: 10px;
  font-weight: 850;
}

.artifact-mcp-button span,
.gate-mcp-button span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gate-support-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.gate-support-strip span {
  display: inline-flex;
  min-height: 20px;
  align-items: center;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 900;
  line-height: 1.2;
}

.gate-run-item strong {
  display: block;
  color: var(--wl-text);
  font-weight: 900;
  line-height: 1.35;
}

.gate-run-item p {
  margin: 0;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.5;
}

.gate-run-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
  margin: 0;
}

.gate-run-meta div {
  min-width: 0;
  padding: 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.1);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.13);
}

.gate-run-meta dt {
  color: rgba(var(--wl-gold-rgb), 0.72);
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
}

.gate-run-meta dd {
  margin: 3px 0 0;
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 800;
  line-height: 1.35;
}

.artifact-item em,
.gate-run-item em {
  color: rgba(var(--wl-gold-rgb), 0.82);
  font-size: 11px;
  font-style: normal;
  font-weight: 850;
  line-height: 1.35;
}

.trace-item > div,
.skill-item > div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.skill-item > .skill-genome-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 5px;
}

.skill-genome-chips span {
  display: inline-flex;
  min-height: 20px;
  align-items: center;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-muted-soft);
  font-size: 10px;
  font-weight: 900;
  line-height: 18px;
}

.skill-meta {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.skill-meta small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-action {
  flex: 0 0 auto;
  min-height: 30px;
  padding: 0 9px;
}

.event-filter {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 6px;
}

.event-filter-button {
  display: inline-flex;
  min-width: 0;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.055);
  color: var(--wl-muted-soft);
  cursor: pointer;
}

.event-filter-button.active {
  border-color: rgba(var(--wl-gold-rgb), 0.42);
  background: rgba(var(--wl-gold-rgb), 0.12);
  color: #fff4cc;
}

.event-filter-button span {
  overflow: hidden;
  font-size: 11px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-filter-button small {
  color: inherit;
  font-size: 10px;
  font-weight: 900;
  opacity: 0.82;
}

.event-audit-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 6px;
}

.event-audit-toolbar input,
.event-audit-toolbar select {
  min-width: 0;
  min-height: 32px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(2, 11, 16, 0.78);
  color: var(--wl-text);
  font-size: 11px;
  font-weight: 850;
  outline: none;
  padding: 0 9px;
}

.event-audit-toolbar input::placeholder {
  color: rgba(var(--wl-text-rgb), 0.45);
}

.event-audit-button {
  display: inline-flex;
  min-width: 0;
  min-height: 32px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text);
  cursor: pointer;
  font-size: 11px;
  font-weight: 900;
}

.event-audit-button span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-audit-button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.event-audit-status {
  min-width: 0;
  overflow: hidden;
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 850;
  line-height: 1.5;
  margin: -2px 0 0;
  text-overflow: ellipsis;
}

.event-list {
  display: grid;
  gap: 10px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 2px;
}

.event-pagination {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
}

.event-pagination > span {
  min-width: 0;
  overflow: hidden;
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 850;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-page-button {
  display: inline-flex;
  min-width: 0;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 0 9px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-size: 11px;
  font-weight: 850;
}

.event-page-button:disabled {
  cursor: not-allowed;
  opacity: 0.52;
}

.event-page-button span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-item {
  display: grid;
  grid-template-columns: 10px minmax(0, 1fr);
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 12px 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(255, 255, 255, 0.035);
  color: var(--wl-text-soft);
  cursor: pointer;
  text-align: left;
}

.event-item:disabled {
  cursor: default;
  opacity: 1;
}

.event-item.preview {
  border-style: dashed;
}

.event-item.selected {
  border-color: rgba(var(--wl-gold-rgb), 0.48);
  background: rgba(var(--wl-gold-rgb), 0.09);
  box-shadow: inset 0 0 0 1px rgba(var(--wl-gold-rgb), 0.12);
}

.event-dot {
  width: 9px;
  height: 9px;
  margin-top: 6px;
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.72);
  box-shadow: 0 0 16px rgba(var(--wl-cyan-rgb), 0.45);
}

.event-item.kind-run .event-dot {
  background: rgba(var(--wl-gold-rgb), 0.86);
  box-shadow: 0 0 16px rgba(var(--wl-gold-rgb), 0.4);
}

.event-item.kind-branch .event-dot {
  background: rgba(112, 240, 187, 0.84);
  box-shadow: 0 0 16px rgba(112, 240, 187, 0.35);
}

.event-item.kind-tool .event-dot {
  background: rgba(157, 184, 255, 0.86);
  box-shadow: 0 0 16px rgba(157, 184, 255, 0.35);
}

.event-item.kind-skill .event-dot {
  background: rgba(255, 213, 117, 0.88);
  box-shadow: 0 0 16px rgba(255, 213, 117, 0.32);
}

.event-body,
.event-title,
.event-summary,
.event-link-row {
  min-width: 0;
}

.event-body {
  display: grid;
  gap: 6px;
}

.event-title {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.event-title strong {
  overflow: hidden;
  color: var(--wl-text);
  font-size: 13px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-title time {
  flex: 0 0 auto;
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
}

.event-summary {
  overflow: hidden;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.5;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-link-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.event-link-chip {
  display: inline-flex;
  min-height: 20px;
  align-items: center;
  padding: 0 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
}

.replay-lane {
  display: grid;
  gap: 8px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(180deg, rgba(var(--wl-cyan-rgb), 0.07), rgba(var(--wl-gold-rgb), 0.035)),
    rgba(0, 0, 0, 0.14);
}

.replay-lane-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.replay-lane-head strong {
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.replay-lane-head span {
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 850;
}

.replay-steps {
  display: grid;
  gap: 7px;
}

.replay-step {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  width: 100%;
  min-width: 0;
  gap: 8px;
  padding: 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
}

.replay-step:hover,
.replay-step:focus-visible,
.replay-step.active {
  border-color: rgba(var(--wl-gold-rgb), 0.48);
  background: rgba(var(--wl-gold-rgb), 0.095);
  outline: none;
}

.replay-index {
  display: inline-flex;
  width: 30px;
  height: 30px;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.25);
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-gold);
  font-size: 10px;
  font-weight: 900;
}

.replay-step-body {
  display: grid;
  min-width: 0;
  gap: 5px;
}

.replay-step-body strong,
.replay-step-body small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.replay-step-body strong {
  color: var(--wl-text);
  font-size: 12px;
  font-weight: 900;
}

.replay-step-body small {
  color: var(--wl-muted);
  font-size: 11px;
  font-weight: 800;
}

.replay-delta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.replay-delta-row span {
  display: inline-flex;
  min-height: 18px;
  align-items: center;
  padding: 0 6px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.06);
  color: var(--wl-muted-soft);
  font-size: 9px;
  font-weight: 900;
  line-height: 16px;
}

.event-body small {
  display: block;
  overflow: hidden;
  color: var(--wl-muted-soft);
  font-size: 11px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-detail {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.22);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-gold-rgb), 0.055);
}

.event-detail-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.event-detail-head h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 15px;
  font-weight: 900;
}

.event-detail-summary {
  margin: 0;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.6;
}

.event-manifest-actions {
  display: flex;
  margin-top: 10px;
}

.event-manifest-actions .manifest-action {
  width: 100%;
}

.event-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 0;
}

.event-meta-grid div {
  min-width: 0;
  padding: 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
}

.event-meta-grid dt {
  color: rgba(var(--wl-gold-rgb), 0.74);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.event-meta-grid dd {
  margin: 4px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 800;
  line-height: 1.45;
}

.decision-snapshot {
  display: grid;
  gap: 9px;
  padding: 10px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.24);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(135deg, rgba(var(--wl-gold-rgb), 0.09), rgba(var(--wl-cyan-rgb), 0.04)),
    rgba(0, 0, 0, 0.16);
}

.decision-snapshot-head {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.decision-snapshot-head strong {
  color: var(--wl-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.decision-snapshot-head span {
  display: inline-flex;
  max-width: 45%;
  min-height: 22px;
  align-items: center;
  padding: 0 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.2);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  font-size: 10px;
  font-weight: 900;
  overflow-wrap: anywhere;
  text-transform: uppercase;
}

.decision-snapshot dl {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
  margin: 0;
}

.decision-snapshot div {
  min-width: 0;
}

.decision-snapshot dt {
  color: rgba(var(--wl-gold-rgb), 0.78);
  font-size: 9px;
  font-weight: 900;
  text-transform: uppercase;
}

.decision-snapshot dd {
  margin: 3px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-text);
  font-size: 11px;
  font-weight: 850;
  line-height: 1.45;
}

.event-detail-sections {
  display: grid;
  gap: 8px;
}

.event-detail-section {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.event-detail-section strong {
  color: var(--wl-text);
  font-size: 12px;
  font-weight: 900;
}

.event-detail-section p {
  margin: 0;
  color: var(--wl-muted-soft);
  font-size: 11px;
  line-height: 1.5;
}

.event-detail-items {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  min-width: 0;
}

.event-detail-token {
  display: inline-flex;
  max-width: 100%;
  min-height: 22px;
  align-items: center;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.18);
  padding: 0 7px;
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.07);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-size: 10px;
  font-weight: 850;
  font-family: inherit;
  line-height: 1.2;
  overflow-wrap: anywhere;
}

.event-detail-token.focused {
  border-color: rgba(var(--wl-gold-rgb), 0.62);
  background: rgba(var(--wl-gold-rgb), 0.16);
  color: #fff7de;
  box-shadow: 0 0 12px rgba(var(--wl-gold-rgb), 0.14);
}

.event-detail-token.disabled,
.event-detail-token:disabled {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.035);
  color: rgba(179, 201, 206, 0.52);
  cursor: default;
}

.event-focus-message {
  margin: 0;
  padding: 8px 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.045);
  color: var(--wl-muted);
  font-size: 11px;
  line-height: 1.5;
}

.focus-dossier {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.2);
  border-radius: var(--wl-radius-sm);
  background:
    linear-gradient(135deg, rgba(var(--wl-cyan-rgb), 0.08), rgba(var(--wl-gold-rgb), 0.05)),
    rgba(255, 255, 255, 0.025);
}

.focus-dossier-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}

.focus-dossier-head h3 {
  margin: 0;
  color: var(--wl-text);
  font-size: 14px;
  font-weight: 900;
  line-height: 1.35;
}

.focus-dossier > p {
  margin: 0;
  color: var(--wl-muted);
  font-size: 12px;
  line-height: 1.6;
}

.focus-dossier-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 0;
}

.focus-dossier-meta div {
  min-width: 0;
  padding: 8px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.12);
  border-radius: var(--wl-radius-sm);
  background: rgba(0, 0, 0, 0.14);
}

.focus-dossier-meta dt {
  color: rgba(var(--wl-gold-rgb), 0.76);
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
}

.focus-dossier-meta dd {
  margin: 4px 0 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 800;
  line-height: 1.45;
}

.focus-dossier-links {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.focus-dossier-link-row {
  display: inline-flex;
  max-width: 100%;
  min-width: 0;
  align-items: center;
  gap: 4px;
}

.focus-dossier-link {
  display: inline-flex;
  max-width: 100%;
  min-height: 22px;
  align-items: center;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.17);
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.065);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-family: inherit;
  font-size: 10px;
  font-weight: 850;
  line-height: 1.2;
  overflow-wrap: anywhere;
  text-align: left;
  transition: border-color 0.16s ease, background 0.16s ease, color 0.16s ease, box-shadow 0.16s ease;
}

.focus-dossier-link-row .focus-dossier-link {
  min-width: 0;
}

.focus-dossier-link:hover,
.focus-dossier-link:focus-visible {
  border-color: rgba(var(--wl-cyan-rgb), 0.44);
  background: rgba(var(--wl-cyan-rgb), 0.12);
  color: var(--wl-text);
  outline: none;
}

.focus-dossier-link.active {
  border-color: rgba(var(--wl-gold-rgb), 0.64);
  background: rgba(var(--wl-gold-rgb), 0.13);
  color: var(--wl-gold);
  box-shadow: 0 0 12px rgba(var(--wl-gold-rgb), 0.13);
}

.focus-dossier-link.disabled,
.focus-dossier-link:disabled {
  cursor: default;
  opacity: 0.72;
}

.focus-dossier-mcp-button {
  display: inline-flex;
  min-height: 22px;
  flex: 0 0 auto;
  align-items: center;
  gap: 4px;
  padding: 0 7px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.22);
  border-radius: 999px;
  background: rgba(var(--wl-gold-rgb), 0.08);
  color: var(--wl-gold);
  cursor: pointer;
  font-family: inherit;
  font-size: 10px;
  font-weight: 850;
  line-height: 1.2;
  transition: border-color 0.16s ease, background 0.16s ease, color 0.16s ease, box-shadow 0.16s ease;
}

.focus-dossier-mcp-button:hover,
.focus-dossier-mcp-button:focus-visible {
  border-color: rgba(var(--wl-gold-rgb), 0.52);
  background: rgba(var(--wl-gold-rgb), 0.14);
  color: #fff7d9;
  outline: none;
  box-shadow: 0 0 12px rgba(var(--wl-gold-rgb), 0.12);
}

.focus-dossier-mcp-button:disabled {
  cursor: default;
  opacity: 0.55;
}

.focus-dossier > .focus-dossier-mcp-message {
  padding: 7px 9px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.16);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-gold-rgb), 0.055);
  color: var(--wl-text-soft);
  font-size: 11px;
  font-weight: 750;
  line-height: 1.45;
}

.detail-modal-backdrop {
  position: fixed;
  z-index: 60;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 18px;
  background: rgba(0, 0, 0, 0.62);
  backdrop-filter: blur(10px);
}

.detail-modal {
  display: grid;
  width: min(860px, 100%);
  max-height: min(720px, calc(100vh - 36px));
  gap: 10px;
  padding: 14px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.22);
  border-radius: var(--wl-radius-md);
  background:
    linear-gradient(135deg, rgba(var(--wl-cyan-rgb), 0.08), rgba(var(--wl-gold-rgb), 0.05)),
    rgba(1, 6, 11, 0.96);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.48);
}

.detail-modal-head {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.detail-modal-head div {
  display: grid;
  min-width: 0;
  gap: 3px;
}

.detail-modal-head .eyebrow {
  margin: 0;
}

.detail-modal-head strong,
.detail-modal-head span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail-modal-head strong {
  color: var(--wl-text);
  font-size: 16px;
  font-weight: 950;
}

.detail-modal-head span {
  color: var(--wl-muted);
  font-family: var(--wl-mono);
  font-size: 11px;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.detail-modal-head button {
  flex: 0 0 auto;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.22);
  border-radius: var(--wl-radius-sm);
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  cursor: pointer;
  font-size: 11px;
  font-weight: 850;
}

.detail-modal pre {
  max-height: calc(min(720px, 100vh - 36px) - 112px);
  margin: 0;
  overflow: auto;
  padding: 12px;
  border: 1px solid rgba(var(--wl-cyan-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.86);
  color: var(--wl-text-soft);
  font-size: 11px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.focus-dossier-mcp-preview {
  display: grid;
  gap: 6px;
  padding: 8px;
  border: 1px solid rgba(var(--wl-gold-rgb), 0.14);
  border-radius: var(--wl-radius-sm);
  background: rgba(1, 6, 11, 0.56);
}

.focus-dossier-mcp-preview span {
  min-width: 0;
  overflow-wrap: anywhere;
  color: var(--wl-text-soft);
  font-family: var(--wl-mono);
  font-size: 10px;
  line-height: 1.45;
}

.focus-dossier-mcp-preview pre {
  max-height: 104px;
  margin: 0;
  overflow: auto;
  color: var(--wl-muted);
  font-size: 10px;
  line-height: 1.45;
  white-space: pre-wrap;
}

.trace-item.focused,
.gate-item.focused,
.gate-run-item.focused,
.artifact-item.focused,
.skill-item.focused {
  border-color: rgba(var(--wl-gold-rgb), 0.58);
  background: rgba(var(--wl-gold-rgb), 0.09);
  box-shadow:
    inset 0 0 0 1px rgba(var(--wl-gold-rgb), 0.14),
    0 0 18px rgba(var(--wl-gold-rgb), 0.12);
}

.status-pill {
  display: inline-flex;
  min-height: 24px;
  align-items: center;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(var(--wl-cyan-rgb), 0.08);
  color: var(--wl-text-soft);
  font-size: 12px;
  font-weight: 800;
}

.status-pill.approval_required,
.gate-item.review,
.gate-run-item.review {
  border-color: rgba(var(--wl-gold-rgb), 0.32);
  background: rgba(var(--wl-gold-rgb), 0.1);
}

.gate-item.passed,
.gate-run-item.passed {
  border-color: rgba(112, 240, 187, 0.32);
  background: rgba(112, 240, 187, 0.08);
}

.gate-item.candidate,
.gate-run-item.candidate {
  border-color: rgba(157, 184, 255, 0.32);
  background: rgba(157, 184, 255, 0.08);
}

@media (max-width: 1280px) {
  .agent-shell {
    grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  }

  .inspect-rail {
    grid-column: 1 / -1;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .agent-workbench {
    padding: 12px;
  }

  .agent-header,
  .agent-shell,
  .inspect-rail,
  .episode-strip {
    grid-template-columns: 1fr;
  }

  .agent-header {
    display: grid;
  }

  .agent-actions {
    justify-content: flex-start;
  }

  .ledger-actions,
  .skill-meta {
    grid-template-columns: 1fr;
  }

  .ledger-actions,
  .skill-meta {
    display: grid;
  }

  .run-selector-head {
    align-items: stretch;
    flex-direction: column;
  }

  .run-selector-refresh {
    width: 100%;
  }

  .run-selector-filters,
  .run-maintenance,
  .run-selector-bulk,
  .run-selector-pagination {
    grid-template-columns: 1fr;
  }

  .run-selector-item {
    grid-template-columns: 1fr;
  }

  .run-selector-compare,
  .run-selector-archive {
    width: 100%;
  }

  .skill-action {
    width: 100%;
  }

  .event-filter {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .event-audit-toolbar {
    grid-template-columns: 1fr;
  }

  .event-pagination {
    grid-template-columns: 1fr;
  }
}
</style>
