# REBUILD FORÇADO - Limpa TUDO e reconstrói

Write-Host "=" -ForegroundColor Red
Write-Host "REBUILD FORÇADO - DELETANDO TUDO" -ForegroundColor Red
Write-Host "=" -ForegroundColor Red

# 1. Parar containers
Write-Host "`n1. Parando containers..." -ForegroundColor Yellow
docker stop $(docker ps -aq) 2>$null

# 2. Remover imagem antiga
Write-Host "`n2. Removendo imagem antiga..." -ForegroundColor Yellow
docker rmi avantis-bot -f 2>$null

# 3. Limpar cache do Docker
Write-Host "`n3. Limpando cache do Docker..." -ForegroundColor Yellow
docker builder prune -f

# 4. Build SEM cache
Write-Host "`n4. Reconstruindo SEM cache..." -ForegroundColor Cyan
docker build --no-cache -t avantis-bot .

Write-Host "`n=" -ForegroundColor Green
Write-Host "PRONTO!" -ForegroundColor Green
Write-Host "=" -ForegroundColor Green

Write-Host "`nExecute agora:" -ForegroundColor White
Write-Host 'docker run --rm -it -v "${PWD}:/app" avantis-bot' -ForegroundColor Yellow
