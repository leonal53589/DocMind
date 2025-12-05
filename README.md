# KnowledgeVault (知识库)

一个本地知识存储系统，用于管理和组织文件、笔记和网页内容，支持自动分类功能。

A local knowledge repository system for managing and organizing files, notes, and web content with automatic classification.

## 功能特性 / Features

- **多格式支持**: 导入文档（PDF、DOCX、TXT）、图片、视频、代码文件和网页
- **自动分类**: 基于规则和可选的AI内容分类
- **全文搜索**: 使用SQLite FTS5进行快速内容搜索
- **文件去重**: 自动检测和处理重复文件
- **文本提取**: 从PDF、Word文档等提取和索引文本
- **缩略图生成**: 自动生成图片缩略图以便可视化浏览
- **多接口**: Web界面、命令行和REST API

---

- **Multi-format Support**: Import documents (PDF, DOCX, TXT), images, videos, code files, and web pages
- **Automatic Classification**: Rule-based and optional AI-powered content categorization
- **Full-text Search**: Fast search across all your content using SQLite FTS5
- **File Deduplication**: Automatically detects and handles duplicate files
- **Text Extraction**: Extract and index text from PDFs, Word documents, and more
- **Thumbnail Generation**: Automatic image thumbnails for visual browsing
- **Multiple Interfaces**: Web UI, CLI, and REST API

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
  use_ai: false
  ollama_model: "llama3.2"
  ollama_url: "http://localhost:11434"

import:
  extract_text: true
  generate_thumbnails: true
  deduplicate: true
```

## API文档 / API Documentation

服务器运行后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点 / Key API Endpoints

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/items/` | 分页列出项目 |
| GET | `/api/items/{id}` | 获取项目详情 |
| POST | `/api/import/file` | 导入文件 |
| POST | `/api/import/url` | 从URL导入 |
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
