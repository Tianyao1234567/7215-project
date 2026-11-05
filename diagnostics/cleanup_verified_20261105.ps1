$ErrorActionPreference='Stop'
$rootPath=(Resolve-Path -LiteralPath 'D:\Desktop\7215\project').Path.TrimEnd('\')
$rootPrefix=$rootPath+'\'
$reportPath=Join-Path $rootPath 'reports\new_json_20261105\cleanup_record.json'
$proof=Get-Content -LiteralPath (Join-Path $rootPath 'reports\new_json_20261105\precleanup_proof.json') -Raw | ConvertFrom-Json
if ($proof.status -ne 'passed') { throw 'Preservation proof missing' }
$candidatePaths=@('yolo','datasets\received_20261102','datasets\real_smoke_20261102','datasets\repartition_draft_20261102','datasets\resource_smoke_20261105','sources\member_02\yolo_dataset','new\dataset-20261105T105219Z-1-001.zip','new\dataset-20261105T105219Z-1-002.zip','new\dataset-20261105T105219Z-1-003.zip','new\dataset-20261105T105219Z-1-004.zip')
$plan=@()
foreach ($rel in $candidatePaths) {
 $target=[System.IO.Path]::GetFullPath((Join-Path $rootPath $rel))
 if (-not $target.StartsWith($rootPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Target outside project: $target" }
 if (-not (Test-Path -LiteralPath $target)) { continue }
 $node=Get-Item -LiteralPath $target -Force
 $chain=if ($node.PSIsContainer) { $node } else { $node.Directory }
 while ($chain.FullName -ne $rootPath) { if (($chain.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse ancestor: $($chain.FullName)" }; $chain=$chain.Parent; if ($null -eq $chain) { throw 'Unexpected path ancestry' } }
 if (($node.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse target: $target" }
 $desc=if ($node.PSIsContainer) { @(Get-ChildItem -LiteralPath $target -Recurse -Force) } else { @($node) }
 if (@($desc | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }).Count -gt 0) { throw "Reparse child in $target" }
 $files=@($desc | Where-Object { -not $_.PSIsContainer })
 $sum=($files | Measure-Object -Property Length -Sum).Sum
 $plan += [pscustomobject]@{path=$target;bytes=[long]$sum;files=$files.Count;status='planned';reason='Superseded data or source ZIP; current JSON-derived split, all original train JSON, quarantine and source evidence verified and preserved.'}
}
$diskBefore=(Get-PSDrive -Name D).Free
$record=[ordered]@{started_China=(Get-Date).ToString('o');status='planned';root=$rootPath;free_bytes_before=$diskBefore;preserved=@('datasets/current','datasets/annotation_source','datasets/quarantine','baseline','environment','sources/member_02/reference_models','sources/shared','reports/new_json_20261105/source_evidence','C drive historical source unchanged');items=$plan}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding utf8
foreach ($entry in $plan) {
 $resolved=(Resolve-Path -LiteralPath $entry.path).Path
 if (-not $resolved.StartsWith($rootPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Resolved path outside project: $resolved" }
 if ((Get-Item -LiteralPath $resolved -Force).PSIsContainer) { Remove-Item -LiteralPath $resolved -Recurse -Force } else { Remove-Item -LiteralPath $resolved -Force }
 if (Test-Path -LiteralPath $resolved) { throw "Deletion incomplete: $resolved" }
 $entry.status='deleted'
 $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding utf8
 Write-Output "DELETED $resolved ($($entry.bytes) logical bytes)"
}
$record.status='completed';$record.completed_China=(Get-Date).ToString('o');$record.free_bytes_after=(Get-PSDrive -Name D).Free
$record.observed_free_bytes_increase=$record.free_bytes_after-$diskBefore
$record.deleted_logical_bytes=($plan | Measure-Object -Property bytes -Sum).Sum
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding utf8
Write-Output "Observed disk free increase: $($record.observed_free_bytes_increase) bytes"
