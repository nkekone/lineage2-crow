[CmdletBinding()]
param(
    [string]$SourceRoot,
    [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $SourceRoot) {
    $SourceRoot = Split-Path -Parent $PSScriptRoot
}
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $SourceRoot '_site'
}

function ConvertFrom-MarkdownCells {
    param([string]$Line)

    $trimmed = $Line.Trim()
    if (-not ($trimmed.StartsWith('|') -and $trimmed.EndsWith('|'))) {
        throw "Markdown table row must start and end with '|': $Line"
    }
    return ,@($trimmed.Trim('|').Split('|') | ForEach-Object { $_.Trim() })
}

function ConvertTo-HtmlText {
    param([string]$Text)
    return [System.Net.WebUtility]::HtmlEncode($Text)
}

$categoryDefinitions = @(
    [pscustomobject]@{ Key = 'ring'; Suffix = 'リング'; Label = 'リング'; Icon = '💍' }
    [pscustomobject]@{ Key = 'earring'; Suffix = 'イヤリング'; Label = 'イヤリング'; Icon = '🦻' }
    [pscustomobject]@{ Key = 'necklace'; Suffix = 'ネックレス'; Label = 'ネックレス'; Icon = '📿' }
)

$legacyIds = @{
    'クイーンアント リング' = 'acc-qa'
    'バイウム リング' = 'acc-baium'
    'コア リング' = 'acc-core'
    'アズタカン イヤリング' = 'acc-aztaqan'
    'アンタラス イヤリング' = 'acc-antharas'
    'オルフェン イヤリング' = 'acc-orfen'
    'ザケン イヤリング' = 'acc-zaken'
    'ベリオン ネックレス' = 'acc-belion'
    'フリンテッサ ネックレス' = 'acc-frintezza'
}

$markdownPath = Join-Path $SourceRoot 'rare-accessories.md'
$templatePath = Join-Path $SourceRoot 'index.html'
if (-not (Test-Path -LiteralPath $markdownPath -PathType Leaf)) {
    throw "Accessory source Markdown was not found: $markdownPath"
}
if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
    throw "HTML template was not found: $templatePath"
}

$markdownLines = [System.IO.File]::ReadAllText($markdownPath, [System.Text.Encoding]::UTF8) -split "`r?`n"
$entries = [System.Collections.Generic.List[object]]::new()

for ($lineIndex = 0; $lineIndex -lt $markdownLines.Length; $lineIndex++) {
    if ($markdownLines[$lineIndex] -notmatch '^##\s+(.+?)\s*$') {
        continue
    }

    $name = $Matches[1].Trim()
    $category = $categoryDefinitions |
        Where-Object { $name.EndsWith($_.Suffix, [System.StringComparison]::Ordinal) } |
        Sort-Object { $_.Suffix.Length } -Descending |
        Select-Object -First 1
    if (-not $category) {
        throw "Accessory heading must end with a supported category (リング, イヤリング, ネックレス): $name"
    }

    $tableLines = [System.Collections.Generic.List[string]]::new()
    for ($rowIndex = $lineIndex + 1; $rowIndex -lt $markdownLines.Length; $rowIndex++) {
        if ($markdownLines[$rowIndex] -match '^##\s+') {
            break
        }
        if ($markdownLines[$rowIndex].Trim().StartsWith('|')) {
            $tableLines.Add($markdownLines[$rowIndex])
        }
    }

    if ($tableLines.Count -lt 3) {
        throw "Accessory table is missing its header, separator, or data rows: $name"
    }
    $header = ConvertFrom-MarkdownCells $tableLines[0]
    if ($header.Count -ne 8 -or $header[0] -ne '項目' -or (($header[1..7] -join ',') -ne '0,1,2,3,4,5,6')) {
        throw "Accessory table must have columns 項目 and 0 through 6: $name"
    }
    $separator = ConvertFrom-MarkdownCells $tableLines[1]
    if ($separator.Count -ne 8 -or @($separator | Where-Object { $_ -notmatch '^:?-+:?$' }).Count -ne 0) {
        throw "Accessory table has an invalid separator row: $name"
    }

    $rows = [System.Collections.Generic.List[object]]::new()
    for ($tableRowIndex = 2; $tableRowIndex -lt $tableLines.Count; $tableRowIndex++) {
        $cells = ConvertFrom-MarkdownCells $tableLines[$tableRowIndex]
        if ($cells.Count -ne 8) {
            throw "Accessory data row must contain a label and seven enchant values: $name"
        }
        $rows.Add([pscustomobject]@{ Label = $cells[0]; Values = @($cells[1..7]) })
    }
    if ($rows.Count -eq 0) {
        throw "Accessory table has no data rows: $name"
    }
    if (@($entries | Where-Object { $_.Name -eq $name }).Count -gt 0) {
        throw "Duplicate accessory heading: $name"
    }

    if ($legacyIds.ContainsKey($name)) {
        $id = $legacyIds[$name]
    } else {
        $hexName = [System.BitConverter]::ToString([System.Text.Encoding]::UTF8.GetBytes($name)).Replace('-', '').ToLowerInvariant()
        $id = "acc-$hexName"
    }

    $entries.Add([pscustomobject]@{
        Name = $name
        Category = $category
        Id = $id
        Rows = @($rows)
    })
}

