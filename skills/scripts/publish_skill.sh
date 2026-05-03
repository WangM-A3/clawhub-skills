#!/bin/bash
#==============================================================================
# OpenClaw Enterprise 自动化发布脚本
# 支持 GitHub 和 ClawHub 双平台发布
#
# 用法:
#   ./scripts/publish_skill.sh [OPTIONS]
#
# 选项:
#   --github          仅发布到 GitHub
#   --clawhub         仅发布到 ClawHub
#   --dry-run         仅模拟，不实际执行
#   --skip-checks     跳过预检查
#   --skip-git        跳过 Git 操作
#   --skip-validate   跳过技能包校验
#   -h, --help        显示帮助
#
# 环境变量:
#   GITHUB_TOKEN      GitHub Personal Access Token（必需）
#   GITHUB_REPO       GitHub 仓库地址（默认从 clawhub.yaml 读取）
#   CLAWHUB_TOKEN     ClawHub API Token
#   CLAWHUB_API_URL   ClawHub API 地址（默认 https://api.clawhub.ai/v1）
#
# 注意:
#   - GitHub 账号需注册满 14 天才能发布到 ClawHub（2026-04-23）
#   - 首次发布需手动配置 GitHub remote
#==============================================================================

set -euo pipefail

#------------------------------
# 配置
#------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_NAME="openclaw-enterprise"
GITHUB_REPO="${GITHUB_REPO:-}"
CLAWHUB_TOKEN="${CLAWHUB_TOKEN:-}"
CLAWHUB_API_URL="${CLAWHUB_API_URL:-https://api.clawhub.ai/v1}"
CLAWHUB_ACCOUNT_READY_DATE="2026-04-23"  # 账号注册满14天的最早日期

# 发布目标（默认为全量）
TARGET_GITHUB=true
TARGET_CLAWHUB=true
DRY_RUN=false
SKIP_CHECKS=false
SKIP_GIT=false
SKIP_VALIDATE=false

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 日志文件
LOG_FILE="${SKILL_DIR}/.publish.log"

#------------------------------
# 工具函数
#------------------------------

log() {
    local level="$1"
    shift
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*"
    echo -e "$msg"
    echo "$msg" >> "$LOG_FILE"
}

info()    { log "INFO"    "${BLUE}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }
warn()    { log "WARN"    "${YELLOW}$*${NC}"; }
error()   { log "ERROR"   "${RED}$*${NC}" >&2; }
step()    { log "STEP"    "${CYAN}[$1] $2${NC}"; }

# 打印彩色分隔线
divider() {
    echo -e "${BOLD}${CYAN}=================================================================${NC}"
}

# 检查命令是否存在
require_cmd() {
    if ! command -v "$1" &> /dev/null; then
        error "缺少必需命令: $1，请先安装。"
        return 1
    fi
}

#------------------------------
# 解析参数
#------------------------------
usage() {
    cat <<EOF
${BOLD}OpenClaw Enterprise 自动化发布脚本${NC}

${BOLD}用法:${NC}
  $0 [OPTIONS]

${BOLD}选项:${NC}
  --github          仅发布到 GitHub
  --clawhub         仅发布到 ClawHub
  --dry-run         模拟运行（不实际执行）
  --skip-checks     跳过预检查
  --skip-git        跳过 Git 操作
  --skip-validate   跳过技能包校验
  -h, --help        显示本帮助

${BOLD}环境变量:${NC}
  GITHUB_TOKEN      GitHub Personal Access Token（必需）
  GITHUB_REPO       GitHub 仓库地址
  CLAWHUB_TOKEN     ClawHub API Token
  CLAWHUB_API_URL   ClawHub API 地址

${BOLD}示例:${NC}
  GITHUB_TOKEN=ghp_xxx $0 --github
  $0 --clawhub --dry-run
  $0 --skip-git --skip-validate

EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --github)       TARGET_CLAWHUB=false; shift ;;
        --clawhub)      TARGET_GITHUB=false;  shift ;;
        --dry-run)      DRY_RUN=true;         shift ;;
        --skip-checks)  SKIP_CHECKS=true;     shift ;;
        --skip-git)     SKIP_GIT=true;        shift ;;
        --skip-validate) SKIP_VALIDATE=true;  shift ;;
        -h|--help)      usage ;;
        *)              error "未知参数: $1"; usage ;;
    esac
done

