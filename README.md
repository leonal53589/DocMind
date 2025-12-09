# KnowledgeVault (知识库)

一个本地知识存储系统，用于管理和组织文件、笔记和网页内容，支持自动分类功能。

## 功能特性 / Features

- **多格式支持**: 导入文档（PDF、DOCX、TXT）、图片、视频、代码文件和网页
- **Markdown渲染**: 内置Markdown查看器，支持语法高亮、目录导航、深色模式和字体大小调整
- **文件预览**: 支持多种文件类型的内置预览（Markdown、图片、PDF、视频、音频、代码）
- **自动分类**: 基于规则和可选的AI内容分类（支持DeepSeek API）
- **全文搜索**: 使用SQLite FTS5进行快速内容搜索
- **文件去重**: 自动检测和处理重复文件
- **文本提取**: 从PDF、Word文档等提取和索引文本
- **缩略图生成**: 自动生成图片缩略图以便可视化浏览
- **收藏夹**: 快速收藏重要项目，便于快速访问
- **项目关联**: 建立项目之间的关联关系，可视化网络图展示
- **重命名支持**: 直接在界面上重命名项目
- **AI摘要**: 使用AI生成内容摘要和分类推荐
- **多接口**: Web界面、命令行和REST API

---

## 快速开始 / Quick Start

### 环境要求 / Prerequisites

- Python 3.10+
- Node.js 18+ (用于前端开发)
- pip 或 uv (Python包管理器)

### 安装 / Installation

1. **克隆仓库 / Clone the repository**:
   ```bash
   git clone https://github.com/knowledgevault/knowledgevault.git
   cd knowledgevault
   ```

2. **安装Python依赖 / Install Python dependencies**:
   ```bash
   # 使用pip / Using pip
   pip install -e .

   # 或使用uv（推荐）/ Or using uv (recommended)
   uv pip install -e .
   ```

3. **安装前端依赖 / Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

   主要前端依赖 / Key Frontend Dependencies:
   - Vue 3 + Vite
   - Tailwind CSS
   - Pinia (状态管理)
   - Vue Router
   - marked (Markdown解析)
   - highlight.js (代码语法高亮)
   - @heroicons/vue (图标库)

### 导入 deepseek 的 API 密钥 / Import deepseek API key (optional)
如果你希望使用 deepseek 的 AI 分类功能，请在环境变量中设置 API 密钥：

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key"
``` 

### 运行应用 / Running the Application

#### 方式一：同时启动后端和前端（开发模式）

**终端1 - 启动后端API服务器**:
```bash
kvault serve
# 或 / or
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

**终端2 - 启动前端开发服务器**:
```bash
cd frontend
npm run dev
```

在浏览器中打开 http://localhost:5173

#### 方式二：仅使用命令行

```bash
# 启动服务器
kvault serve

# 导入文件
kvault import /path/to/file.pdf
kvault import /path/to/directory/

# 导入网页
kvault import https://example.com/article

# 搜索知识库
kvault search "机器学习"

# 列出项目
kvault list-items

# 查看状态
kvault status
```

### 生产构建 / Production Build

构建前端生产版本：
```bash
cd frontend
npm run build
```

构建后的文件将位于 `frontend/dist/`，可由后端提供服务。

## 项目结构 / Project Structure

```
knowledgevault/
├── backend/                 # FastAPI REST API
│   └── app/
│       ├── main.py         # 应用入口
│       ├── config.py       # 配置管理
│       ├── database.py     # SQLAlchemy设置
│       ├── models/         # 数据库模型
│       ├── routers/        # API端点
│       ├── schemas/        # Pydantic模式
│       ├── services/       # 业务逻辑
│       └── utils/          # 工具函数
├── frontend/               # Vue 3 Web应用
│   └── src/
│       ├── api/           # API客户端
│       ├── components/    # Vue组件
│       │   ├── FilePreviewModal.vue  # 通用文件预览模态框
│       │   ├── MarkdownViewer.vue    # Markdown渲染组件
│       │   ├── ItemCard.vue          # 项目卡片组件
│       │   ├── ImportModal.vue       # 导入模态框
│       │   ├── SearchBar.vue         # 搜索栏组件
│       │   └── Sidebar.vue           # 侧边栏导航
│       ├── stores/        # Pinia状态管理
│       ├── views/         # 页面组件
│       └── router/        # Vue Router配置
├── cli/                    # 命令行界面
│   ├── main.py            # CLI入口
│   └── commands/          # CLI命令
├── data/                   # 数据存储（运行时创建）
│   ├── vault.db           # SQLite数据库
│   ├── files/             # 存储的文件
│   └── thumbnails/        # 生成的缩略图
├── pyproject.toml         # Python项目配置
└── config.yaml            # 可选配置文件
```

## 配置 / Configuration

在项目根目录创建 `config.yaml` 文件以自定义设置：

