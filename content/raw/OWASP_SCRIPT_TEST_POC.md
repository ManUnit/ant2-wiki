



=====

PS C:\Users\anan> type .\owaps.ps1

=====================================================

OWASP CRS - 24 Rules Test + Summary Report

Usage: .\owaps.ps1 https://target.com

=====================================================

if ($args.Count -lt 1) {
    Write-Host "Usage: .\owaps.ps1 <TARGET_URL>" -ForegroundColor Yellow
    exit 1
}

$TargetUrl  = $args[0].TrimEnd("/")
$ReportFile = "owasp-crs-report.txt"
$Curl       = "$env:SystemRoot\System32\curl.exe"

if (-not (Test-Path $Curl)) {
    Write-Host "curl.exe not found" -ForegroundColor Red
    exit 1
}

-------------------------------

###### COUNTERS

# -------------------------------

$TotalTests = 0
$PassCount  = 0
$FailCount  = 0

# -------------------------------

TEST CASES (24 RULES)

# -------------------------------

$Tests = @(
    @{ Name='SQLi Basic';        Rule='942100'; Group='REQUEST-942'; Payload='?id=1'' OR ''1''=''1' }
    @{ Name='SQLi UNION';        Rule='942200'; Group='REQUEST-942'; Payload='?id=1 UNION SELECT 1,2,3' }
    @{ Name='SQLi Comment';      Rule='942110'; Group='REQUEST-942'; Payload='?id=1--' }
    @{ Name='SQLi Boolean';      Rule='942150'; Group='REQUEST-942'; Payload='?id=1 AND 1=1' }
    @{ Name='SQLi Time-based';   Rule='942390'; Group='REQUEST-942'; Payload='?id=1;WAITFOR DELAY ''0:0:5''' }

    @{ Name='XSS Script';        Rule='941100'; Group='REQUEST-941'; Payload='?q=`<script>`alert(1)`</script>`' }
    @{ Name='XSS IMG';           Rule='941130'; Group='REQUEST-941'; Payload='?q=<img src=x onerror=alert(1)>' }
    @{ Name='XSS SVG';           Rule='941160'; Group='REQUEST-941'; Payload='?q=<svg/onload=alert(1)>' }
    @{ Name='XSS JS URI';        Rule='941120'; Group='REQUEST-941'; Payload='?q=javascript:alert(1)' }
    @{ Name='XSS Encoded';       Rule='941180'; Group='REQUEST-941'; Payload='?q=%3Cscript%3Ealert(1)%3C/script%3E' }

    @{ Name='LFI passwd';        Rule='930100'; Group='REQUEST-930'; Payload='?file=../../../../etc/passwd' }
    @{ Name='LFI proc';          Rule='930110'; Group='REQUEST-930'; Payload='?file=../../../../proc/self/environ' }
    @{ Name='Traversal Windows'; Rule='930120'; Group='REQUEST-930'; Payload='?file=..\\..\\windows\\win.ini' }

    @{ Name='CMD Semicolon';     Rule='932100'; Group='REQUEST-932'; Payload='?cmd=;cat /etc/passwd' }
    @{ Name='CMD Pipe';          Rule='932110'; Group='REQUEST-932'; Payload='?cmd=|whoami' }
    @{ Name='CMD AND';           Rule='932105'; Group='REQUEST-932'; Payload='?cmd=&&whoami' }
    @{ Name='CMD Backticks';     Rule='932130'; Group='REQUEST-932'; Payload='?cmd=``whoami``' }

    @{ Name='File Upload PHP';   Rule='933110'; Group='REQUEST-933'; Payload='?file=shell.php' }
    @{ Name='Double Extension';  Rule='933120'; Group='REQUEST-933'; Payload='?file=shell.php.jpg' }

    @{ Name='Open Redirect';     Rule='921110'; Group='REQUEST-921'; Payload='?redirect=https://evil.com' }
    @{ Name='CRLF Injection';    Rule='921150'; Group='REQUEST-921'; Payload='?q=%0d%0aSet-Cookie:evil=1' }
    @{ Name='Host Header';       Rule='921160'; Group='REQUEST-921'; Payload=''; Header='Host: evil.com' }

    @{ Name='Shellshock';        Rule='932160'; Group='REQUEST-932'; Payload='?q=() { :; }; /bin/cat /etc/passwd' }
    @{ Name='NoSQL Injection';   Rule='942290'; Group='REQUEST-942'; Payload='?id[$ne]=1' }
    @{ Name='NoSQL$gt';           Rule='942290'; Group='REQUEST-942'; Payload='?id[$gt]=0' }
    @{ Name='NoSQL $regex';        Rule='942290'; Group='REQUEST-942'; Payload='?id[$regex]=.*' }
    @{ Name='NoSQL $where';        Rule='942290'; Group='REQUEST-942'; Payload='?id[$where]=this.password.length>0' }

)