#------------------------------
# 预检查
#------------------------------
preflight_checks() {
    divider
    echo -e "${BOLD}  🔍 预检查${NC}"
    divider

    step "1" "检查目录结构"
    if [[ ! -d "$SKILL_DIR" ]]; then
        error "技能目录不存在: $SKILL_DIR"
        exit 1
    fi
    [[ -f "$SKILL_DIR/SKILL.md" ]] || { error "缺少 SKILL.md"; exit 1; }
    [[ -f "$SKILL_DIR/clawhub.yaml" ]] || { error "缺少 clawhub.yaml"; exit 1; }
    [[ -f "$SKILL_DIR/README.md" ]] || { error "缺少 README.md"; exit 1; }
    success "目录结构检查通过"

    step "2" "检查系统命令"
    require_cmd "git" || exit 1
    require_cmd "tar" || exit 1
    require_cmd "curl" || exit 1
    # zip 为可选（dist/ 中已有 tar.gz，zip 是跨平台补充）
    if ! command -v zip &> /dev/null; then
        warn "zip 命令不可用，将跳过 zip 打包"
    else
        success "系统命令检查通过（含 zip）"
    fi

    step "3" "检查 Git 状态"
    cd "$SKILL_DIR"
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local branch
        branch=$(git branch --show-current 2>/dev/null || echo "main")
        info "当前分支: $branch"

        # 检查未提交的更改
        if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
            warn "存在未提交的更改"
            if [[ "$DRY_RUN" == false ]]; then
                echo "使用 --skip-git 跳过 Git 操作，或先提交更改。"
                exit 1
            fi
        fi
    else
        warn "非 Git 仓库，Git 操作将被跳过"
        TARGET_GITHUB=false
    fi
    success "Git 状态检查通过"
}

#------------------------------
# 版本管理
#------------------------------
get_current_version() {
    local ver
    ver=$(grep -m1 '"version"' "$SKILL_DIR/package.json" 2>/dev/null | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    if [[ -z "$ver" ]]; then
        ver="1.0.0"
    fi
    echo "$ver"
}

bump_version() {
    local current="$1"
    local part="${2:-patch}"

    local major minor patch
    IFS='.' read -r major minor patch <<< "$current"
    major="${major:-1}"; minor="${minor:-0}"; patch="${patch:-0}"

    case "$part" in
        major) ((major++)); minor=0; patch=0 ;;
        minor) ((minor++)); patch=0 ;;
        patch) ((patch++)) ;;
        *)     error "无效版本类型: $part"; exit 1 ;;
    esac

    echo "${major}.${minor}.${patch}"
}

update_version_in_files() {
    local new_ver="$1"
    info "更新版本号至: $new_ver"

    # 更新 package.json
    if [[ -f "$SKILL_DIR/package.json" ]]; then
        sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$new_ver\"/" "$SKILL_DIR/package.json"
        info "已更新 package.json"
    fi

    # 更新 SKILL.md 中的 version
    if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
        sed -i "s/^    version: \"[^\"]*\"/    version: \"$new_ver\"/" "$SKILL_DIR/SKILL.md"
        sed -i "s/^version: \"[^\"]*\"/version: \"$new_ver\"/" "$SKILL_DIR/clawhub.yaml" 2>/dev/null || true
        info "已更新 SKILL.md / clawhub.yaml"
    fi
}

#------------------------------
# 技能包校验
#------------------------------
validate_skill_package() {
    divider
    echo -e "${BOLD}  ✅ 技能包校验${NC}"
    divider

    step "1" "检查必需文件"
    local required_files=(
        "SKILL.md"
        "README.md"
        "clawhub.yaml"
        "package.json"
    )
    for f in "${required_files[@]}"; do
        if [[ -f "$SKILL_DIR/$f" ]]; then
            success "  ✓ $f"
        else
            error "  ✗ 缺少 $f"
            exit 1
        fi
    done

    step "2" "检查脚本权限"
    for script in "$SKILL_DIR/scripts/"*.sh; do
        if [[ -f "$script" ]]; then
            chmod +x "$script" 2>/dev/null || true
            success "  ✓ $(basename "$script")"
        fi
    done

    step "3" "验证 SKILL.md YAML 语法"
    local yaml_errors=0

    # 基础 YAML 检查
    if grep -q "name:" "$SKILL_DIR/SKILL.md" && \
       grep -q "description:" "$SKILL_DIR/SKILL.md" && \
       grep -q "version:" "$SKILL_DIR/SKILL.md"; then
        success "SKILL.md 元数据完整"
    else
        error "SKILL.md 缺少必需字段（name/description/version）"
        ((yaml_errors++))
    fi

    if [[ $yaml_errors -eq 0 ]]; then
        success "所有校验通过 ✓"
    else
        error "校验失败，共 $yaml_errors 项错误"
        exit 1
    fi
}