if ($entries.Count -eq 0) {
    throw 'No accessory sections were found in rare-accessories.md.'
}

$fragment = [System.Collections.Generic.List[string]]::new()
$fragment.Add('                    <!-- カテゴリー絞り込みボタン -->')
$fragment.Add('                    <div class="accessory-nav">')
$fragment.Add("                        <button type=`"button`" class=`"filter-btn is-active`" data-filter=`"all`">すべて ($($entries.Count))</button>")
foreach ($category in $categoryDefinitions) {
    $count = @($entries | Where-Object { $_.Category.Key -eq $category.Key }).Count
    if ($count -gt 0) {
        $fragment.Add("                        <button type=`"button`" class=`"filter-btn`" data-filter=`"$($category.Key)`">$($category.Icon) $($category.Label) ($count)</button>")
    }
}
$fragment.Add('                    </div>')
$fragment.Add('')
$fragment.Add('                    <!-- クイックジャンプリンク -->')
$fragment.Add('                    <div class="accessory-quick-jump">')
$fragment.Add('                        <span class="quick-jump-label">目次ジャンプ:</span>')
foreach ($entry in $entries) {
    $quickName = $entry.Name -replace '\s+(リング|イヤリング|ネックレス)$', ''
    $safeQuickName = ConvertTo-HtmlText $quickName
    $fragment.Add("                        <a href=`"#$($entry.Id)`" class=`"quick-jump-chip`">$safeQuickName</a>")
}
$fragment.Add('                    </div>')
$fragment.Add('')

foreach ($entry in $entries) {
    $safeName = ConvertTo-HtmlText $entry.Name
    $fragment.Add("                    <div id=`"$($entry.Id)`" class=`"accessory-item-card`" data-category=`"$($entry.Category.Key)`">")
    $fragment.Add('                        <div class="accessory-header">')
    $fragment.Add("                            <h2 class=`"accessory-name`">$safeName</h2>")
    $fragment.Add("                            <span class=`"accessory-badge badge-$($entry.Category.Key)`">$($entry.Category.Icon) $($entry.Category.Label)</span>")
    $fragment.Add('                        </div>')
    $fragment.Add('                        <div class="table-responsive">')
    $fragment.Add('                            <table class="accessory-table">')
    $fragment.Add('                                <thead>')
    $fragment.Add('                                    <tr>')
    $fragment.Add('                                        <th class="col-name">項目</th>')
    foreach ($level in 0..6) {
        $fragment.Add("                                        <th class=`"col-enchant`">+$level</th>")
    }
    $fragment.Add('                                    </tr>')
    $fragment.Add('                                </thead>')
    $fragment.Add('                                <tbody>')

    foreach ($row in $entry.Rows) {
        $safeLabel = ConvertTo-HtmlText $row.Label
        $fragment.Add('                                    <tr>')
        $fragment.Add("                                        <td class=`"cell-name`">$safeLabel</td>")
        foreach ($value in $row.Values) {
            if ([string]::IsNullOrWhiteSpace($value) -or $value -eq '-') {
                $fragment.Add('                                        <td class="cell-empty">-</td>')
            } else {
                $safeValue = ConvertTo-HtmlText $value
                if ($value.Length -gt 20) {
                    $fragment.Add("                                        <td class=`"cell-val`" style=`"font-size:0.8rem; white-space:normal;`">$safeValue</td>")
                } else {
                    $fragment.Add("                                        <td class=`"cell-val`">$safeValue</td>")
                }
            }
        }
        $fragment.Add('                                    </tr>')
    }

    $fragment.Add('                                </tbody>')
    $fragment.Add('                            </table>')
    $fragment.Add('                        </div>')
    $fragment.Add('                    </div>')
    $fragment.Add('')
}

$template = [System.IO.File]::ReadAllText($templatePath, [System.Text.Encoding]::UTF8)
$startMarker = '<!-- ACCESSORIES_GENERATED_START -->'
$endMarker = '<!-- ACCESSORIES_GENERATED_END -->'
$startIndex = $template.IndexOf($startMarker, [System.StringComparison]::Ordinal)
$endIndex = $template.IndexOf($endMarker, [System.StringComparison]::Ordinal)
if ($startIndex -lt 0 -or $endIndex -le $startIndex) {
    throw 'Could not find the accessory generation markers in index.html.'
}

$contentStart = $startIndex + $startMarker.Length
$generatedHtml = $template.Substring(0, $contentStart) + "`r`n" +
    ($fragment -join "`r`n") + "`r`n                    " +
    $template.Substring($endIndex)
if (($generatedHtml | Select-String -Pattern 'class="accessory-item-card"' -AllMatches).Matches.Count -ne $entries.Count) {
    throw 'Generated accessory card count does not match the Markdown sections.'
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputPath = Join-Path $OutputDirectory 'index.html'
[System.IO.File]::WriteAllText($outputPath, $generatedHtml, [System.Text.UTF8Encoding]::new($false))
Write-Host "Generated $outputPath with $($entries.Count) accessories."
