# Release Notes - v0.2.0

**发布日期 / Release Date**: 2026-01-21  
**版本 / Version**: 0.2.0

---

[English](#english) | [中文](#中文)

---

## 中文

### 🎉 新功能

#### 专辑榜单支持

v0.2.0 引入了对专辑榜单的完整支持，这是本版本的主要功能更新。

##### 核心改进

1. **ChartMetadata 类型字段**
   - 新增 `type` 字段，用于区分单曲榜（`"single"`）和专辑榜（`"album"`）
   - 自动根据榜单名称识别类型

2. **ChartEntry 专辑支持**
   - 新增 `album` 字段，用于专辑榜单条目
   - 保持向后兼容，单曲榜继续使用 `song` 字段
   - 数据验证确保每个条目只能包含 `song` 或 `album` 之一

3. **Album 数据模型**
   - 新增 `Album` 模型，包含专辑标题、艺术家、封面图片等信息
   - 与 `Song` 模型结构相似，但针对专辑数据优化

4. **Billboard 200 支持**
   - 完整支持 Billboard 200 专辑榜单
   - 自动识别专辑榜单并使用专门的解析方法
   - 正确提取专辑信息、排名数据等

##### 使用示例

**获取专辑榜：**
```python
from mchart import MChart

client = MChart()
chart = client.get_chart("billboard", "billboard-200")

# 检查榜单类型
print(chart["metadata"]["type"])  # "album"

# 访问专辑信息
for entry in chart["entries"][:10]:
    album = entry["album"]  # 专辑榜使用 album 字段
    print(f"#{entry['rank']} - {album['title']} by {album['artist']}")
```

**使用 Pydantic 模型：**
```python
chart = client.get_chart("billboard", "billboard-200", return_type="model")

# 查找特定艺术家的专辑
albums = chart.find_by_artist("Taylor Swift")
for entry in albums:
    print(f"#{entry.rank} - {entry.album.title}")
```

### 📚 文档更新

- ✅ 更新 API 文档，详细说明专辑榜的使用方法
- ✅ 添加 `ChartMetadata.type` 字段说明
- ✅ 添加 `ChartEntry.album` 字段说明
- ✅ 添加 `Album` 模型文档
- ✅ 添加专辑榜和单曲榜的使用示例

### 🧪 测试

- ✅ 创建完整的测试套件（43个测试用例）
- ✅ 测试覆盖数据模型、客户端和 Billboard provider
- ✅ 所有测试通过（43 passed）

### 🔧 技术细节

#### 数据模型变更

- `ChartMetadata`: 新增 `type: Literal["single", "album"]` 字段
- `ChartEntry`: 新增 `album: Optional[Album]` 字段
- 新增 `Album` 模型类

#### Billboard Provider 改进

- 自动识别专辑榜单（`billboard-200`）
- 实现 `_parse_album_entries()` 方法专门解析专辑榜单
- 根据榜单类型自动选择解析方法
- 更新 `list_available_charts()` 方法，为每个榜单设置正确的 `type` 字段

### 🔄 向后兼容性

- ✅ 完全向后兼容，现有单曲榜功能不受影响
- ✅ 单曲榜继续使用 `song` 字段
- ✅ 所有现有代码无需修改即可继续工作

### 📦 示例代码

新增示例文件：
- `examples/fetch_billboard_200.py` - 演示如何获取和使用 Billboard 200 专辑榜单

### 🐛 Bug 修复

无重大 bug 修复（本版本主要专注于新功能）

### 📝 其他改进

- 改进错误处理和验证
- 优化代码结构
- 增强类型提示

### 🔜 下一步计划

- Spotify Provider 实现
- 更多专辑榜单支持
- 异步 API 支持
- 缓存机制

---

## English

### 🎉 New Features

#### Album Chart Support

v0.2.0 introduces full support for album charts, the main feature update of this release.

##### Core Improvements

1. **ChartMetadata Type Field**
   - Added `type` field to distinguish between single charts (`"single"`) and album charts (`"album"`)
   - Automatically identifies type based on chart name

2. **ChartEntry Album Support**
   - Added `album` field for album chart entries
   - Maintains backward compatibility, single charts continue to use `song` field
   - Data validation ensures each entry contains either `song` or `album`, but not both

3. **Album Data Model**
   - New `Album` model containing album title, artist, cover image, etc.
   - Similar structure to `Song` model but optimized for album data

4. **Billboard 200 Support**
   - Full support for Billboard 200 album chart
   - Automatically identifies album charts and uses specialized parsing method
   - Correctly extracts album information, ranking data, etc.

##### Usage Examples

**Fetch Album Chart:**
```python
from mchart import MChart

client = MChart()
chart = client.get_chart("billboard", "billboard-200")

# Check chart type
print(chart["metadata"]["type"])  # "album"

# Access album information
for entry in chart["entries"][:10]:
    album = entry["album"]  # Album charts use album field
    print(f"#{entry['rank']} - {album['title']} by {album['artist']}")
```

**Using Pydantic Models:**
```python
chart = client.get_chart("billboard", "billboard-200", return_type="model")

# Find albums by specific artist
albums = chart.find_by_artist("Taylor Swift")
for entry in albums:
    print(f"#{entry.rank} - {entry.album.title}")
```

### 📚 Documentation Updates

- ✅ Updated API documentation with detailed album chart usage instructions
- ✅ Added `ChartMetadata.type` field documentation
- ✅ Added `ChartEntry.album` field documentation
- ✅ Added `Album` model documentation
- ✅ Added usage examples for both album and single charts

### 🧪 Testing

- ✅ Created comprehensive test suite (43 test cases)
- ✅ Tests cover data models, client, and Billboard provider
- ✅ All tests passing (43 passed)

### 🔧 Technical Details

#### Data Model Changes

- `ChartMetadata`: Added `type: Literal["single", "album"]` field
- `ChartEntry`: Added `album: Optional[Album]` field
- New `Album` model class

#### Billboard Provider Improvements

- Automatically identifies album charts (`billboard-200`)
- Implemented `_parse_album_entries()` method specifically for parsing album charts
- Automatically selects parsing method based on chart type
- Updated `list_available_charts()` method to set correct `type` field for each chart

### 🔄 Backward Compatibility

- ✅ Fully backward compatible, existing single chart functionality unaffected
- ✅ Single charts continue to use `song` field
- ✅ All existing code works without modification

### 📦 Example Code

New example file:
- `examples/fetch_billboard_200.py` - Demonstrates how to fetch and use Billboard 200 album chart

### 🐛 Bug Fixes

No major bug fixes (this release focuses primarily on new features)

### 📝 Other Improvements

- Improved error handling and validation
- Optimized code structure
- Enhanced type hints

### 🔜 Next Steps

- Spotify Provider implementation
- Support for more album charts
- Async API support
- Caching mechanism

---

**完整变更列表 / Full Changelog**: 查看 [docs/v0.2.0_TODOS.md](docs/v0.2.0_TODOS.md)

**API 文档 / API Documentation**: 查看 [docs/API.md](docs/API.md)