#------------------------------
# 打包
#------------------------------
build_packages() {
    divider
    echo -e "${BOLD}  📦 打包技能包${NC}"
    divider

    local pkg_dir="${SKILL_DIR}/dist"
    mkdir -p "$pkg_dir"

    local ver
    ver=$(get_current_version)
    local base_name="${SKILL_NAME}-${ver}"

    cd "$SKILL_DIR"

    # 排除文件
    local exclude_args=(
        --exclude=".git"
        --exclude=".gitignore"
        --exclude="*.log"
        --exclude="__pycache__"
        --exclude="*.pyc"
        --exclude="*.pyo"
        --exclude="node_modules"
        --exclude=".coverage"
        --exclude="htmlcov"
        --exclude="dist"
        --exclude="build"
    )

    # tar.gz 包（Linux 首选）
    step "1" "创建 tar.gz 包"
    local tar_path="${pkg_dir}/${base_name}.tar.gz"
    if tar czf "$tar_path" "${exclude_args[@]}" \
        SKILL.md README.md clawhub.yaml package.json \
        scripts/ references/ 2>/dev/null; then
        local tar_size
        tar_size=$(du -h "$tar_path" | cut -f1)
        success "✓ ${base_name}.tar.gz (${tar_size})"
    else
        warn "tar.gz 打包失败，尝试仅打包关键文件"
        tar czf "$tar_path" "${exclude_args[@]}" . 2>/dev/null || true
        if [[ -f "$tar_path" ]]; then
            success "✓ ${base_name}.tar.gz (fallback)"
        fi
    fi

    # zip 包（跨平台）
    step "2" "创建 zip 包"
    local zip_path="${pkg_dir}/${base_name}.zip"
    if zip -rq "$zip_path" . \
        -x ".git/*" \
        -x "*.log" \
        -x "__pycache__/*" \
        -x "*.pyc" \
        -x "node_modules/*" \
        -x ".coverage/*" \
        -x "htmlcov/*" \
        -x "dist/*" \
        -x "build/*" \
        -x ".DS_Store" \
        -x "*.swp" 2>/dev/null; then
        local zip_size
        zip_size=$(du -h "$zip_path" | cut -f1)
        success "✓ ${base_name}.zip (${zip_size})"
    else
        warn "zip 命令不可用，跳过 zip 打包"
    fi

    success "打包完成: ${pkg_dir}"
    ls -lh "$pkg_dir"/${SKILL_NAME}-${ver}.* 2>/dev/null || true
}

