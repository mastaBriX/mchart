# MChart API 文档

MChart 是一个统一的音乐排行榜数据获取库，支持从多个来源（如 Billboard、Spotify 等）获取排行榜数据。

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [配置](#配置)
- [主客户端 API](#主客户端-api)
- [数据模型](#数据模型)
- [Provider API](#provider-api)
- [已实现的功能](#已实现的功能)
- [规划中的功能](#规划中的功能)

---

## 安装

### 使用 pip

```bash
pip install mchart
```

### 使用 uv

```bash
uv add mchart
```

### 可选依赖

为了更快的 HTML 解析速度，建议安装 lxml：

```bash
pip install mchart[lxml]
# 或
uv add mchart[lxml]
```

---

## 快速开始

### 基础使用

```python
from mchart import MChart

# 创建客户端
client = MChart()

# 获取 Billboard Hot 100（返回字典，适合 JSON 序列化）
chart = client.get_chart("billboard", "hot-100")

print(f"排行榜: {chart['metadata']['title']}")
print(f"发布日期: {chart['published_date']}")
print(f"总条目数: {len(chart['entries'])}")

# 显示前 5 名
for entry in chart['entries'][:5]:
    song = entry['song']
    print(f"#{entry['rank']} - {song['title']} by {song['artist']}")
```

### 使用 Pydantic 模型

```python
from mchart import MChart

client = MChart()

# 返回 Pydantic 模型，支持类型提示和方法
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

### 使用上下文管理器

```python
from mchart import MChart

# 自动清理资源
with MChart() as client:
    chart = client.get_chart("billboard", "hot-100")
    # 处理数据...
# 退出时自动关闭连接
```

---

## 配置

### 基础配置

所有 provider 共享的配置项：

```python
from mchart import MChart

config = {
    "billboard": {
        "timeout": 60,              # 请求超时（秒）
        "max_retries": 5,           # 最大重试次数
        "user_agent": "MyApp/1.0",  # 自定义 User-Agent
        "verify_ssl": True,         # 是否验证 SSL 证书
        "proxy": "http://proxy.example.com:8080",  # HTTP 代理
        "enable_cache": False,      # 是否启用缓存
        "cache_ttl": 3600,          # 缓存过期时间（秒）
    }
}

client = MChart(config)
```

### Billboard 特定配置

```python
config = {
    "billboard": {
        # 基础配置项...
        "parser": "lxml",           # HTML 解析器：lxml, html.parser, html5lib
        "include_images": True,     # 是否获取封面图片 URL
        "max_chart_entries": 50,    # 限制返回的条目数量（None 表示全部）
        "fallback_to_default": True,  # 未找到排行榜时回退到 Hot 100
    }
}

client = MChart(config)
```

### Spotify 配置（未来实现）

```python
config = {
    "spotify": {
        "client_id": "your_spotify_client_id",
        "client_secret": "your_spotify_client_secret",
        "market": "US",             # 市场/地区代码
        "access_token": None,       # 可选：直接提供 access token
        "auto_refresh_token": True, # 自动刷新过期的 token
    }
}

client = MChart(config)
```

---

## 主客户端 API

### `MChart(config=None)`

创建 MChart 客户端实例。

**参数：**
- `config` (dict, optional): Provider 配置字典

**示例：**
```python
client = MChart()
# 或带配置
client = MChart({"billboard": {"timeout": 60}})
```

---

### `client.providers`

获取所有可用的 provider 列表。

**返回：** `list[str]` - provider 名称列表

**示例：**
```python
print(client.providers)  # ['billboard']
```

---

### `client.get_chart(provider, chart_name, return_type="dict", **kwargs)`

获取最新的排行榜数据。

**参数：**
- `provider` (str): Provider 名称，如 `"billboard"`, `"spotify"`
- `chart_name` (str): 排行榜名称，如 `"hot-100"`, `"billboard-200"`
- `return_type` (str): 返回类型，`"dict"` 或 `"model"`，默认 `"dict"`
- `**kwargs`: Provider 特定的额外参数

**返回：** 
- `dict[str, Any]` 如果 `return_type="dict"`
- `Chart` 模型 如果 `return_type="model"`

**异常：**
- `ValueError`: provider 不可用或排行榜名称无效
- `Exception`: 获取数据失败

**示例：**
```python
# 返回字典（默认）
chart = client.get_chart("billboard", "hot-100")

# 返回 Pydantic 模型
chart = client.get_chart("billboard", "hot-100", return_type="model")
```

---

### `client.get_chart_by_date(provider, chart_name, chart_date, return_type="dict", **kwargs)`

获取指定日期的排行榜数据（如果 provider 支持）。

**参数：**
- `provider` (str): Provider 名称
- `chart_name` (str): 排行榜名称
- `chart_date` (date): 排行榜日期
- `return_type` (str): 返回类型，`"dict"` 或 `"model"`
- `**kwargs`: Provider 特定的额外参数

**返回：** 排行榜数据

**异常：**
- `NotImplementedError`: provider 不支持历史数据

**示例：**
```python
from datetime import date

# 注意：Billboard 当前不支持历史数据
chart = client.get_chart_by_date("billboard", "hot-100", date(2024, 1, 1))
```

---

### `client.list_charts(provider, return_type="dict")`

列出指定 provider 的所有可用排行榜。

**参数：**
- `provider` (str): Provider 名称
- `return_type` (str): 返回类型，`"dict"` 或 `"model"`

**返回：** 
- `list[dict[str, Any]]` 如果 `return_type="dict"`
- `list[ChartMetadata]` 如果 `return_type="model"`

**示例：**
```python
charts = client.list_charts("billboard")
for chart in charts:
    print(f"{chart['title']}: {chart['description']}")
```

---

### `client.list_all_charts(return_type="dict")`

列出所有 provider 的所有可用排行榜。

**返回：** `dict[str, list]` - provider 名称到排行榜列表的映射

**示例：**
```python
all_charts = client.list_all_charts()
for provider, charts in all_charts.items():
    print(f"{provider}: {len(charts)} 个排行榜")
```

---

### `client.close()`

关闭所有 provider 连接，释放资源。

建议在使用完客户端后调用，或使用上下文管理器。

**示例：**
```python
client = MChart()
try:
    # 使用客户端...
    pass
finally:
    client.close()
```

---

## 数据模型

### Chart（排行榜）

完整的排行榜数据。

**字段：**
```python
{
    "metadata": ChartMetadata,      # 排行榜元数据
    "published_date": str,          # 发布日期（ISO 格式）
    "entries": list[ChartEntry]     # 排行榜条目列表
}
```

**Pydantic 模型方法：**
- `chart.total_entries` - 总条目数
- `chart.get_top(n)` - 获取前 N 名
- `chart.find_by_artist(name)` - 按艺术家搜索
- `chart.find_by_title(title)` - 按歌曲标题搜索
- `chart.to_dict()` - 转换为字典

**示例：**
```python
# 字典格式
chart = client.get_chart("billboard", "hot-100")
print(chart["published_date"])
print(len(chart["entries"]))

# 模型格式
chart = client.get_chart("billboard", "hot-100", return_type="model")
print(chart.total_entries)
top_5 = chart.get_top(5)
```

---

### ChartMetadata（排行榜元数据）

排行榜的基本信息。

**字段：**
```python
{
    "provider": str,      # Provider 名称，如 "billboard"
    "title": str,         # 排行榜标题
    "description": str,   # 排行榜描述
    "url": str,          # 排行榜原始 URL
    "type": str          # 排行榜类型："single"（单曲榜）或 "album"（专辑榜）
}
```

**type 字段说明：**
- `"single"`: 单曲榜，排行榜条目包含歌曲信息（使用 `song` 字段）
- `"album"`: 专辑榜，排行榜条目包含专辑信息（使用 `album` 字段）

**示例：**
```python
metadata = chart["metadata"]
print(f"排行榜: {metadata['title']}")
print(f"类型: {metadata['type']}")  # "single" 或 "album"
```

---

### ChartEntry（排行榜条目）

单个排行榜条目。根据排行榜类型，条目可能包含歌曲信息（单曲榜）或专辑信息（专辑榜）。

**字段：**
```python
{
    "song": Song,           # 歌曲信息（单曲榜使用，专辑榜为 None）
    "album": Album,         # 专辑信息（专辑榜使用，单曲榜为 None）
    "rank": int,            # 当前排名
    "weeks_on_chart": int,  # 在榜周数
    "last_week": int,       # 上周排名（0 表示新上榜）
    "peak_position": int    # 历史最高排名
}
```

**重要说明：**
- 单曲榜（`metadata.type == "single"`）：使用 `song` 字段，`album` 字段为 `None`
- 专辑榜（`metadata.type == "album"`）：使用 `album` 字段，`song` 字段为 `None`
- 每个条目必须且仅能包含 `song` 或 `album` 中的一个

**示例（单曲榜）：**
```python
# 获取单曲榜
chart = client.get_chart("billboard", "hot-100")
entry = chart["entries"][0]

if chart["metadata"]["type"] == "single":
    print(f"#{entry['rank']} - {entry['song']['title']}")
    print(f"艺术家: {entry['song']['artist']}")
    print(f"已上榜 {entry['weeks_on_chart']} 周")
```

**示例（专辑榜）：**
```python
# 获取专辑榜
chart = client.get_chart("billboard", "billboard-200")
entry = chart["entries"][0]

if chart["metadata"]["type"] == "album":
    print(f"#{entry['rank']} - {entry['album']['title']}")
    print(f"艺术家: {entry['album']['artist']}")
    print(f"已上榜 {entry['weeks_on_chart']} 周")
```

---

### Song（歌曲信息）

歌曲的详细信息。用于单曲榜（`ChartEntry.song`）。

**字段：**
```python
{
    "title": str,        # 歌曲标题
    "artist": str,       # 主要艺术家
    "artists": list[str],  # 所有艺术家列表
    "image": str,        # 封面图片 URL
    "album": str         # 专辑名称
}
```

**示例：**
```python
song = entry["song"]
print(f"{song['title']} by {song['artist']}")
if song["artists"]:
    print(f"合作艺术家: {', '.join(song['artists'])}")
```

---

### Album（专辑信息）

专辑的详细信息。用于专辑榜（`ChartEntry.album`）。

**字段：**
```python
{
    "title": str,        # 专辑标题
    "artist": str,       # 主要艺术家
    "artists": list[str],  # 所有艺术家列表
    "image": str        # 封面图片 URL
}
```

**示例：**
```python
album = entry["album"]
print(f"{album['title']} by {album['artist']}")
if album["artists"]:
    print(f"合作艺术家: {', '.join(album['artists'])}")
```

---

## Provider API

### Billboard Provider

#### 支持的排行榜

| 排行榜名称 | 说明 |
|-----------|------|
| `hot-100` | Billboard Hot 100 - 美国最热门 100 首歌曲 |
| `billboard-200` | Billboard 200 - 最热门 200 张专辑 |
| `global-200` | Global 200 - 全球最热门 200 首歌曲 |
| `artist-100` | Artist 100 - 最热门 100 位艺术家 |
| `streaming-songs` | Streaming Songs - 流媒体最热歌曲 |
| `radio-songs` | Radio Songs - 电台最热播放歌曲 |
| `digital-song-sales` | Digital Song Sales - 数字单曲销量榜 |

#### 支持的功能

- ✅ 获取最新排行榜 (`get_chart`)
- ✅ 列出可用排行榜 (`list_charts`)
- ❌ 获取历史排行榜（Billboard 网站不支持通过爬虫获取历史数据）

#### 示例

**单曲榜示例：**
```python
from mchart import MChart

client = MChart()

# 获取 Billboard Hot 100（单曲榜）
hot100 = client.get_chart("billboard", "hot-100")

# 检查排行榜类型
print(f"排行榜类型: {hot100['metadata']['type']}")  # "single"

# 访问歌曲信息
for entry in hot100["entries"][:5]:
    song = entry["song"]  # 单曲榜使用 song 字段
    print(f"#{entry['rank']} - {song['title']} by {song['artist']}")
```

**专辑榜示例：**
```python
from mchart import MChart

client = MChart()

# 获取 Billboard 200（专辑榜）
bb200 = client.get_chart("billboard", "billboard-200")

# 检查排行榜类型
print(f"排行榜类型: {bb200['metadata']['type']}")  # "album"

# 访问专辑信息
for entry in bb200["entries"][:5]:
    album = entry["album"]  # 专辑榜使用 album 字段
    print(f"#{entry['rank']} - {album['title']} by {album['artist']}")
    print(f"  已上榜 {entry['weeks_on_chart']} 周")
```

**列出所有 Billboard 排行榜：**
```python
charts = client.list_charts("billboard")
for chart in charts:
    print(f"{chart['title']} ({chart['type']})")  # 显示排行榜名称和类型
```

---

### Spotify Provider（规划中）

> ⚠️ **注意：** Spotify provider 当前仅为占位实现，尚未完全开发。

#### 计划支持的功能

- 📋 获取 Spotify 官方排行榜播放列表
- 📋 支持地区特定排行榜（Top 50 各国版本）
- 📋 病毒排行榜（Viral 50）
- 📋 新歌排行榜
- ❌ 历史数据（Spotify API 限制）

#### 使用示例（未来）

```python
from mchart import MChart

config = {
    "spotify": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "market": "US"
    }
}

client = MChart(config)

# 获取 Spotify Top 50 美国
chart = client.get_chart("spotify", "top-50-us")
```

---

## 已实现的功能

### ✅ 核心功能

- [x] 统一的客户端接口
- [x] 灵活的配置系统（TypedDict）
- [x] 支持字典和 Pydantic 模型两种返回格式
- [x] 标准化的数据模型
- [x] 错误处理和重试机制
- [x] 上下文管理器支持

### ✅ Billboard Provider

- [x] 获取最新排行榜
- [x] 支持 7 种主要排行榜
- [x] 提取歌曲信息（标题、艺术家、图片等）
- [x] 提取排名信息（当前排名、上周排名、在榜周数、峰值排名）
- [x] 配置化的 HTML 解析器选择
- [x] 限制返回条目数量
- [x] 列出所有可用排行榜

### ✅ 文档和示例

- [x] 完整的 API 文档
- [x] 多个使用示例脚本
- [x] 配置指南

---

## 规划中的功能

### 🔄 短期计划

#### Spotify Provider
- [ ] 实现 OAuth 认证流程
- [ ] 获取官方排行榜播放列表
- [ ] 支持地区特定排行榜
- [ ] Token 自动刷新机制

#### 功能增强
- [ ] 缓存机制实现
- [ ] 异步 API 支持（`async/await`）
- [ ] 批量获取多个排行榜
- [ ] 数据导出（CSV、Excel）

#### 测试和质量
- [ ] 单元测试覆盖
- [ ] 集成测试
- [ ] CI/CD 流程
- [ ] 代码质量检查

### 📅 长期计划

#### 新 Provider
- [ ] **Apple Music** - Apple Music 排行榜
- [ ] **YouTube Music** - YouTube 音乐排行榜
- [ ] **Deezer** - Deezer 排行榜
- [ ] **Last.fm** - Last.fm 统计数据
- [ ] **Melon** - 韩国 Melon 排行榜
- [ ] **Oricon** - 日本 Oricon 排行榜
- [ ] **QQ Music** - QQ 音乐排行榜（国内）
- [ ] **NetEase Music** - 网易云音乐排行榜（国内）

#### 高级功能
- [ ] 排行榜数据对比分析
- [ ] 趋势分析和预测
- [ ] 艺术家统计信息
- [ ] 排行榜历史数据（如果可用）
- [ ] 数据可视化工具
- [ ] Web API 服务

#### 生态系统
- [ ] CLI 工具
- [ ] Web 仪表板
- [ ] REST API 服务器
- [ ] 数据库集成
- [ ] 定时任务支持

---

## 尚未实现的功能

### ❌ 当前不支持

#### Billboard
- **历史数据**: Billboard 网站通过爬虫无法获取历史排行榜数据
  - 如需历史数据，建议使用 Billboard API（需要订阅）或第三方服务

#### Spotify
- **完整实现**: Spotify provider 仅为占位实现
  - 需要实现：OAuth 流程、API 调用、数据转换

#### 通用限制
- **实时更新**: 数据依赖于源网站的更新频率
- **所有排行榜**: 只支持主要排行榜，不支持所有子分类
- **完整元数据**: 某些信息可能不完整（如专辑名称在 Billboard 上不总是可用）

---

## 贡献指南

欢迎贡献！特别欢迎以下方面的贡献：

1. **新 Provider 实现**: 添加对新音乐平台的支持
2. **功能增强**: 改进现有功能
3. **Bug 修复**: 修复已知问题
4. **文档完善**: 改进文档和示例
5. **测试覆盖**: 添加更多测试用例

请参考项目的 CONTRIBUTING.md（待添加）了解详细的贡献流程。

---

## 许可证

MIT License

---

## 支持

- GitHub Issues: 报告 Bug 或请求新功能
- 文档: 查看完整文档和示例
- 示例: 参考 `examples/` 目录中的示例代码

---

**最后更新**: 2026-01-21  
**版本**: 0.2.0
