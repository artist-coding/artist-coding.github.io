# HarnessSafe 项目网站

公开站点：[artist-coding.github.io](https://artist-coding.github.io/)

论文：[arXiv:2608.06984](https://arxiv.org/abs/2608.06984)

实验框架：[artist-coding/harnesssafe](https://github.com/artist-coding/harnesssafe)

这是无需构建的静态 GitHub Pages 网站，提供中英切换、三张论文原图的放大浏览与 PDF 入口、当前适配器状态、离线快速开始，以及从冻结基准生成的 328 个案例索引。

- `index.html`：论文、图解、案例分布、历史结果、当前框架和引用。
- `cases.html`：按七类家族筛选、关键词搜索和分页查看案例。
- `assets/site.css`、`assets/site.js`：共享样式、语言切换、图像对话框和复制操作。
- `assets/cases.json`：从实际案例元数据提取的公开索引。
- `assets/content-source.json`：案例源提交、manifest 与各案例元数据的哈希。
- `assets/figures/`：三张原始论文 PDF、2400 px PNG 与来源哈希。

## 本地预览

```bash
python -m http.server 8766 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8766/`。案例页需要通过 HTTP 读取 JSON，请勿直接双击 HTML。

## 同步案例与配图

需要 Python 3.10+；生成配图还需要 Poppler 的 `pdftoppm` 在 PATH 中。

```bash
python scripts/sync-content.py --benchmark-root /path/to/harnesssafe
python scripts/sync-content.py --benchmark-root /path/to/harnesssafe --figures-dir /path/to/paper/Figures
```

脚本直接读取 manifest 与 `case_meta.json`，校验七类家族的 328 个案例；没有模型调用。案例数量或家族改变时，应同时审查网页统计与筛选项，脚本会拒绝静默改变现有展示口径。

## 发布与来源

GitHub Pages 从 `main` 分支根目录发布，`.nojekyll` 保留静态资源。推送后检查 Pages 部署状态与线上页面。

论文图 1、图 2、图 3分别对应 `benchmark`、`background`、`checkpoint_dist`，图像内容未重绘或改写，来源为作者提供的原始 PDF。原论文作者为 Xiao Zhang、Yusheng Wang、Yuhao Fei、Dongyuan Li、Zian Liang、Liuyu Xiang、Hongxun Gu、Zhaofeng He；论文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。

结果图明确对应 2026-08-07 的 arXiv v1 历史实验。当前适配器能力以代码仓库文档为准；当前 CLI 版本需重新测试，未评分或未完成的记录不能视作安全。
