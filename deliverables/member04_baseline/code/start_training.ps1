param([string]$RunId=('yolov8n_newjson_from_official_'+[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyyMMdd_HHmmss')))
$ErrorActionPreference='Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
$env:PYTHONDONTWRITEBYTECODE='1';$env:PYTHONIOENCODING='utf-8';$env:PYTHONUNBUFFERED='1'
$Host.UI.RawUI.WindowTitle="IDAT7215 YOLOv8n 100 epochs | $RunId"
Set-Location -LiteralPath $projectRoot
Write-Host "Run: $RunId"
Write-Host 'Official COCO initialization; 100 full epochs; resume=False; fixed train/validation/test=1371/171/171.'
Write-Host "Live log: $projectRoot\baseline\runs\$RunId\training.log"
Write-Host 'Keep this window open. Epochs, losses, validation metrics and errors appear here and in the live log.'
& (Join-Path $projectRoot 'environment\.venv_gpu\Scripts\python.exe') -B -u (Join-Path $PSScriptRoot 'train_baseline.py') --run-id $RunId
$trainExit=$LASTEXITCODE
$exitRecord=@{run_id=$RunId;exit_code=$trainExit;terminal_pid=$PID;finished_China=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')}
$runDirectory=Join-Path $PSScriptRoot ('runs\'+$RunId)
if (Test-Path -LiteralPath $runDirectory) { $exitRecord | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDirectory 'terminal_exit.json') -Encoding utf8 }
if ($trainExit -eq 0) { Write-Host '100 epoch training finished. Independent validation and handoff packaging follow in Codex.' -ForegroundColor Green } else { Write-Host "Training exited with code $trainExit. See training.log and status.json." -ForegroundColor Red }
