param(
    [string]$Owner = "AdityaMJN",
    [string]$Repo = "stock-research-agent",
    [int]$ProjectNumber = 1,
    [switch]$AddToProject,
    [switch]$SkipLabelSetup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $env:GITHUB_TOKEN) {
    throw "GITHUB_TOKEN is not set. Create a classic token with repo + project scopes and set it in the terminal before running."
}

$headers = @{
    Authorization = "Bearer $($env:GITHUB_TOKEN)"
    Accept        = "application/vnd.github+json"
    "User-Agent" = "stock-research-agent-issue-seed"
}

$graphHeaders = @{
    Authorization = "Bearer $($env:GITHUB_TOKEN)"
    Accept        = "application/vnd.github+json"
    "User-Agent" = "stock-research-agent-issue-seed"
}

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color,
        [string]$Description
    )

    $url = "https://api.github.com/repos/$Owner/$Repo/labels/$([uri]::EscapeDataString($Name))"
    try {
        Invoke-RestMethod -Method Get -Uri $url -Headers $headers | Out-Null
    }
    catch {
        $createUrl = "https://api.github.com/repos/$Owner/$Repo/labels"
        $body = @{ name = $Name; color = $Color; description = $Description } | ConvertTo-Json
        Invoke-RestMethod -Method Post -Uri $createUrl -Headers $headers -Body $body -ContentType "application/json" | Out-Null
    }
}

function New-Issue {
    param(
        [string]$Title,
        [string]$Body,
        [string[]]$Labels
    )

    $url = "https://api.github.com/repos/$Owner/$Repo/issues"
    $payload = @{ title = $Title; body = $Body; labels = $Labels } | ConvertTo-Json -Depth 5
    return Invoke-RestMethod -Method Post -Uri $url -Headers $headers -Body $payload -ContentType "application/json"
}

function Get-ProjectId {
        $query = @'
query($login: String!, $number: Int!) {
  user(login: $login) {
    projectV2(number: $number) {
      id
      title
    }
  }
}
'@
    $payload = @{ query = $query; variables = @{ login = $Owner; number = $ProjectNumber } } | ConvertTo-Json -Depth 6
    $res = Invoke-RestMethod -Method Post -Uri "https://api.github.com/graphql" -Headers $graphHeaders -Body $payload -ContentType "application/json"
    if (-not $res.data.user.projectV2.id) {
        throw "Could not resolve ProjectV2 #$ProjectNumber for user $Owner"
    }
    return $res.data.user.projectV2.id
}

function Add-IssueToProject {
    param(
        [string]$ProjectId,
        [string]$IssueNodeId
    )

        $mutation = @'
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item {
      id
    }
  }
}
'@
    $payload = @{ query = $mutation; variables = @{ projectId = $ProjectId; contentId = $IssueNodeId } } | ConvertTo-Json -Depth 6
    Invoke-RestMethod -Method Post -Uri "https://api.github.com/graphql" -Headers $graphHeaders -Body $payload -ContentType "application/json" | Out-Null
}

$labelCatalog = @(
    @{ n = "track:data-platform"; c = "1D76DB"; d = "Data platform and APIs" },
    @{ n = "track:ai-intelligence"; c = "5319E7"; d = "AI feature and recommendation engine" },
    @{ n = "track:portfolio-execution"; c = "0E8A16"; d = "Paper/live execution and portfolio" },
    @{ n = "track:intraday"; c = "FBCA04"; d = "Intraday systems" },
    @{ n = "track:governance-risk"; c = "B60205"; d = "Risk, governance, and controls" },
    @{ n = "type:backend"; c = "0052CC"; d = "Backend implementation" },
    @{ n = "type:frontend"; c = "0E8A16"; d = "Frontend implementation" },
    @{ n = "type:data"; c = "5319E7"; d = "Data model and ingestion" },
    @{ n = "type:ml"; c = "6F42C1"; d = "ML and scoring" },
    @{ n = "type:infra"; c = "D93F0B"; d = "Infra and runbooks" },
    @{ n = "type:qa"; c = "C2E0C6"; d = "Testing and validation" },
    @{ n = "priority:critical"; c = "B60205"; d = "Critical priority" },
    @{ n = "priority:high"; c = "D93F0B"; d = "High priority" }
)

foreach ($l in $labelCatalog) {
    # no-op here; labels are created in guarded section below
}

