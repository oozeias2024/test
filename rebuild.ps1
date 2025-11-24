# Script PowerShell para rebuild completo do Docker

Write-Host "🧹 Limpando imagens Docker antigas..." -ForegroundColor Yellow
docker rmi avantis-bot 2>$null

Write-Host "🔨 Construindo nova imagem..." -ForegroundColor Cyan
docker build -t avantis-bot .

Write-Host ""
Write-Host "✅ Pronto! Execute com:" -ForegroundColor Green
Write-Host 'docker run --rm -it -v "${PWD}:/app" avantis-bot' -ForegroundColor White
