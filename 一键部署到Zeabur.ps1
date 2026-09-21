# ============================================================
# MindGuard 一键部署 GitHub + Zeabur 脚本
# 用法：右键 → 以管理员身份运行 PowerShell → 执行
# 或直接双击（可能需要先解除 Windows 执行策略限制）
# ============================================================

$ErrorActionPreference = "Continue"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

Write-Host ""
Write-Host "========================================"
Write-Host "  MindGuard → GitHub → Zeabur 一键部署"
Write-Host "========================================"
Write-Host ""
Write-Host "项目目录: $ProjectDir"
Write-Host ""

# ── 步骤 1：安装 Git ────────────────────────────────────────
function Install-Git {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "[1/5] Git 已安装: $(git --version)"
        return
    }
    Write-Host "[1/5] 安装 Git for Windows..."
    try {
        winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    } catch {
        Write-Host "  winget 失败，尝试直接下载..."
        $zip = "$env:TEMP\git-portable.zip"
        $dest = "$env:TEMP\git-portable"
        Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/MinGit-2.47.1-64-bit.zip" -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath $dest -Force
        $env:PATH = "$dest\cmd;$env:PATH"
        [Environment]::SetEnvironmentVariable("PATH", "$dest\cmd;" + [Environment]::GetEnvironmentVariable("PATH", "User"), "User")
    }
    # 重新加载 PATH
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
    Write-Host "  ✅ Git: $(git --version)"
}

Install-Git

# ── 步骤 2：配置 Git 用户（首次） ────────────────────────────
$gitUser = git config --global user.name 2>$null
if (-not $gitUser) {
    $userName = Read-Host "请输入你的 GitHub 用户名（用于 git commit）"
    git config --global user.name $userName
    $userEmail = Read-Host "请输入你的 GitHub 邮箱"
    git config --global user.email $userEmail
    Write-Host "  ✅ 已配置 git user.name / user.email"
} else {
    Write-Host "[2/5] Git 用户已配置: $gitUser"
}

# ── 步骤 3：Git init + commit ────────────────────────────────
Write-Host "[3/5] 初始化仓库并提交..."

if (-not (Test-Path ".git")) {
    git init -b main
}

# 确保关键配置文件存在
$needFiles = @("Procfile", "runtime.txt", "requirements.txt", ".gitignore")
foreach ($f in $needFiles) {
    if (Test-Path $f) { Write-Host "  ✅ $f 存在" } else { Write-Host "  ❌ $f 缺失！" }
}

git add -A
git status
Write-Host ""
Write-Host "检查要提交的文件列表（如果看到 mmhs.db / .env / dist 是正常的——.gitignore 应该过滤掉了）"

Write-Host ""
$commitMsg = Read-Host "输入 commit message（回车用默认 'MindGuard v2.0 - 完整系统 + Zeabur 部署配置'）"
if (-not $commitMsg) { $commitMsg = "MindGuard v2.0 - 完整系统 + Zeabur 部署配置" }

git commit -m $commitMsg

# ── 步骤 4：连接 GitHub repo ────────────────────────────────
Write-Host ""
Write-Host "[4/5] 准备推送到 GitHub..."
Write-Host ""
Write-Host "👉 请先去 https://github.com/new 创建一个新仓库"
Write-Host "   Repository name: mindguard （或你喜欢的名字）"
Write-Host "   ❌ 不要勾选 'Initialize this repository with a README'"
Write-Host "   点击 Create repository"
Write-Host ""

$githubUrl = Read-Host "然后粘贴仓库地址（例如 https://github.com/你的用户名/mindguard.git）"

git remote remove origin 2>$null
git remote add origin $githubUrl

Write-Host ""
Write-Host "推送中..."
try {
    git push -u origin main
    Write-Host "  ✅ 推送成功！"
} catch {
    Write-Host "  ❌ 推送失败。可能需要先登录 GitHub。"
    Write-Host "     建议在浏览器打开 https://github.com/你的用户名/mindguard 确认仓库存在。"
    Write-Host "     如果弹出登录，请用你的 GitHub 账号授权。"
    Write-Host "     然后重新运行: git push -u origin main"
    exit 1
}

# ── 步骤 5：Zeabur 部署指引 ───────────────────────────────────
Write-Host ""
Write-Host "========================================"
Write-Host "  ✅ Git 推送完成！"
Write-Host "========================================"
Write-Host ""
Write-Host "[5/5] Zeabur 部署（Web UI 操作，3 分钟）"
Write-Host ""
Write-Host "  ① 打开 https://zeabur.com ，用 GitHub 账号登录"
Write-Host "  ② 点击「新建项目」→「从 GitHub 导入」"
Write-Host "  ③ 选择刚才的 mindguard 仓库 → 导入"
Write-Host "  ④ 环境变量设置："
Write-Host "     DB_PATH = /data/mmhs.db"
Write-Host "     ADMIN_USERNAME = admin"
Write-Host "     ADMIN_PASSWORD = admin123"
Write-Host "  ⑤ 添加持久化存储："
Write-Host "     项目设置 → 服务 → 添加挂载目录 → /data"
Write-Host "  ⑥ 点击「部署」，等待 2-3 分钟"
Write-Host ""
Write-Host "  部署成功后会自动分配一个 HTTPS 域名！"
Write-Host "  例如：https://mindguard-xxxx.zeabur.app"
Write-Host ""
Write-Host "  打开就能用了 🎉"
Write-Host ""
Write-Host "  如需 CLI 一键部署（备选）："
Write-Host "    npm install -g @zeabur/cli"
Write-Host "    zeabur login"
Write-Host "    zeabur deploy"
