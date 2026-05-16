# 架构文档

## 项目架构

本项目采用模块化设计，将UI、业务逻辑、数据持久化和配置管理分离，以提高代码的可维护性和可扩展性。

## 目录结构

```
tools/
├── src/                      # 源代码
│   ├── core/                 # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── app.py           # 主应用类
│   │   └── models.py        # 数据模型
│   ├── ui/                   # UI相关
│   │   ├── __init__.py
│   │   ├── components/      # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── buttons.py   # 按钮组件
│   │   │   ├── icon_button.py # 图标按钮组件
│   │   │   ├── labels.py    # 标签组件
│   │   │   └── tooltips.py  # 提示框组件
│   │   └── styles/          # 样式管理
│   │       ├── __init__.py
│   │       ├── manager.py   # 样式管理器
│   │       └── themes/      # 主题
│   │           └── __init__.py
│   ├── persistence/          # 数据持久化
│   │   ├── __init__.py
│   │   └── file_handler.py  # 文件处理器
│   └── config/               # 配置管理
│       ├── __init__.py
│       └── settings.py      # 配置文件
├── tests/                    # 测试
│   ├── __init__.py
│   └── test_models.py       # 数据模型测试
├── docs/                     # 文档
│   └── ARCHITECTURE.md      # 架构文档
├── main.py                  # 应用程序入口
├── ui_styles.json           # UI样式配置
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

## 核心模块

### 1. 核心业务逻辑 (src/core/)

#### app.py
- **ImageMeasureApp**: 主应用类
  - 图片加载和管理
  - 测量功能（线段、角度、圆形、矩形、点到线距离、多边形面积）
  - 单位转换
  - 标注管理
  - 撤销/恢复功能

#### models.py
- **LineSegment**: 线段数据模型
- **AngleSegment**: 角度数据模型
- **CircleSegment**: 圆形数据模型（半径、直径、周长、面积）
- **RectangleSegment**: 矩形数据模型（边长、周长、面积）
- **PointToLineSegment**: 点到线距离数据模型
- **PolygonSegment**: 多边形数据模型（面积、周长）
- **MeasurementData**: 测量数据集合

### 2. UI模块 (src/ui/)

#### components/buttons.py
- **ModernButton**: 现代化按钮组件
  - 支持悬停效果
  - 支持子菜单
  - 响应式设计

#### components/labels.py
- **ResponsiveLabel**: 响应式标签组件

#### components/tooltips.py
- **ToolTip**: 提示框组件

#### styles/manager.py
- **StyleManager**: 样式管理器
  - 加载样式配置
  - 提供样式访问接口
  - 支持主题切换

### 3. 数据持久化 (src/persistence/)

#### file_handler.py
- **FileHandler**: 文件处理器
  - 加载/保存标注数据
  - 加载/保存项目文件
  - 导出CSV数据

### 4. 配置管理 (src/config/)

#### settings.py
- **Config**: 配置类
  - UI配置
  - 图片配置
  - 导出配置
  - 测量配置

## 数据流

```
用户操作
    ↓
UI组件 (src/ui/)
    ↓
主应用类 (src/core/app.py)
    ↓
数据模型 (src/core/models.py)
    ↓
文件处理器 (src/persistence/file_handler.py)
    ↓
文件系统
```

## 设计原则

1. **分离关注点**: UI、业务逻辑、数据持久化分离
2. **单一职责**: 每个模块只负责一个功能
3. **开闭原则**: 对扩展开放，对修改关闭
4. **依赖注入**: 通过构造函数注入依赖
5. **数据驱动**: 使用数据模型定义数据结构

## 扩展指南

### 添加新的测量类型

1. 在 `src/core/models.py` 中创建新的数据模型
2. 在 `src/core/app.py` 中添加测量逻辑
3. 在 UI 中添加相应的控制组件

### 添加新的导出格式

1. 在 `src/persistence/file_handler.py` 中添加导出方法
2. 在 UI 中添加导出选项
3. 更新配置文件

### 添加新的主题

1. 在 `src/ui/styles/themes/` 中创建主题文件
2. 在 `StyleManager` 中加载主题
3. 在 UI 中添加主题切换选项