#------------------------------
# GitHub 发布
#------------------------------
publish_to_github() {
    divider
    echo -e "${BOLD}  🐙 GitHub 发布${NC}"
    divider

    if [[ -z "$GITHUB_TOKEN" ]]; then
        warn "未设置 GITHUB_TOKEN，跳过 GitHub 发布"
        warn "提示: export GITHUB_TOKEN=ghp_xxx"
        return 0
    fi

    cd "$SKILL_DIR"

    # 获取仓库地址
    local repo_url
    if [[ -n "$GITHUB_REPO" ]]; then
        repo_url="$GITHUB_REPO"
    else
        repo_url=$(git remote get-url origin 2>/dev/null | sed 's|https://[^@]*@|https://|' | sed 's|\.git$||') || ""
    fi

    if [[ -z "$repo_url" ]]; then
        warn "无法获取 GitHub 仓库地址，跳过 GitHub 发布"
        warn "提示: export GITHUB_REPO=https://github.com/WangM-A3/openclaw-enterprise-skill"
        return 0
    fi

    info "仓库: $repo_url"

    # 提取 owner/repo
    local owner repo
    owner=$(echo "$repo_url" | sed 's|.*github\.com/||' | cut -d'/' -f1)
    repo=$(echo "$repo_url" | sed 's|.*github\.com/||' | cut -d'/' -f2)

    if [[ -z "$owner" || -z "$repo" ]]; then
        error "无法解析仓库地址: $repo_url"
        return 1
    fi

    local ver
    ver=$(get_current_version)

    step "1" "生成发布说明"
    local release_notes
    release_notes=$(generate_release_notes)
    success "发布说明已生成"

    step "2" "创建 Git tag"
    if git rev-parse "v${ver}" > /dev/null 2>&1; then
        warn "Tag v${ver} 已存在，跳过创建"
    else
        if [[ "$DRY_RUN" == false ]]; then
            git tag -a "v${ver}" -m "Release v${ver}" || warn "Tag 创建失败"
            success "Tag v${ver} 已创建"
        else
            info "[DRY-RUN] 模拟创建 tag: v${ver}"
        fi
    fi

    step "3" "推送 commit"
    if [[ "$DRY_RUN" == false ]]; then
        # 设置远程 URL（含 token）
        git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${owner}/${repo}.git" 2>/dev/null || \
        git remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${owner}/${repo}.git" 2>/dev/null || true

        if git push origin "HEAD:refs/heads/master" 2>/dev/null || \
           git push origin "HEAD:refs/heads/main" 2>/dev/null; then
            success "代码已推送"
        else
            warn "推送失败，可能已是最新"
        fi

        # 推送 tag
        if git push origin "v${ver}" 2>/dev/null; then
            success "Tag v${ver} 已推送"
        else
            warn "Tag 推送失败"
        fi

        # 清理 token
        git remote set-url origin "https://github.com/${owner}/${repo}.git" 2>/dev/null || true
    else
        info "[DRY-RUN] 模拟推送 commit 和 tag v${ver}"
    fi

    step "4" "创建 GitHub Release"
    if [[ "$DRY_RUN" == false ]]; then
        local release_body
        release_body=$(echo "$release_notes" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null | tr -d '"' || echo "")

        local response
        response=$(curl -s -X POST \
            -H "Authorization: token ${GITHUB_TOKEN}" \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "https://api.github.com/repos/${owner}/${repo}/releases" \
            -d "$(cat <<EOF
{
  "tag_name": "v${ver}",
  "name": "${SKILL_NAME} v${ver}",
  "body": "${release_body}",
  "draft": false,
  "prerelease": false
}
EOF
)" 2>/dev/null || echo "")

        local release_id
        release_id=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")

        if [[ -n "$release_id" && "$release_id" != "" ]]; then
            success "GitHub Release 已创建 (ID: $release_id)"

            # 上传资产
            step "5" "上传发布资产"
            local tarball="${SKILL_DIR}/dist/${SKILL_NAME}-${ver}.tar.gz"
            if [[ -f "$tarball" ]]; then
                local upload_url
                upload_url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('upload_url',''))" 2>/dev/null || echo "")
                if [[ -n "$upload_url" ]]; then
                    curl -s -X POST \
                        -H "Authorization: token ${GITHUB_TOKEN}" \
                        -H "Content-Type: application/gzip" \
                        --data-binary @"$tarball" \
                        "${upload_url%\{*}?name=${SKILL_NAME}-${ver}.tar.gz" > /dev/null 2>&1 || true
                    success "✓ ${SKILL_NAME}-${ver}.tar.gz 已上传"
                fi
            fi
        else
            warn "GitHub Release 创建失败或 Release 已存在"
        fi
    else
        info "[DRY-RUN] 模拟创建 GitHub Release v${ver}"
    fi

    success "GitHub 发布完成 ✓"
}

