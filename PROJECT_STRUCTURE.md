# MChart 项目结构说明

本文档说明重构后的项目结构和架构设计。

## 📁 项目结构

```
mchart/
├── mchart/                    # 主包目录
│   ├── __init__.py           # 包初始化，导出公共API
│   ├── client.py             # MChart主客户端
│   ├── models.py             # 数据模型定义
│   ├── config/               # 配置模块
│   │   ├── __init__.py
│   │   ├── base.py          # 基础配置（TypedDict）
│   │   └── providers.py     # Provider特定配置
│   └── providers/            # Provider实现
│       ├── __init__.py
│       ├── base.py          # Provider基类和接口
│       ├── billboard.py     # Billboard实现
│       └── spotify.py       # Spotify占位实现
│
├── examples/                  # 使用示例
│   ├── fetch_billboard_hot100.py
│   ├── list_all_charts.py
│   ├── compare_charts.py
│   └── search_artist.py
│
├── docs/                      # 文档
│   └── API.md                # API完整文档
│
├── data/                      # 数据目录（生成）
│   └── billboard_hot100.json
│
├── pyproject.toml            # 项目配置
├── README.md                 # 项目说明
├── LICENSE                   # MIT许可证
└── .gitignore               # Git忽略配置
```

## 🏗️ 架构设计

### 1. 配置系统（TypedDict）

使用 TypedDict 而不是 Pydantic，让用户可以直接传入字典：

```python
# mchart/config/base.py
class BaseConfig(TypedDict, total=False):
    timeout: NotRequired[int]
    max_retries: NotRequired[int]
    # ...

# mchart/config/providers.py
class BillboardConfig(BaseConfig):
    parser: NotRequired[Literal["lxml", "html.parser"]]
    include_images: NotRequired[bool]
    # ...
```

**优势：**
- ✅ 用户可以直接传字典
- ✅ 保留类型提示
- ✅ 所有字段可选
- ✅ 易于扩展

### 2. 标准化Provider接口

所有provider继承 `BaseProvider` 并实现标准接口：

```python
# mchart/providers/base.py
class BaseProvider(ABC):
    @abstractmethod
    def get_latest(self, chart_name: str, **kwargs) -> Chart:
        pass
    
    @abstractmethod
    def get_chart(self, chart_name: str, chart_date: date, **kwargs) -> Chart:
        pass
    
    @abstractmethod
    def list_available_charts(self) -> list[ChartMetadata]:
        pass
```

**优势：**
- ✅ 统一的API
- ✅ 易于添加新provider
- ✅ 能力标志（ProviderCapability）
- ✅ 清晰的接口定义

### 3. 双返回格式支持

用户可以选择返回格式：

```python
# 返回字典（默认）- 适合JSON序列化
chart = client.get_chart("billboard", "hot-100")
# chart 是 dict[str, Any]

# 返回Pydantic模型 - 类型安全，有便捷方法
chart = client.get_chart("billboard", "hot-100", return_type="model")
# chart 是 Chart 对象
# chart.total_entries, chart.find_by_artist(), etc.
```

**优势：**
- ✅ 灵活性：适应不同使用场景
- ✅ JSON友好：字典格式直接序列化
- ✅ 类型安全：模型格式提供类型提示
- ✅ 开发者友好：无需强制导入内部类

### 4. 数据模型设计

使用Pydantic进行内部验证，提供转换方法：

```python
# mchart/models.py
class Chart(BaseModel):
    metadata: ChartMetadata
    published_date: date
    entries: list[ChartEntry]
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        data = self.model_dump()
        data["published_date"] = self.published_date.isoformat()
        return data
    
    # 便捷方法
    def get_top(self, n: int) -> list[ChartEntry]: ...
    def find_by_artist(self, artist: str) -> list[ChartEntry]: ...
```

**优势：**
- ✅ 内部数据验证
- ✅ 便捷的辅助方法
- ✅ 易于转换为字典

### 5. Billboard Provider优化

