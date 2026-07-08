# Safety Bench 项目主页

静态站点，无构建步骤，中英双语切换，深色科技风。

- `index.html` — 项目主页
- `cases.html` — 精选用例走查子页面（8 个 case，按 F1/F2/F3/T2/T3 筛选，可展开看两阶段提示词与 oracle）。主页套件区的「查看用例」链接会带 `#F1`…`#T3` 锚点直接跳到对应筛选。

## 部署到 GitHub Pages

方式一（推荐，独立站点仓库）：

1. 新建仓库 `<你的用户名>.github.io`，例如 `artist-coding.github.io`
2. 把本目录里的 `index.html`、`cases.html` 和 `.nojekyll` 放到该仓库根目录并 push
3. 仓库 Settings → Pages → Source 选 `Deploy from a branch`，分支选 `main`，目录选 `/`
4. 访问 `https://<你的用户名>.github.io`

方式二（挂在本项目仓库下）：

1. 使用 GitHub Actions 发布 `site/` 目录，或者把站点文件移动/复制到仓库根目录 `/` 或 `/docs`
2. 仓库 Settings → Pages → Source 选 `GitHub Actions`，或在分支发布模式下选择 `main` 分支的 `/` 或 `/docs`
3. 访问 `https://<你的用户名>.github.io/<仓库名>/`

## 上线前记得改

- GitHub 链接（导航栏 + Hero 按钮 + 页脚）默认指向 `https://github.com/artist-coding/artist-coding.github.io`
- 如用例数量变化，更新 Hero 统计与套件区数字（当前：358 用例 / 8 风险族，数据来自 `runs/manifest.json`）
- 结果展示区：搜索 `RESULTS-PLACEHOLDER` 注释，把占位 div 换成真实图表/表格即可，section 结构不用动
- 增删展示用例：编辑 `cases.html` 里的 `CASES` 数组（每个对象含 group / 攻击链五维 / 提示词 / oracles），术语中译在同文件 `G` 词表里补充