```yaml
server:
  host: "127.0.0.1"
  port: 8000

storage:
  data_dir: "./data"
  max_file_size: 104857600  # 100MB

classification:
  auto_classify: true
  ai_provider: "deepseek"   # 可选: "ollama" 或 "deepseek"
  # DeepSeek设置（推荐）
  deepseek_url: "https://api.deepseek.com/v1/chat/completions"
  deepseek_model: "deepseek-chat"
  # Ollama设置（本地）
  ollama_model: "llama3.2"
  ollama_url: "http://localhost:11434"

import:
  extract_text: true
  generate_thumbnails: true
  deduplicate: true
```

### 环境变量 / Environment Variables

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 使用DeepSeek时需要 |

## API文档 / API Documentation

服务器运行后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点 / Key API Endpoints

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/items/` | 分页列出项目 |
| GET | `/api/items/{id}` | 获取项目详情 |
| PUT | `/api/items/{id}` | 更新项目（重命名、修改分类等） |
| DELETE | `/api/items/{id}` | 删除项目 |
| POST | `/api/items/{id}/favorite` | 切换收藏状态 |
| POST | `/api/items/{id}/associations` | 添加项目关联 |
| DELETE | `/api/items/{id}/associations/{aid}` | 删除项目关联 |
| GET | `/api/items/{id}/associations` | 获取项目关联列表 |
| POST | `/api/items/{id}/ai-summary` | 获取AI摘要和分类推荐 |
| POST | `/api/import/file` | 导入文件 |
| POST | `/api/import/url` | 从URL导入 |
| POST | `/api/import/{id}/reclassify` | AI重新分类 |
| GET | `/api/search/` | 全文搜索 |
| GET | `/api/categories/` | 列出分类 |
| GET | `/api/stats` | 知识库统计 |

## 默认分类 / Default Categories

知识库创建以下默认分类：

- **数学原理 / Mathematical Principles**: 数学概念和证明
- **创意与概念 / Ideas & Concepts**: 创意想法和概念笔记
- **程序实现 / Program Implementation**: 代码、脚本和编程资源
- **研究论文 / Research Papers**: 学术论文和研究材料
- **参考文档 / Reference Documentation**: 技术文档和参考资料
- **网络资源 / Web Resources**: 保存的网页和书签
- **工具与实用程序 / Tools & Utilities**: 软件工具和实用程序
- **未分类 / Uncategorized**: 待分类项目

## 支持的文件类型 / Supported File Types

| 类型 | 扩展名 |
|------|--------|
| 文档 | PDF, DOCX, DOC, TXT, MD, RST, HTML |
| 图片 | PNG, JPG, JPEG, GIF, WEBP, BMP, SVG |
| 视频 | MP4, WEBM, MKV, AVI, MOV, WMV |
| 代码 | Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Ruby, PHP等 |
| 数据 | JSON, YAML, XML, TOML, INI, SQL, CSV |

## 文件预览功能 / File Preview Features

知识库支持多种文件类型的内置预览功能：

### Markdown查看器 / Markdown Viewer
- **语法高亮**: 使用highlight.js进行代码块语法高亮
- **目录导航**: 自动生成目录（TOC），支持点击跳转
- **深色模式**: 一键切换深色/浅色主题
- **字体调整**: 支持调整字体大小（12px-24px）
- **GFM支持**: 完整支持GitHub Flavored Markdown

### 预览支持的文件类型 / Previewable File Types
| 类型 | 描述 |
|------|------|
| Markdown | 渲染预览，支持语法高亮和目录 |
| 图片 | 内置图片查看器 |
| PDF | 使用浏览器内置PDF查看器 |
| 视频 | HTML5视频播放器 |
| 音频 | HTML5音频播放器 |
| 代码 | 语法高亮的代码查看器 |
| 文本 | 纯文本预览 |

### 快捷键 / Keyboard Shortcuts
- `Esc`: 关闭预览窗口
- `Ctrl/Cmd + F`: 切换全屏模式

## 命令行命令 / CLI Commands

```bash
# 服务器管理
kvault serve              # 启动API服务器
kvault serve --reload     # 启动并自动重载（开发模式）
kvault serve check        # 检查服务器是否运行

# 导入内容
kvault import <路径>      # 导入文件或目录
kvault import <网址>      # 导入网页  

# 浏览内容
kvault list-items         # 列出所有项目
kvault list-items -c <分类>  # 按分类筛选
kvault list-items -t file        # 按类型筛选
kvault categories         # 列出所有分类

# 搜索
kvault search <关键词>    # 全文搜索

# 信息
kvault status             # 显示知识库统计
kvault version            # 显示版本
```

## 开发 / Development

### 设置开发环境 / Setup Development Environment

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装pre-commit钩子
pre-commit install
```

### 运行测试 / Running Tests

```bash
pytest
```

### 代码格式化 / Code Formatting

```bash
ruff check .
ruff format .
```

## 许可证 / License

MIT License - 详见LICENSE文件

## 贡献 / Contributing

欢迎贡献！请随时提交问题和拉取请求。

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request