完整的HTML解析和数据提取：

```python
# mchart/providers/billboard.py
class BillboardProvider(BaseProvider):
    # 支持多个解析器
    # 完整的重试逻辑
    # 详细的数据提取
    # 支持多种排行榜
```

**特性：**
- ✅ 7种主要排行榜支持
- ✅ 完整的排名信息提取
- ✅ 可配置的解析器
- ✅ 重试和错误处理
- ✅ 图片URL提取

## 🔄 重构要点总结

### 1. 配置系统改进
- **之前**: Pydantic BaseModel
- **现在**: TypedDict
- **优势**: 更灵活，用户直接传字典

### 2. Provider分离
- **之前**: 混合在一个文件
- **现在**: 独立的provider模块
- **优势**: 清晰的职责，易于扩展

### 3. 返回格式
- **之前**: 只有Pydantic模型
- **现在**: 支持dict和model两种
- **优势**: 适应不同场景，降低使用门槛

### 4. 项目结构
- **之前**: 扁平结构，文件混杂
- **现在**: 模块化，职责清晰
- **优势**: 易于维护和扩展

### 5. 文档
- **之前**: 无文档
- **现在**: 完整的API文档、README、示例
- **优势**: 易于上手和使用

## 📋 代码规范

### 注释语言
- **代码注释**: 英文（面向全球开发者）
- **文档**: 中文+英文双语（API.md中文，代码注释英文）

### 类型提示
- 所有公共API使用类型提示
- 使用Python 3.10+的新语法（如 `list[str]` 而不是 `List[str]`）

### 配置
- 使用TypedDict定义配置结构
- 提供默认配置常量
- 所有配置项可选

## 🚀 使用场景

### 场景1: 简单脚本
```python
from mchart import MChart

client = MChart()
chart = client.get_chart("billboard", "hot-100")
# 使用字典，直接json.dump()
```

### 场景2: 类型安全应用
```python
from mchart import MChart, Chart

client = MChart()
chart: Chart = client.get_chart("billboard", "hot-100", return_type="model")
# 使用模型方法和类型提示
```

### 场景3: Web API
```python
from mchart import MChart
from fastapi import FastAPI

app = FastAPI()
client = MChart()

@app.get("/charts/{provider}/{chart_name}")
def get_chart(provider: str, chart_name: str):
    return client.get_chart(provider, chart_name)  # 直接返回dict
```

### 场景4: 数据分析
```python
from mchart import MChart
import pandas as pd

client = MChart()
chart = client.get_chart("billboard", "hot-100")

# 转换为DataFrame
df = pd.DataFrame(chart['entries'])
# 分析...
```

## 🔧 扩展指南

### 添加新Provider

1. 在 `mchart/providers/` 创建新文件
2. 继承 `BaseProvider`
3. 实现必需方法
4. 在 `mchart/config/providers.py` 添加配置类
5. 在 `mchart/client.py` 中注册

```python
# mchart/providers/apple_music.py
class AppleMusicProvider(BaseProvider):
    def get_latest(self, chart_name: str, **kwargs) -> Chart:
        # 实现...
        pass
```

### 添加新配置项

```python
# mchart/config/providers.py
class NewProviderConfig(BaseConfig):
    api_key: NotRequired[str]
    region: NotRequired[str]
```

## 📊 数据流

```
用户请求
    ↓
MChart Client
    ↓
Provider (Billboard/Spotify/...)
    ↓
HTTP请求 → HTML/JSON解析
    ↓
Pydantic模型验证
    ↓
[可选] 转换为dict
    ↓
返回给用户
```

## 🎯 设计原则

1. **简单优先**: API设计简洁，开箱即用
2. **灵活配置**: 通过配置适应不同需求
3. **类型安全**: 完整的类型提示
4. **可扩展**: 标准化接口，易于添加新provider
5. **用户友好**: 支持字典和模型两种格式
6. **文档完善**: 详细的文档和示例

---

**版本**: 0.2.0  
**最后更新**: 2026-01-18