$canUseLabels = $true
if ($SkipLabelSetup) {
    $canUseLabels = $false
    Write-Warning "Skipping label setup because -SkipLabelSetup was provided. Issues will be created without labels."
}
else {
    foreach ($l in $labelCatalog) {
        try {
            Ensure-Label -Name $l.n -Color $l.c -Description $l.d
        }
        catch {
            $canUseLabels = $false
            Write-Warning "Label setup failed (likely token permission issue). Continuing without labels."
            Write-Warning "To fix: use a token with repo write access (classic repo scope) and rerun without -SkipLabelSetup."
            break
        }
    }
}

$issues = @(
    @{ id = "SRA-001"; title = "Define trading KPIs and paper-to-live gates"; labels = @("track:governance-risk", "type:infra", "priority:critical"); depends = @(); ac = @("KPI document committed with thresholds", "Promotion decision matrix documented", "Formulas and data sources defined") },
    @{ id = "SRA-002"; title = "Define risk policy and hard stop controls"; labels = @("track:governance-risk", "type:infra", "priority:critical"); depends = @("SRA-001"); ac = @("Configurable hard limits", "Kill switch behavior tested", "Emergency flatten procedure documented") },
    @{ id = "SRA-003"; title = "Replace stocks list API with DB-backed query"; labels = @("track:data-platform", "type:backend", "priority:high"); depends = @("SRA-001"); ac = @("Endpoint DB-backed in production mode", "Pagination and filtering supported", "Unit tests for empty and normal states") },
    @{ id = "SRA-004"; title = "Implement stock detail API GET /api/v1/stocks/{symbol}"; labels = @("track:data-platform", "type:backend", "priority:high"); depends = @("SRA-003"); ac = @("Valid symbol returns profile and indicators", "Unknown symbol returns 404", "OpenAPI docs updated") },
    @{ id = "SRA-005"; title = "Implement stock history API GET /api/v1/stocks/{symbol}/history"; labels = @("track:data-platform", "type:backend", "priority:high"); depends = @("SRA-004"); ac = @("Supports from/to/interval", "Chart-ready ordered series", "Handles holidays cleanly") },
    @{ id = "SRA-006"; title = "Build frontend stock detail page /stocks/:symbol"; labels = @("track:data-platform", "type:frontend", "priority:high"); depends = @("SRA-004", "SRA-005"); ac = @("Detail and history API integrated", "Loading and error states", "Navigation from stocks list") },
    @{ id = "SRA-007"; title = "Remove hardcoded payloads from dashboard and jobs surfaces"; labels = @("track:data-platform", "type:backend", "priority:high"); depends = @("SRA-003"); ac = @("No static sample arrays", "Metric sources documented", "Deterministic fallback behavior") },
    @{ id = "SRA-008"; title = "Add job_runs persistence, retry policy, and structured logs"; labels = @("track:governance-risk", "type:backend", "priority:high"); depends = @("SRA-007"); ac = @("job_runs migration added", "Retry count captured", "Last N runs API available") },
    @{ id = "SRA-009"; title = "Add Sprint 1 integration tests for stock and job endpoints"; labels = @("track:governance-risk", "type:qa", "priority:high"); depends = @("SRA-004", "SRA-005", "SRA-008"); ac = @("Happy and failure path tests", "Run commands documented", "Seeded deterministic tests") },
    @{ id = "SRA-010"; title = "Add schema: promoter_snapshots, insider_trades, news_articles, news_signals"; labels = @("track:data-platform", "type:data", "priority:critical"); depends = @("SRA-009"); ac = @("Migration with rollback", "Indexes for symbol/date", "Retention policy defined") },
    @{ id = "SRA-011"; title = "Build promoter holdings ingestion job"; labels = @("track:data-platform", "type:data", "priority:high"); depends = @("SRA-010"); ac = @("Source connector implemented", "Duplicate-safe upsert", "Ingestion metrics logged") },
    @{ id = "SRA-012"; title = "Build insider transactions ingestion job"; labels = @("track:data-platform", "type:data", "priority:high"); depends = @("SRA-010"); ac = @("Historical backfill", "Validation rules", "Daily incremental mode") },
    @{ id = "SRA-013"; title = "Build multi-source news ingestion job"; labels = @("track:data-platform", "type:data", "priority:high"); depends = @("SRA-010"); ac = @("Multi-source adapters", "Time normalization", "Outage fallback") },
    @{ id = "SRA-014"; title = "Build NLP enrichment pipeline (entity, sentiment, event tagging)"; labels = @("track:ai-intelligence", "type:ml", "priority:critical"); depends = @("SRA-013"); ac = @("Entity linking by symbol/sector", "Sentiment and event confidence", "At least 90 percent enriched") },
    @{ id = "SRA-015"; title = "Implement ownership and news APIs for stock detail"; labels = @("track:data-platform", "type:backend", "priority:high"); depends = @("SRA-011", "SRA-012", "SRA-014"); ac = @("Ownership API implemented", "News API implemented", "Pagination and validation documented") },
    @{ id = "SRA-016"; title = "Add stock detail intelligence panels (ownership and news)"; labels = @("track:data-platform", "type:frontend", "priority:high"); depends = @("SRA-006", "SRA-015"); ac = @("Ownership trend panel", "News feed panel", "Stale and empty state handling") },
    @{ id = "SRA-017"; title = "Add data freshness SLAs and monitoring checks"; labels = @("track:governance-risk", "type:infra", "priority:high"); depends = @("SRA-011", "SRA-012", "SRA-013"); ac = @("SLA thresholds defined", "Daily checks automated", "Breach status exposed") },
    @{ id = "SRA-018"; title = "Add feature store schema and daily feature snapshot pipeline"; labels = @("track:ai-intelligence", "type:data", "priority:critical"); depends = @("SRA-015", "SRA-017"); ac = @("feature_snapshots schema", "Feature versioning", "Reproducible historical snapshots") },
    @{ id = "SRA-019"; title = "Implement hybrid scoring engine v1"; labels = @("track:ai-intelligence", "type:ml", "priority:critical"); depends = @("SRA-018"); ac = @("Externalized weight config", "Component scores persisted", "Universe run within SLA") },
    @{ id = "SRA-020"; title = "Implement recommendation APIs"; labels = @("track:ai-intelligence", "type:backend", "priority:high"); depends = @("SRA-019"); ac = @("Recommendation list endpoint", "Symbol recommendation endpoint", "Swagger updated") },
    @{ id = "SRA-021"; title = "Add explainability and evidence payload for recommendations"; labels = @("track:ai-intelligence", "type:backend", "priority:high"); depends = @("SRA-020"); ac = @("Top drivers in payload", "Evidence links present", "Audit persistence") },
    @{ id = "SRA-022"; title = "Add walk-forward validation pipeline"; labels = @("track:ai-intelligence", "type:ml", "priority:high"); depends = @("SRA-019"); ac = @("Rolling validation report", "Risk metrics by window", "Versioned report artifacts") },
    @{ id = "SRA-023"; title = "Add benchmark comparison report vs baseline screeners"; labels = @("track:portfolio-execution", "type:backend", "priority:high"); depends = @("SRA-022"); ac = @("Alpha, CAGR, drawdown, turnover", "Costs and slippage included", "Machine-readable export") },
    @{ id = "SRA-024"; title = "Add paper trading schema (accounts, orders, fills, snapshots)"; labels = @("track:portfolio-execution", "type:data", "priority:critical"); depends = @("SRA-023"); ac = @("Migration with FK integrity", "Snapshot model for equity curve", "Paper account seed") },
    @{ id = "SRA-025"; title = "Implement paper execution simulator (slippage, partial fills, rejection)"; labels = @("track:portfolio-execution", "type:backend", "priority:critical"); depends = @("SRA-024"); ac = @("Fill outcomes modeled", "Configurable slippage model", "Fee/slippage persisted") },
    @{ id = "SRA-026"; title = "Implement paper trading APIs"; labels = @("track:portfolio-execution", "type:backend", "priority:high"); depends = @("SRA-025"); ac = @("Order endpoint with validation", "Positions endpoint", "Performance endpoint") },
    @{ id = "SRA-027"; title = "Implement risk engine controls (position, sector, daily loss, kill switch)"; labels = @("track:governance-risk", "type:backend", "priority:critical"); depends = @("SRA-002", "SRA-026"); ac = @("Risk failures block orders", "Kill switch halts submits", "Breach events queryable") },
    @{ id = "SRA-028"; title = "Implement PnL, attribution, and cost-aware performance reports"; labels = @("track:portfolio-execution", "type:backend", "priority:high"); depends = @("SRA-026"); ac = @("Realized and unrealized separated", "Cost components explicit", "Daily and cumulative views") },
    @{ id = "SRA-029"; title = "Build paper trading dashboard page"; labels = @("track:portfolio-execution", "type:frontend", "priority:high"); depends = @("SRA-026", "SRA-028"); ac = @("Equity and drawdown widgets", "Orders and fills table", "Loading/error/empty states") },
    @{ id = "SRA-030"; title = "Add end-to-end paper replay tests"; labels = @("track:governance-risk", "type:qa", "priority:high"); depends = @("SRA-027", "SRA-029"); ac = @("Deterministic replay suite", "Risk block tests", "Regression drift thresholds") },
    @{ id = "SRA-031"; title = "Add intraday schema and ingestion pipeline"; labels = @("track:intraday", "type:data", "priority:critical"); depends = @("SRA-030"); ac = @("intraday_prices schema", "Configurable intervals", "Backfill plus incremental") },
    @{ id = "SRA-032"; title = "Implement intraday signal engine (breakout and VWAP pullback)"; labels = @("track:intraday", "type:ml", "priority:high"); depends = @("SRA-031"); ac = @("Two strategies implemented", "Confidence and rationale", "Latency SLA met") },
    @{ id = "SRA-033"; title = "Implement intraday session APIs"; labels = @("track:intraday", "type:backend", "priority:high"); depends = @("SRA-032"); ac = @("Run-session endpoint", "Signals endpoint", "Session details endpoint") },
    @{ id = "SRA-034"; title = "Implement intraday risk controls and session limits"; labels = @("track:intraday", "type:backend", "priority:critical"); depends = @("SRA-027", "SRA-033"); ac = @("Max trades/day and loss limits", "Time-window validation", "Auto-stop on breach") },
    @{ id = "SRA-035"; title = "Build intraday monitoring dashboard"; labels = @("track:intraday", "type:frontend", "priority:high"); depends = @("SRA-033", "SRA-034"); ac = @("Session PnL widgets", "Risk alert feed", "History drill-down") },
    @{ id = "SRA-036"; title = "Produce intraday evaluation report and stability gate"; labels = @("track:intraday", "type:qa", "priority:high"); depends = @("SRA-035"); ac = @("Evaluation report generated", "Failing strategies disabled", "Stability gate published") },
    @{ id = "SRA-037"; title = "Build promotion gate dashboard for paper-to-live decision"; labels = @("track:governance-risk", "type:frontend", "priority:critical"); depends = @("SRA-023", "SRA-036"); ac = @("All gates pass/fail visible", "Trend charts present", "Drill-down to evidence") },
    @{ id = "SRA-038"; title = "Implement broker adapter framework and dry-run live mode"; labels = @("track:portfolio-execution", "type:backend", "priority:critical"); depends = @("SRA-037"); ac = @("Stable adapter contract", "Dry-run sends no real orders", "Live adapter disabled by default") },
    @{ id = "SRA-039"; title = "Add trading mode switch with live safeguards"; labels = @("track:governance-risk", "type:infra", "priority:critical"); depends = @("SRA-038"); ac = @("PAPER or LIVE mode config", "LIVE blocked unless gates pass", "Fail-fast startup checks") },
    @{ id = "SRA-040"; title = "Write operational runbooks and incident playbooks"; labels = @("track:governance-risk", "type:infra", "priority:high"); depends = @("SRA-039"); ac = @("Startup/shutdown/rollback runbooks", "Incident playbooks", "Escalation checklist") },
    @{ id = "SRA-041"; title = "Run final UAT and go/no-go review"; labels = @("track:governance-risk", "type:qa", "priority:critical"); depends = @("SRA-040"); ac = @("UAT checklist complete", "Signed decision record", "Zero open critical defects") },
    @{ id = "SRA-042"; title = "Release v1 and enable post-launch monitoring"; labels = @("track:governance-risk", "type:infra", "priority:critical"); depends = @("SRA-041"); ac = @("Release notes and tag", "Monitoring and alerts enabled", "2-week post-launch report template") }
)