# -------------------------------

# INIT REPORT

# -------------------------------

"OWASP CRS - 24 Rules Test Report" | Out-File $ReportFile
"Target: $TargetUrl" | Out-File $ReportFile -Append
"Date: $(Get-Date)" | Out-File $ReportFile -Append
"====================================================================" | Out-File $ReportFile -Append
"Test Name | Rule ID | Group | HTTP | Result" | Out-File $ReportFile -Append
"--------------------------------------------------------------------" | Out-File $ReportFile -Append

Write-Host "`nRunning OWASP CRS 24 Rules Tests..." -ForegroundColor Cyan Write-Host "Target: $TargetUrl`n"

# -------------------------------

# RUN TESTS

# -------------------------------

foreach ($Test in $Tests) {

    $TotalTests++$Url = "$TargetUrl$($Test.Payload)"

    $HeaderArgs = @()
    if ($Test.ContainsKey('Header')) {
        $HeaderArgs += '-H'$HeaderArgs += $Test.Header
    }

    try {$StatusCode = & $Curl -k -s -o NUL -w "%{http_code}" @HeaderArgs "$Url"
    } catch {
        $StatusCode = 'ERR'
    }

    if ($StatusCode -in @('403','406','000')) {
        $Result = 'PASS'
        $PassCount++
        $Color = 'Green'
    } else {
        $Result = 'NOT PASS'
        $FailCount++
        $Color = 'Red'
    }

    $Line = "{0} | {1} | {2} | {3} | {4}" -f `$Test.Name, $Test.Rule, $Test.Group, $StatusCode, $Result

    Write-Host$Line -ForegroundColor $Color
    $Line | Out-File $ReportFile -Append
}

# -------------------------------

# SUMMARY

# -------------------------------

$PassRate = [math]::Round(($PassCount / $TotalTests) * 100, 2)

$Summary = @"

###### SUMMARY RESULT

Total Tests : $TotalTests
PASS        : $PassCount
NOT PASS    : $FailCount
PASS RATE   : $PassRate %
=========================

"@

Write-Host $Summary -ForegroundColor Cyan
$Summary | Out-File $ReportFile -Append

Write-Host "Report saved to: $ReportFile" -ForegroundColor Cyan

PS C:\Users\anan> .\owaps.ps1 abpmart.com

Running OWASP CRS 24 Rules Tests...
Target: abpmart.com

SQLi Basic | 942100 | REQUEST-942 | 000 | PASS
SQLi UNION | 942200 | REQUEST-942 | 000 | PASS
SQLi Comment | 942110 | REQUEST-942 | 301 | NOT PASS
SQLi Boolean | 942150 | REQUEST-942 | 000 | PASS
SQLi Time-based | 942390 | REQUEST-942 | 000 | PASS
XSS Script | 941100 | REQUEST-941 | 403 | PASS
XSS IMG | 941130 | REQUEST-941 | 000 | PASS
XSS SVG | 941160 | REQUEST-941 | 301 | NOT PASS
XSS JS URI | 941120 | REQUEST-941 | 301 | NOT PASS
XSS Encoded | 941180 | REQUEST-941 | 403 | PASS
LFI passwd | 930100 | REQUEST-930 | 403 | PASS
LFI proc | 930110 | REQUEST-930 | 403 | PASS
Traversal Windows | 930120 | REQUEST-930 | 301 | NOT PASS
CMD Semicolon | 932100 | REQUEST-932 | 000 | PASS
CMD Pipe | 932110 | REQUEST-932 | 301 | NOT PASS
CMD AND | 932105 | REQUEST-932 | 301 | NOT PASS
CMD Backticks | 932130 | REQUEST-932 | 301 | NOT PASS
File Upload PHP | 933110 | REQUEST-933 | 301 | NOT PASS
Double Extension | 933120 | REQUEST-933 | 301 | NOT PASS
Open Redirect | 921110 | REQUEST-921 | 301 | NOT PASS
CRLF Injection | 921150 | REQUEST-921 | 301 | NOT PASS
Host Header | 921160 | REQUEST-921 | 409 | NOT PASS
Shellshock | 932160 | REQUEST-932 | 000 | PASS
NoSQL Injection | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $gt | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $regex | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $where | 942290 | REQUEST-942 |  | NOT PASS

**SUMMARY RESULT**

Total Tests : 27
PASS        : 11
NOT PASS    : 16
PASS RATE   : 40.74 %

Report saved to: owasp-crs-report.txt
PS C:\Users\anan> .\owaps.ps1  kasikornbank.com

Running OWASP CRS 24 Rules Tests...
Target: kasikornbank.com

SQLi Basic | 942100 | REQUEST-942 | 000 | PASS
SQLi UNION | 942200 | REQUEST-942 | 000 | PASS
SQLi Comment | 942110 | REQUEST-942 | 000 | PASS
SQLi Boolean | 942150 | REQUEST-942 | 000 | PASS
SQLi Time-based | 942390 | REQUEST-942 | 000 | PASS
XSS Script | 941100 | REQUEST-941 | 000 | PASS
XSS IMG | 941130 | REQUEST-941 | 000 | PASS
XSS SVG | 941160 | REQUEST-941 | 000 | PASS
XSS JS URI | 941120 | REQUEST-941 | 000 | PASS
XSS Encoded | 941180 | REQUEST-941 | 000 | PASS
LFI passwd | 930100 | REQUEST-930 | 000 | PASS
LFI proc | 930110 | REQUEST-930 | 000 | PASS
Traversal Windows | 930120 | REQUEST-930 | 000 | PASS
CMD Semicolon | 932100 | REQUEST-932 | 000 | PASS
CMD Pipe | 932110 | REQUEST-932 | 000 | PASS
CMD AND | 932105 | REQUEST-932 | 000 | PASS
CMD Backticks | 932130 | REQUEST-932 | 000 | PASS
File Upload PHP | 933110 | REQUEST-933 | 000 | PASS
Double Extension | 933120 | REQUEST-933 | 000 | PASS
Open Redirect | 921110 | REQUEST-921 | 000 | PASS
CRLF Injection | 921150 | REQUEST-921 | 000 | PASS
Host Header | 921160 | REQUEST-921 | 000 | PASS
Shellshock | 932160 | REQUEST-932 | 000 | PASS
NoSQL Injection | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $gt | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $regex | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $where | 942290 | REQUEST-942 |  | NOT PASS

SUMMARY RESULT

##### Total Tests : 27
PASS        : 23
NOT PASS    : 4
PASS RATE   : 85.19 %

Report saved to: owasp-crs-report.txt
PS C:\Users\anan>
PS C:\Users\anan>



PS C:\Users\anan> .\owaps.ps1 abpmart.com

Running OWASP CRS 24 Rules Tests...
Target: abpmart.com

SQLi Basic | 942100 | REQUEST-942 | 000 | PASS
SQLi UNION | 942200 | REQUEST-942 | 000 | PASS
SQLi Comment | 942110 | REQUEST-942 | 301 | NOT PASS
SQLi Boolean | 942150 | REQUEST-942 | 000 | PASS
SQLi Time-based | 942390 | REQUEST-942 | 000 | PASS
XSS Script | 941100 | REQUEST-941 | 403 | PASS
XSS IMG | 941130 | REQUEST-941 | 000 | PASS
XSS SVG | 941160 | REQUEST-941 | 301 | NOT PASS
XSS JS URI | 941120 | REQUEST-941 | 301 | NOT PASS
XSS Encoded | 941180 | REQUEST-941 | 403 | PASS
LFI passwd | 930100 | REQUEST-930 | 403 | PASS
LFI proc | 930110 | REQUEST-930 | 403 | PASS
Traversal Windows | 930120 | REQUEST-930 | 301 | NOT PASS
CMD Semicolon | 932100 | REQUEST-932 | 000 | PASS
CMD Pipe | 932110 | REQUEST-932 | 301 | NOT PASS
CMD AND | 932105 | REQUEST-932 | 301 | NOT PASS
CMD Backticks | 932130 | REQUEST-932 | 301 | NOT PASS
File Upload PHP | 933110 | REQUEST-933 | 301 | NOT PASS
Double Extension | 933120 | REQUEST-933 | 301 | NOT PASS
Open Redirect | 921110 | REQUEST-921 | 301 | NOT PASS
CRLF Injection | 921150 | REQUEST-921 | 301 | NOT PASS
Host Header | 921160 | REQUEST-921 | 409 | NOT PASS
Shellshock | 932160 | REQUEST-932 | 000 | PASS
NoSQL Injection | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $gt | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $regex | 942290 | REQUEST-942 |  | NOT PASS
NoSQL $where | 942290 | REQUEST-942 |  | NOT PASS

###### SUMMARY RESULT

Total Tests : 27
PASS        : 11
NOT PASS    : 16
PASS RATE   : 40.74 %
