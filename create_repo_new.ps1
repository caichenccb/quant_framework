$headers = @{
    "Authorization" = "token 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"
    "Accept" = "application/vnd.github.v3+json"
}

$body = '{"name":"quant_framework","description":"量化回测框架","private":false}'

Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method POST -Headers $headers -Body $body
