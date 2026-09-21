$ErrorActionPreference = "Continue"
try {
    $w = New-Object -ComObject Word.Application
    $w.Visible = $false
    $src = "C:\Users\24974\AppData\Local\Temp\tech_plan_s5.pdf"
    $d = $w.Documents.Open($src, $false, $true)
    Start-Sleep -Seconds 3
    $pages = $d.ComputeStatistics(2)  # wdStatisticPages
    Write-Output ("PAGES: " + $pages)
    $d.Close($false)
    $w.Quit()
} catch {
    Write-Output ("ERR: " + $_.Exception.Message)
    try { $w.Quit() } catch {}
}