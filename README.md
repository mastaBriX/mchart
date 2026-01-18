# MChart

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

一个统一的 Python 音乐排行榜数据获取库，支持从多个来源（Billboard、Spotify 等）获取排行榜数据。

[English](#english) | [中文](#中文)

---

## 中文

### ✨ 特性

- 🎵 **多数据源支持** - 统一接口访问多个音乐排行榜平台
- 🔧 **灵活配置** - TypedDict 配置系统，支持按需定制
- 📊 **双重返回格式** - 支持字典（JSON）和 Pydantic 模型两种返回格式
- 🚀 **易于使用** - 简洁的 API 设计，开箱即用
- 🛡️ **类型安全** - 完整的类型提示支持
- ⚡ **可扩展** - 标准化的 Provider 接口，易于添加新数据源

### 🎯 支持的平台

| 平台 | 状态 | 功能 |
|-----|------|------|
| Billboard | ✅ 已实现 | 最新排行榜、列出排行榜 |
| Spotify | 📋 计划中 | 等待实现 |
| Apple Music | 📋 计划中 | 未来支持 |
| YouTube Music | 📋 计划中 | 未来支持 |

### 📦 安装

#### 使用 pip

```bash
pip install mchart
```

#### 使用 uv（推荐）

```bash
uv add mchart
```

#### 可选依赖

为获得更快的 HTML 解析速度，建议安装 lxml：

```bash
pip install mchart[lxml]
# 或
uv add mchart[lxml]
```

### 🚀 快速开始

#### 基础使用

```python
from mchart import MChart

# 创建客户端
client = MChart()

# 获取 Billboard Hot 100（返回字典）
chart = client.get_chart("billboard", "hot-100")

print(f"排行榜: {chart['metadata']['title']}")
print(f"发布日期: {chart['published_date']}")
print(f"总条目数: {len(chart['entries'])}")

# 显示前 5 名
for entry in chart['entries'][:5]:
    song = entry['song']
    print(f"#{entry['rank']} - {song['title']} by {song['artist']}")
```

#### 使用 Pydantic 模型

```python
from mchart import MChart

client = MChart()

# 返回 Pydantic 模型，支持类型提示和便捷方法
chart = client.get_chart("billboard", "hot-100", return_type="model")

# 使用模型的便捷方法
print(f"总条目数: {chart.total_entries}")

# 查找特定艺术家
taylor_songs = chart.find_by_artist("Taylor Swift")
for entry in taylor_songs:
    print(f"#{entry.rank} - {entry.song.title}")

# 获取前 10 名
top_10 = chart.get_top(10)
```

#### 自定义配置

```python
from mchart import MChart

# 配置 Billboard provider
config = {
    "billboard": {
        "timeout": 60,              # 请求超时（秒）
        "max_retries": 5,           # 最大重试次数
        "parser": "html.parser",    # HTML 解析器
        "max_chart_entries": 50,    # 限制返回条目数
    }
}

client = MChart(config)
chart = client.get_chart("billboard", "hot-100")
```

### 📚 示例

查看 `examples/` 目录获取更多示例：

- `fetch_billboard_hot100.py` - 获取并保存 Billboard Hot 100
- `list_all_charts.py` - 列出所有可用排行榜
- `compare_charts.py` - 比较多个排行榜
- `search_artist.py` - 搜索特定艺术家

运行示例：

```bash
# 使用 uv
uv run python examples/fetch_billboard_hot100.py

# 或使用 python
python examples/fetch_billboard_hot100.py
```

### 🎵 支持的排行榜

#### Billboard

- `hot-100` - Billboard Hot 100（美国最热门 100 首歌曲）
- `billboard-200` - Billboard 200（最热门 200 张专辑）
- `global-200` - Global 200（全球最热门 200 首歌曲）
- `artist-100` - Artist 100（最热门 100 位艺术家）
- `streaming-songs` - Streaming Songs（流媒体最热歌曲）
- `radio-songs` - Radio Songs（电台最热播放歌曲）
- `digital-song-sales` - Digital Song Sales（数字单曲销量榜）

### 📖 文档

完整的 API 文档请查看 [docs/API.md](docs/API.md)

### 🛠️ 开发

#### 克隆仓库

```bash
git clone https://github.com/yourusername/mchart.git
cd mchart
```

#### 安装开发依赖

```bash
# 使用 uv
uv sync --all-extras

# 或使用 pip
pip install -e ".[dev,lxml]"
```

#### 运行测试

```bash
pytest
```

### 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

特别欢迎以下贡献：
- 新的 provider 实现（Spotify、Apple Music 等）
- Bug 修复和功能增强
- 文档改进
- 测试用例

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

### 🙏 致谢

- [Billboard](https://www.billboard.com/) - 排行榜数据源
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证
- [Requests](https://requests.readthedocs.io/) - HTTP 库

---

## English

### ✨ Features

- 🎵 **Multiple Data Sources** - Unified interface for accessing multiple music chart platforms
- 🔧 **Flexible Configuration** - TypedDict-based configuration system with customization support
- 📊 **Dual Return Formats** - Support for both dict (JSON) and Pydantic model return types
- 🚀 **Easy to Use** - Clean API design, works out of the box
- 🛡️ **Type Safe** - Full type hints support
- ⚡ **Extensible** - Standardized Provider interface for easy addition of new data sources

### 🎯 Supported Platforms

| Platform | Status | Features |
|----------|--------|----------|
| Billboard | ✅ Implemented | Latest charts, List charts |
| Spotify | 📋 Planned | Coming soon |
| Apple Music | 📋 Planned | Future support |
| YouTube Music | 📋 Planned | Future support |

### 📦 Installation

#### Using pip

```bash
pip install mchart
```

#### Using uv (Recommended)

```bash
uv add mchart
```

#### Optional Dependencies

For faster HTML parsing, install lxml:

```bash
pip install mchart[lxml]
# or
uv add mchart[lxml]
```

### 🚀 Quick Start

#### Basic Usage

```python
from mchart import MChart

# Create client
client = MChart()

# Get Billboard Hot 100 (returns dict)
chart = client.get_chart("billboard", "hot-100")

print(f"Chart: {chart['metadata']['title']}")
print(f"Date: {chart['published_date']}")
print(f"Total entries: {len(chart['entries'])}")

# Show top 5
for entry in chart['entries'][:5]:
    song = entry['song']
    print(f"#{entry['rank']} - {song['title']} by {song['artist']}")
```

#### Using Pydantic Models

```python
from mchart import MChart

client = MChart()

# Return Pydantic model with type hints and convenient methods
chart = client.get_chart("billboard", "hot-100", return_type="model")

# Use model's convenient methods
print(f"Total entries: {chart.total_entries}")

# Find specific artist
taylor_songs = chart.find_by_artist("Taylor Swift")
for entry in taylor_songs:
    print(f"#{entry.rank} - {entry.song.title}")

# Get top 10
top_10 = chart.get_top(10)
```

#### Custom Configuration

```python
from mchart import MChart

# Configure Billboard provider
config = {
    "billboard": {
        "timeout": 60,              # Request timeout (seconds)
        "max_retries": 5,           # Max retry attempts
        "parser": "html.parser",    # HTML parser
        "max_chart_entries": 50,    # Limit returned entries
    }
}

client = MChart(config)
chart = client.get_chart("billboard", "hot-100")
```

### 📚 Examples

See the `examples/` directory for more examples:

- `fetch_billboard_hot100.py` - Fetch and save Billboard Hot 100
- `list_all_charts.py` - List all available charts
- `compare_charts.py` - Compare multiple charts
- `search_artist.py` - Search for specific artist

Run examples:

```bash
# Using uv
uv run python examples/fetch_billboard_hot100.py

# Or using python
python examples/fetch_billboard_hot100.py
```

### 🎵 Supported Charts

#### Billboard

- `hot-100` - Billboard Hot 100 (Top 100 songs in the US)
- `billboard-200` - Billboard 200 (Top 200 albums)
- `global-200` - Global 200 (Top 200 songs globally)
- `artist-100` - Artist 100 (Top 100 artists)
- `streaming-songs` - Streaming Songs (Most-streamed songs)
- `radio-songs` - Radio Songs (Most-played on radio)
- `digital-song-sales` - Digital Song Sales (Best-selling digital songs)

### 📖 Documentation

For complete API documentation, see [docs/API.md](docs/API.md)

### 🛠️ Development

#### Clone Repository

```bash
git clone https://github.com/yourusername/mchart.git
cd mchart
```

#### Install Development Dependencies

```bash
# Using uv
uv sync --all-extras

# Or using pip
pip install -e ".[dev,lxml]"
```

#### Run Tests

```bash
pytest
```

### 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

We especially welcome:
- New provider implementations (Spotify, Apple Music, etc.)
- Bug fixes and feature enhancements
- Documentation improvements
- Test cases

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Billboard](https://www.billboard.com/) - Chart data source
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Requests](https://requests.readthedocs.io/) - HTTP library

---

**Made with ❤️ for music lovers and developers**
