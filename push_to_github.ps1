# 创建GitHub仓库
$headers = @{
    "Authorization" = "token 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"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = "quant_framework"
    description = "量化回测框架"
    private = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method POST -Headers $headers -Body $body

# 推送代码到GitHub
git push -u origin main