$projectId = $null
if ($AddToProject) {
    $projectId = Get-ProjectId
    Write-Host "Resolved project id for user $Owner project #$ProjectNumber"
}

$created = @()
foreach ($i in $issues) {
    $title = "[$($i.id)] $($i.title)"
    $dependsText = if ($i.depends.Count -eq 0) { "none" } else { ($i.depends -join ", ") }
    $acText = ($i.ac | ForEach-Object { "- $_" }) -join "`n"
    $issueLabels = if ($canUseLabels) { $i.labels } else { @() }
    $body = @"
## Summary
$($i.title)

## Dependency
$dependsText

## Acceptance Criteria
$acText

## Notes
- Keep issue id prefix ($($i.id)) in title for dependency tracing.
- Link PRs and test evidence before closing.
"@

    $resp = New-Issue -Title $title -Body $body -Labels $issueLabels
    $created += [PSCustomObject]@{
        key    = $i.id
        number = $resp.number
        url    = $resp.html_url
        nodeId = $resp.node_id
    }
    Write-Host "Created $($i.id) -> #$($resp.number)"

    if ($AddToProject) {
        Add-IssueToProject -ProjectId $projectId -IssueNodeId $resp.node_id
        Write-Host "Added #$($resp.number) to project #$ProjectNumber"
    }
}

Write-Host ""
Write-Host "Created issues summary:"
$created | Format-Table -AutoSize
