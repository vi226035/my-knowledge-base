# CLAUDE.md

知识库维护与部署操作指南。

## 项目概览

- **知识库根目录**: `docs/`（Obsidian vault）
- **外部参考材料**: `knowledge_base_material/`（PDF 提取、论文、图片等，通过 `docs/kb_material` 符号链接访问）
- **MkDocs 站点**: `https://vi226035.github.io/my-knowledge-base/`

## 笔记整理工作流

### 整理 Clippings

当用户表达任何与整理抓取文章相关的意图时（不限于"整理抓取的文章"，详见 `CLAUDE-CLIPPINGS.md` 意图识别章节）：

1. **自动识别用户意图** — 完整整理 / 仅翻译 / 仅分类 / 仅格式化 / 部分操作
2. 检查 `docs/Clippings/` 目录下的新文件
3. 读取并评估每篇文章的质量（详见 CLAUDE-CLIPPINGS.md 质量标准）
4. 英文内容翻译为中文（详见翻译规则）
5. 按标准输出格式重构（详见标准笔记结构 + 通俗解释规则）
6. 清理内容、添加 frontmatter、确定分类
7. **自动创建新分类**（如果文章不属于任何现有目录）
8. 移动到目标目录（`ML/`、`信号处理/`、`FPGA/` 等）
9. 添加 Wiki 链接关联已有笔记
10. 在 `docs/index.md` 和 `mkdocs.yml` 的 `nav` 中同步更新
11. 删除 Clippings 中的原始文件
12. 运行 `mkdocs build` 验证
13. 输出整理结果汇总

### 新笔记创建规范

- 文件命名：使用有意义的中文名，如 `空间谱估计与 MUSIC 算法.md`
- 使用 YAML frontmatter（tags、created 日期）
- 笔记之间使用 Wiki 链接 `[[笔记名]]` 建立关联
- 首页 `index.md` 和 `mkdocs.yml` 导航**必须同步更新**

## 知识库定期维护

### 清理检查清单

每次维护时检查以下项目：

1. **空文件**：删除 0 字节或仅含 frontmatter/标题的 `.md` 文件
2. **未引用图片**：检查 `docs/` 根目录和子目录中未被 `![[...]]` 嵌入的图片文件
3. **未引用 PDF 提取资料**：`knowledge_base_material/` 中未被任何笔记引用的 PDF 提取目录（每个可达 8-30 MB）
4. **损坏 Wiki 链接**：搜索 `[[...]]` 确保目标文件存在
5. **孤立笔记**：无入站链接的笔记应考虑在 `index.md` 中添加引用
6. **临时文件**：`.base` 文件、`未命名*` 文件等

### 常用检查命令

```bash
# 查找空文件
find docs/ -name "*.md" -size 0

# 查找未被引用的图片（需比对 ![[...]] 嵌入列表）
grep -roh '!\[\[[^]]*\]\]' docs/ | sed 's/!\[\[//;s/\]\]//' | sort -u > /tmp/refs.txt
find docs/ -name "*.png" -o -name "*.jpg" | xargs -I{} basename {} | sort > /tmp/imgs.txt
comm -13 /tmp/refs.txt /tmp/imgs.txt

# 查找损坏的 Wiki 链接
grep -roh '\[\[[^]]*\]\]' docs/ | sed 's/\[\[//;s/\]\]//;s/|.*//' | sort -u | while read f; do
  [ -z "$(find docs/ -name "${f}.md")" ] && echo "BROKEN: $f"
done
```

## MkDocs 管理

### 配置文件

- `mkdocs.yml`：站点配置、导航结构、主题设置
- `hooks.py`：自定义钩子，将 Obsidian `![[path]]` 语法转为标准 Markdown 图片
- LaTeX 数学公式通过 KaTeX 渲染（`javascripts/` + `stylesheets/`）

### 导航更新规则

新增或移动笔记时**必须**同步更新 `mkdocs.yml` 的 `nav` 部分：

- 新增笔记 → 在对应分类下添加条目
- 移动笔记 → 更新路径
- 删除笔记 → 移除对应条目
- 删除分类 → 移除整个小节

### 构建验证

```bash
# 本地预览（在项目根目录运行）
cd D:\Obsidian\my-knowledge-base
mkdocs build    # 检查构建错误
mkdocs serve    # 本地预览 http://localhost:8000
```

## 部署流程

部署到 GitHub Pages：

```bash
cd D:\Obsidian\my-knowledge-base

# 1. 提交所有更改
git add -A
git commit -m "描述你的更改"
git push origin master

# 2. 部署 MkDocs
mkdocs gh-deploy
```

> **注意**：`mkdocs gh-deploy` 会将站点构建到 `gh-pages` 分支，GitHub Pages 自动从该分支部署。当前无 CI/CD（GitHub Actions），部署需手动执行。

## 目录结构规范

```
D:\Obsidian\my-knowledge-base\
├── docs/                    # Obsidian Vault 根目录 (MkDocs 源目录)
│   ├── index.md             # 首页（与 mkdocs.yml nav 匹配）
│   ├── ML/                  # 机器学习笔记
│   ├── 信号处理/             # 信号处理笔记
│   ├── Pytorch入门/          # PyTorch 教程笔记
│   ├── FPGA/                # FPGA 开发笔记
│   ├── Clippings/           # Obsidian Web Clipper 抓取暂存
│   ├── kb_material/         # → knowledge_base_material/ 符号链接
│   ├── javascripts/         # KaTeX JS
│   ├── stylesheets/         # 自定义 CSS + KaTeX 字体
│   └── .obsidian/           # Obsidian 配置 (Git 忽略部分文件)
├── knowledge_base_material/ # 外部参考材料（PDF 提取、图片等）
├── mkdocs.yml               # MkDocs 站点配置
├── hooks.py                 # MkDocs 自定义钩子
├── CLAUDE.md                # 主操作指南
── CLAUDE-CLIPPINGS.md      # Clippings 整理专用手册
```

## 重要约定

- **Wiki 链接格式**：建议使用 `信号处理/笔记名` 完整路径，确保 Obsidian 外部也可解析
- **MkDocs 排除规则**：`kb_material/` 下的 `.md` 和 `.json` 文件不会构建到站点中（仅图片资源被引用）
- **Git 忽略规则**：`site/`（构建输出）、`.claude/`、`.obsidian/workspace.json` 等不纳入版本控制
