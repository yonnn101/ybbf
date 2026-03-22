# Fail fast if sensitive files are tracked by Git (run from repo root).
# Does not rewrite history — see SECURITY.md for git-filter-repo / BFG.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

if (-not (Test-Path ".git")) {
    Write-Host "No .git directory — not a Git repo. Initialize only after confirming .env is not staged."
    exit 0
}

$bad = @(
    git ls-files 2>$null | Where-Object {
        $_ -match '(^|/)\.env$' -or
        $_ -match '\.pem$' -or
        $_ -match '\.key$' -or
        $_ -match '(^|/)id_rsa$' -or
        $_ -match '(^|/)id_ed25519$'
    }
)

if ($bad.Count -gt 0) {
    Write-Error "Tracked files that should not be in Git:`n  $($bad -join "`n  ")`nRemove from index: git rm --cached <file>  See SECURITY.md for history cleanup."
    exit 1
}

Write-Host "OK: no .env / key files tracked by Git."
