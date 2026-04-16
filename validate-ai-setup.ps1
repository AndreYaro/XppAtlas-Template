param(
    [string]$RootPath = "."
)

$resolvedRoot = (Resolve-Path -Path $RootPath).Path
$failureCount = 0
$warningCount = 0
$passCount = 0

function Add-Pass {
    param([string]$Message)

    $script:passCount++
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Add-Warning {
    param([string]$Message)

    $script:warningCount++
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Add-Fail {
    param([string]$Message)

    $script:failureCount++
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Test-RequiredPath {
    param([string]$RelativePath)

    $targetPath = Join-Path -Path $resolvedRoot -ChildPath $RelativePath
    if (Test-Path -Path $targetPath) {
        Add-Pass "Found $RelativePath"
        return $true
    }

    Add-Fail "Missing $RelativePath"
    return $false
}

function Test-FileContains {
    param(
        [string]$RelativePath,
        [string]$Pattern,
        [string]$Description
    )

    $targetPath = Join-Path -Path $resolvedRoot -ChildPath $RelativePath
    if (-not (Test-Path -Path $targetPath)) {
        Add-Fail "Cannot validate $Description because $RelativePath is missing"
        return
    }

    if (Select-String -Path $targetPath -Pattern $Pattern -Quiet) {
        Add-Pass $Description
        return
    }

    Add-Fail "$Description not found in $RelativePath"
}

Write-Host "AI setup validation for $resolvedRoot" -ForegroundColor Cyan

$requiredPaths = @(
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "context_setup.md",
    ".claude\agents\d365-developer.md",
    ".claude\agents\d365-architect.md",
    "skills\README.md",
    "skills\d365-developer\SKILL.md",
    "skills\d365-developer\agents\openai.yaml",
    "skills\d365-architect\SKILL.md",
    "skills\d365-architect\agents\openai.yaml"
)

foreach ($requiredPath in $requiredPaths) {
    Test-RequiredPath -RelativePath $requiredPath | Out-Null
}

$sharedSkills = @(
    "audit-arch",
    "design-integration",
    "explain",
    "fix-perf",
    "gen-batch",
    "gen-coc",
    "gen-entity",
    "gen-service",
    "new-task",
    "prep-comment",
    "review-code"
)

foreach ($skill in $sharedSkills) {
    Test-RequiredPath -RelativePath ".claude\skills\$skill\SKILL.md" | Out-Null
    Test-RequiredPath -RelativePath "skills\$skill\SKILL.md" | Out-Null
}

$claudeSkillPath = Join-Path -Path $resolvedRoot -ChildPath ".claude\skills"
$codexSkillPath = Join-Path -Path $resolvedRoot -ChildPath "skills"
$allowedCodexOnlySkills = @("d365-architect", "d365-developer")

if ((Test-Path -Path $claudeSkillPath) -and (Test-Path -Path $codexSkillPath)) {
    $claudeSkillNames = Get-ChildItem -Path $claudeSkillPath -Directory | Select-Object -ExpandProperty Name
    $codexSkillNames = Get-ChildItem -Path $codexSkillPath -Directory | Select-Object -ExpandProperty Name

    $missingInCodex = $claudeSkillNames | Where-Object { $_ -notin $codexSkillNames }
    $unexpectedCodex = $codexSkillNames | Where-Object { ($_ -notin $claudeSkillNames) -and ($_ -notin $allowedCodexOnlySkills) }

    if ($missingInCodex.Count -eq 0) {
        Add-Pass "Every Claude shared skill is mirrored in skills/"
    }
    else {
        Add-Fail ("Missing mirrored Codex skill folders: " + ($missingInCodex -join ", "))
    }

    if ($unexpectedCodex.Count -eq 0) {
        Add-Pass "No unexpected Codex-only skill folders were found"
    }
    else {
        Add-Fail ("Unexpected Codex-only skill folders: " + ($unexpectedCodex -join ", "))
    }
}

Test-FileContains -RelativePath "AGENTS.md" -Pattern "d365-developer" -Description "AGENTS.md lists d365-developer"
Test-FileContains -RelativePath "AGENTS.md" -Pattern "d365-architect" -Description "AGENTS.md lists d365-architect"
Test-FileContains -RelativePath "AGENTS.md" -Pattern "Shared Skills" -Description "AGENTS.md documents shared skills"
Test-FileContains -RelativePath "CLAUDE.md" -Pattern "Cross-Tool Agent Parity" -Description "CLAUDE.md documents cross-tool agent parity"
Test-FileContains -RelativePath "CLAUDE.md" -Pattern "Shared Skills" -Description "CLAUDE.md documents shared skills"
Test-FileContains -RelativePath "GEMINI.md" -Pattern "Shared Specialist Agents" -Description "GEMINI.md documents shared specialist agents"
Test-FileContains -RelativePath "GEMINI.md" -Pattern "Shared Skills" -Description "GEMINI.md documents shared skills"
Test-FileContains -RelativePath ".claude\skills\new-task\SKILL.md" -Pattern "Models/\{ModelName\}/Tasks/\{TaskID\}_\{TaskName\}/" -Description "Claude new-task skill uses model-based task paths"
Test-FileContains -RelativePath "skills\new-task\SKILL.md" -Pattern "Models/\{ModelName\}/Tasks/\{TaskID\}_\{TaskName\}/" -Description "Codex new-task skill uses model-based task paths"

if (-not (Test-Path -Path (Join-Path -Path $resolvedRoot -ChildPath "Models"))) {
    Add-Warning "Models/ was not found, so this repository may not be a project template clone"
}

Write-Host ""
Write-Host "Summary: $passCount passed, $warningCount warnings, $failureCount failed" -ForegroundColor Cyan

if ($failureCount -gt 0) {
    exit 1
}

exit 0