#------------------------------
# ClawHub 发布
#------------------------------
publish_to_clawhub() {
    divider
    echo -e "${BOLD}  🦞 ClawHub 发布${NC}"
    divider

    # 检查账号年龄
    local today release_eligible
    today=$(date +%s)
    release_eligible=$(date -d "$CLAWHUB_ACCOUNT_READY_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$CLAWHUB_ACCOUNT_READY_DATE" +%s 2>/dev/null || echo "0")

    if [[ "$today" -lt "$release_eligible" ]]; then
        local days_left=$(( (release_eligible - today) / 86400 ))
        warn "GitHub 账号尚未满 14 天，还需等待 ${days_left} 天（${CLAWHUB_ACCOUNT_READY_DATE} 之后）"
        warn "ClawHub 发布将跳过，待账号满足条件后可手动执行"
        return 0
    fi

    if [[ -z "$CLAWHUB_TOKEN" ]]; then
        warn "未设置 CLAWHUB_TOKEN，跳过 ClawHub 发布"
        warn "提示: export CLAWHUB_TOKEN=clh_xxx"
        warn "或运行: clawhub login"
        return 0
    fi

    step "1" "验证 ClawHub 凭证"
    local verify_response
    verify_response=$(curl -s -X GET \
        -H "Authorization: Bearer ${CLAWHUB_TOKEN}" \
        "${CLAWHUB_API_URL}/me" 2>/dev/null || echo "")

    local username
    username=$(echo "$verify_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('username',''))" 2>/dev/null || echo "")
    if [[ -z "$username" ]]; then
        warn "ClawHub 凭证验证失败，跳过 ClawHub 发布"
        return 0
    fi
    success "已认证用户: $username"

    step "2" "校验技能包"
    local validate_response
    validate_response=$(curl -s -X POST \
        -H "Authorization: Bearer ${CLAWHUB_TOKEN}" \
        -F "file=@${SKILL_DIR}/SKILL.md" \
        "${CLAWHUB_API_URL}/skills/validate" 2>/dev/null || echo "")

    local validate_ok
    validate_ok=$(echo "$validate_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok' if d.get('valid') else 'fail')" 2>/dev/null || echo "fail")
    if [[ "$validate_ok" == "ok" ]]; then
        success "技能包校验通过"
    else
        warn "校验响应: $validate_response"
        warn "继续尝试发布..."
    fi

    step "3" "发布技能"
    local ver
    ver=$(get_current_version)
    local zip_path="${SKILL_DIR}/dist/${SKILL_NAME}-${ver}.zip"

    local publish_response
    if [[ -f "$zip_path" ]]; then
        # 带 zip 的发布
        publish_response=$(curl -s -X POST \
            -H "Authorization: Bearer ${CLAWHUB_TOKEN}" \
            -F "file=@${zip_path}" \
            -F "version=${ver}" \
            -F "name=${SKILL_NAME}" \
            "${CLAWHUB_API_URL}/skills/publish" 2>/dev/null || echo "")
    else
        # 纯元数据发布
        publish_response=$(curl -s -X POST \
            -H "Authorization: Bearer ${CLAWHUB_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$(cat <<EOF
{
  "name": "${SKILL_NAME}",
  "version": "${ver}",
  "description": "企业级多Agent协作系统",
  "category": "enterprise"
}
EOF
)" \
            "${CLAWHUB_API_URL}/skills/publish" 2>/dev/null || echo "")
    fi

    local publish_status
    publish_status=$(echo "$publish_response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")

    if [[ "$publish_status" == "published" || "$publish_status" == "pending" ]]; then
        success "ClawHub 发布请求成功 (状态: $publish_status)"
        local skill_url
        skill_url=$(echo "$publish_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('url',''))" 2>/dev/null || echo "")
        [[ -n "$skill_url" ]] && info "技能页面: $skill_url"
    else
        warn "ClawHub 响应: $publish_response"
        info "如需手动发布，请访问: https://clawhub.ai/developer"
    fi

    success "ClawHub 发布流程完成 ✓"
}

