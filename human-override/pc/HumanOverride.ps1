# Human Override for Windows - the AI kill switch
# Copyright (c) 2026 Amghar Said. All rights reserved.
# Blocks AI services for every browser and app on this PC by adding them to the Windows hosts file.
# Only needs administrator rights. Sends nothing about you anywhere; it only downloads the public list.
$ErrorActionPreference = 'Stop'
$Hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
$Start = '# >>> Human Override (do not edit this block)'
$End   = '# <<< Human Override'
$ListUrl = 'https://geopolcoins.xyz/human-override/hosts.txt'

function Test-Admin { ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }
if (-not (Test-Admin)) {
  Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
  exit
}

function Remove-Block([string]$text) {
  $pattern = [regex]::Escape($Start) + '[\s\S]*?' + [regex]::Escape($End) + '\r?\n?'
  return [regex]::Replace($text, $pattern, '')
}

function Get-List {
  try {
    $raw = (Invoke-WebRequest -Uri $ListUrl -UseBasicParsing -TimeoutSec 20).Content
  } catch {
    $local = Join-Path $PSScriptRoot 'hosts.txt'
    if (Test-Path $local) { $raw = Get-Content $local -Raw } else { throw 'Could not download the list and no local hosts.txt found.' }
  }
  # accept only safe lines: "0.0.0.0 domain"
  $lines = $raw -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^0\.0\.0\.0 ([a-z0-9-]{1,63}\.)+[a-z]{2,24}$' }
  if ($lines.Count -lt 20) { throw 'The downloaded list looks wrong. Nothing was changed.' }
  return $lines
}

Clear-Host
Write-Host ''
Write-Host '  HUMAN OVERRIDE  -  the AI kill switch' -ForegroundColor Red
Write-Host '  (c) 2026 Amghar Said  ·  geopolcoins.xyz/human-override.html'
Write-Host ''
Write-Host '  1) Block AI on this PC (or update the list)'
Write-Host '  2) Allow AI again (remove the block)'
Write-Host '  3) Quit'
$c = Read-Host '  Choose 1, 2 or 3'
$current = Get-Content $Hosts -Raw -ErrorAction SilentlyContinue
if ($null -eq $current) { $current = '' }
if ($c -eq '1') {
  $lines = Get-List
  Copy-Item $Hosts "$Hosts.human-override-backup" -Force
  $clean = (Remove-Block $current).TrimEnd()
  $block = @($Start) + $lines + @($End)
  Set-Content -Path $Hosts -Value ($clean + "`r`n`r`n" + ($block -join "`r`n") + "`r`n") -Encoding ASCII
  ipconfig /flushdns | Out-Null
  Write-Host ''
  Write-Host ("  Done: {0} AI addresses are blocked on this PC. Restart your browser." -f $lines.Count) -ForegroundColor Green
  Write-Host '  Tip: give children a normal (non-admin) Windows account, then they cannot undo it.'
} elseif ($c -eq '2') {
  Set-Content -Path $Hosts -Value ((Remove-Block $current).TrimEnd() + "`r`n") -Encoding ASCII
  ipconfig /flushdns | Out-Null
  Write-Host ''
  Write-Host '  AI is allowed again on this PC.' -ForegroundColor Yellow
}
Write-Host ''
Read-Host '  Press Enter to close'
