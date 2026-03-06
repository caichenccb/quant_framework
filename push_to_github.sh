#!/bin/bash

# 创建GitHub仓库
curl -X POST \
  -H "Authorization: token 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" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"quant_framework","description":"量化回测框架","private":false}'

# 推送代码到GitHub
git push -u origin main