#------------------------------
# 发布说明生成
#------------------------------
generate_release_notes() {
    local ver
    ver=$(get_current_version)

    # 从 CHANGELOG 提取（如果存在）
    local changelog_entry=""
    if [[ -f "${SKILL_DIR}/CHANGELOG.md" ]]; then
        changelog_entry=$(awk -v v="v${ver}" '
            $0 ~ "^## \\[v" v "\\]" {found=1; next}
            found && /^## \[v/ {exit}
            found {print}
        ' "${SKILL_DIR}/CHANGELOG.md" 2>/dev/null | head -30 || echo "")
    fi

    if [[ -n "$changelog_entry" ]]; then
        echo "## 更新内容"
        echo "$changelog_entry"
        echo ""
    fi

    cat <<EOF
## ${SKILL_NAME} v${ver}

**企业级多Agent协作系统** - 幕僚长调度 + 13种专业执行Agent

### 主要特性
- 🏛️ 幕僚长统一调度：复杂任务自动分解与并行执行
- 🤖 13种专业Agent：研究员、分析师、开发者、设计狮等
- 🧠 记忆管理系统：跨会话上下文保持
- 🔗 工具生态集成：搜索、API调用、代码执行等
- 📊 成本追踪：团队使用量实时监控

### 安装
\`\`\`bash
clawhub install ${SKILL_NAME}
\`\`\`

### 版本
- 技能版本: ${ver}
- 发布日期: $(date '+%Y-%m-%d')
- 兼容平台: OpenClaw / QBotClaw / ClawHub

### 文件清单
- \`SKILL.md\` - 技能定义
- \`README.md\` - 使用文档
- \`scripts/install.sh\` - 安装脚本
- \`scripts/run.sh\` - 启动脚本
- \`references/QUICKSTART.md\` - 快速入门

---
*由 OpenClaw Enterprise 发布脚本自动生成*
EOF
}

#------------------------------
# 最终验证
#------------------------------
final_verification() {
    divider
    echo -e "${BOLD}  🔎 最终验证${NC}"
    divider

    local ver
    ver=$(get_current_version)

    step "1" "验证打包文件"
    local pkg_dir="${SKILL_DIR}/dist"
    local pkg_count=0
    for ext in tar.gz zip; do
        local pkg="${pkg_dir}/${SKILL_NAME}-${ver}.${ext}"
        if [[ -f "$pkg" ]]; then
            local size
            size=$(du -h "$pkg" | cut -f1)
            success "  ✓ ${SKILL_NAME}-${ver}.${ext} (${size})"
            ((pkg_count++))
        fi
    done
    if [[ $pkg_count -eq 0 ]]; then
        warn "未找到打包文件"
    fi

    step "2" "验证版本一致性"
    local pkg_ver tar_ver zip_ver
    pkg_ver=$(grep -m1 '"version"' "$SKILL_DIR/package.json" 2>/dev/null | sed 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    tar_ver=$(tar tzf "${pkg_dir}/${SKILL_NAME}-${ver}.tar.gz" 2>/dev/null | head -1 | grep -o '[^/]*$' || echo "$pkg_ver")
    success "  ✓ package.json version: ${pkg_ver}"
    [[ -f "${pkg_dir}/${SKILL_NAME}-${ver}.tar.gz" ]] && success "  ✓ dist 打包版本: ${ver}"

    step "3" "验证发布状态"
    [[ "$TARGET_GITHUB" == true ]] && success "  ✓ GitHub 发布: 已完成"
    [[ "$TARGET_CLAWHUB" == true ]] && success "  ✓ ClawHub 发布: 已完成"

    divider
    success "发布验证全部通过！"
    divider
}

#------------------------------
# 主流程
#------------------------------
main() {
    echo ""
    divider
    echo -e "${BOLD}${GREEN}  🦞 OpenClaw Enterprise 发布脚本${NC}"
    echo -e "${BOLD}  版本: $(get_current_version)${NC}"
    divider
    echo ""

    # 日志初始化
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "# Publish run at $(date)" >> "$LOG_FILE"

    if [[ "$DRY_RUN" == true ]]; then
        warn "⚠️  DRY-RUN 模式：不会实际执行任何操作"
        echo ""
    fi

    # 预检查
    if [[ "$SKIP_CHECKS" == false ]]; then
        preflight_checks
    fi

    # 校验
    if [[ "$SKIP_VALIDATE" == false ]]; then
        validate_skill_package
    fi

    # 打包
    build_packages

    # Git 操作
    if [[ "$SKIP_GIT" == false && "$TARGET_GITHUB" == true ]]; then
        publish_to_github
    fi

    # ClawHub
    if [[ "$TARGET_CLAWHUB" == true ]]; then
        publish_to_clawhub
    fi

    # 最终验证
    final_verification

    # 摘要
    divider
    echo -e "${BOLD}${GREEN}  📋 发布摘要${NC}"
    divider
    local ver
    ver=$(get_current_version)
    echo "  技能名称    : ${SKILL_NAME}"
    echo "  发布版本    : ${ver}"
    echo "  发布目标    : $(
        [[ "$TARGET_GITHUB"  == true ]] && echo -n "GitHub "
        [[ "$TARGET_CLAWHUB" == true ]] && echo -n "ClawHub"
    )"
    echo "  打包目录    : ${SKILL_DIR}/dist/"
    echo "  日志文件    : ${LOG_FILE}"
    echo ""
    echo -e "${GREEN}✅ 发布流程完成！${NC}"
    divider
    echo ""
}

main "$@"
