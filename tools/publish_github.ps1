param([string]$Repo='Tianyao1234567/7215-project',[string]$Tag='member04-baseline-20261105')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$env:GH_CONFIG_DIR=Join-Path $root '.runtime\github_cli_auth'
$env:GIT_TERMINAL_PROMPT='0';$env:GCM_INTERACTIVE='never';$env:GH_PROMPT_DISABLED='1'
$assets=Join-Path $root '.runtime\github_publication\assets'
$statePath=Join-Path $root '.runtime\github_publication\upload_state.json'
$gh=(Get-Command gh.exe).Path
$manifest=Get-Content -LiteralPath (Join-Path $root 'PUBLICATION_MANIFEST.json') -Raw | ConvertFrom-Json
function Write-State($status,$name,$completed) { @{status=$status;asset=$name;completed_assets=$completed;total_assets=10;updated_China=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8 }
function Push-Main {
 & git -C $root -c credential.helper= -c 'credential.helper=!gh auth git-credential' push --set-upstream origin main
 if ($LASTEXITCODE -ne 0) { throw 'Git push failed; remote history was not force-overwritten.' }
}
& $gh auth status
if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI device authorization is required.' }
Push-Main
$commit=(& git -C $root rev-parse HEAD).Trim()
$releaseText=& $gh release view $Tag --repo $Repo --json isDraft,tagName,url 2>$null
if ($LASTEXITCODE -ne 0) {
 & $gh release create $Tag --repo $Repo --target $commit --title 'Member04 original YOLOv8n baseline 2026-11-05' --notes-file (Join-Path $root '.runtime\github_publication\release_notes.md') --draft
 if ($LASTEXITCODE -ne 0) { throw 'Draft release creation failed' }
}
$releaseListText=& $gh api "repos/$Repo/releases?per_page=100"
if ($LASTEXITCODE -ne 0) { throw 'Draft release lookup failed' }
$matches=@(($releaseListText | ConvertFrom-Json) | Where-Object { $_.tag_name -eq $Tag })
if ($matches.Count -ne 1) { throw 'Expected exactly one matching release' }
$releaseId=$matches[0].id
$list=@($manifest.image_assets)+@($manifest.handoff_asset)+@([pscustomobject]@{name='SHA256SUMS.txt';bytes=(Get-Item -LiteralPath (Join-Path $assets 'SHA256SUMS.txt')).Length;sha256=(Get-FileHash -LiteralPath (Join-Path $assets 'SHA256SUMS.txt') -Algorithm SHA256).Hash.ToLowerInvariant()})
$completed=0
foreach ($asset in $list) {
 $metadata=& $gh api "repos/$Repo/releases/$releaseId"
 if ($LASTEXITCODE -ne 0) { throw 'Release inspection failed' }
 $release=$metadata | ConvertFrom-Json
 $existing=@($release.assets | Where-Object { $_.name -eq $asset.name })
 if ($existing.Count -gt 0) {
   if ($existing.Count -ne 1 -or $existing[0].size -ne $asset.bytes -or ($existing[0].digest -and $existing[0].digest -ne ('sha256:'+$asset.sha256))) { throw "Existing asset differs; not replacing it: $($asset.name)" }
   Write-Output "VERIFIED EXISTING $($asset.name)"
 } else {
   $local=Join-Path $assets $asset.name
   if (-not (Test-Path -LiteralPath $local) -or (Get-Item -LiteralPath $local).Length -ne $asset.bytes) { throw "Prepared asset missing or wrong size: $local" }
   Write-State 'uploading' $asset.name $completed
   Write-Output "UPLOADING $($completed+1)/$($list.Count): $($asset.name) ($($asset.bytes) bytes)"
   & $gh release upload $Tag $local --repo $Repo
   if ($LASTEXITCODE -ne 0) { throw "Upload failed: $($asset.name)" }
 }
 $completed++;Write-State 'uploaded' $asset.name $completed
}
$metadata=& $gh api "repos/$Repo/releases/$releaseId"
if ($LASTEXITCODE -ne 0) { throw 'Final release inspection failed' }
$release=$metadata | ConvertFrom-Json
$verified=@()
foreach ($asset in $list) {
 $remote=@($release.assets | Where-Object { $_.name -eq $asset.name })
 if ($remote.Count -ne 1 -or $remote[0].size -ne $asset.bytes -or ($remote[0].digest -and $remote[0].digest -ne ('sha256:'+$asset.sha256))) { throw "Remote asset verification failed: $($asset.name)" }
 $verified+=@{name=$remote[0].name;bytes=$remote[0].size;expected_sha256=$asset.sha256;server_digest=$remote[0].digest;url=$remote[0].browser_download_url;id=$remote[0].id}
}
& $gh release edit $Tag --repo $Repo --draft=false
if ($LASTEXITCODE -ne 0) { throw 'Release publication failed' }
$receipt=@{status='published';repository="https://github.com/$Repo";release_url="https://github.com/$Repo/releases/tag/$Tag";release_id=$release.id;source_commit=$commit;verified_assets=$verified;image_count=1761;quarantined_images=48;test_used=$false;published_China=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $root 'reports\member04\GITHUB_PUBLICATION_RECEIPT.json') -Encoding utf8
$manifest.status='published';$manifest | Add-Member -NotePropertyName source_commit -NotePropertyValue $commit -Force
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $root 'PUBLICATION_MANIFEST.json') -Encoding utf8
$imageIndex=Get-Content -LiteralPath (Join-Path $root 'datasets\IMAGE_PACKAGES.json') -Raw | ConvertFrom-Json
$imageIndex.status='published';$imageIndex | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $root 'datasets\IMAGE_PACKAGES.json') -Encoding utf8
& git -C $root add -- PUBLICATION_MANIFEST.json datasets/IMAGE_PACKAGES.json reports/member04/GITHUB_PUBLICATION_RECEIPT.json
& git -C $root commit -m 'Record verified baseline release and image assets'
if ($LASTEXITCODE -ne 0) { throw 'Publication receipt commit failed' }
Push-Main
Write-State 'complete' '' $completed
Write-Output "PUBLISHED https://github.com/$Repo/releases/tag/$Tag"

