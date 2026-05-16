# 图片测量工具

一个功能强大的图片测量工具，支持多种测量工具、多单位转换、批量导出等功能。

## 功能特性

- ✅ 线段测量
- ✅ 角度测量
- ✅ 圆形测量（半径、直径、周长、面积）
- ✅ 矩形测量（边长、周长、面积）
- ✅ 点到线距离测量
- ✅ 多边形面积测量
- ✅ 多单位支持（像素、毫米、厘米、英寸）
- ✅ 批量导出测量数据
- ✅ 项目保存/加载
- ✅ 响应式UI设计
- ✅ Microsoft Office风格界面
- ✅ 自动保存标注数据
- ✅ 撤销/恢复功能

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动程序

```bash
python main.py
```

### 快捷键

- `←` `→`：切换图片
- `空格`：完成当前测量
- `Delete`：删除选中项
- `Ctrl+Z`：撤销
- `Ctrl+Y`：恢复
- `鼠标滚轮`：缩放图片
- `右键`：撤销最后一个点

### 测量工具

1. **测量距离**：点击添加起点和终点，按空格键完成
2. **测量角度**：点击添加三个点（顶点、起点、终点），按空格键完成
3. **测量圆形**：点击添加圆心和圆周上一点，按空格键完成
4. **测量矩形**：点击添加两个对角点，按空格键完成
5. **点到线距离**：点击添加点和线段两端点，按空格键完成
6. **多边形测面积**：点击添加多个顶点，按空格键完成

## 项目结构

```
tools/
├── src/                      # 源代码
│   ├── core/                 # 核心业务逻辑
│   │   ├── app.py           # 主应用类
│   │   └── models.py        # 数据模型
│   ├── ui/                   # UI相关
│   │   ├── components/      # UI组件
│   │   │   ├── buttons.py   # 按钮组件
│   │   │   ├── icon_button.py # 图标按钮组件
│   │   │   ├── labels.py    # 标签组件
│   │   │   └── tooltips.py  # 提示框组件
│   │   └── styles/          # 样式管理
│   │       ├── manager.py   # 样式管理器
│   │       └── themes/      # 主题
│   ├── persistence/          # 数据持久化
│   │   └── file_handler.py  # 文件处理器
│   └── config/               # 配置管理
│       └── settings.py      # 配置文件
├── tests/                    # 测试
│   └── test_models.py       # 数据模型测试
├── docs/                     # 文档
│   └── ARCHITECTURE.md      # 架构文档
├── main.py                   # 主程序入口
├── ui_styles.json            # UI样式配置
└── requirements.txt          # 依赖列表
```

## 数据格式

### 标注数据格式

```json
{
  "segments": [
    {
      "points": [[x1, y1], [x2, y2]],
      "image_index": 0
    }
  ],
  "angles": [
    {
      "vertex_point": [x, y],
      "point1": [x1, y1],
      "point2": [x2, y2],
      "image_index": 0
    }
  ],
  "circles": [
    {
      "center": [x, y],
      "point_on_circle": [x1, y1],
      "image_index": 0
    }
  ],
  "rectangles": [
    {
      "points": [[x1, y1], [x2, y2]],
      "image_index": 0
    }
  ],
  "point_to_lines": [
    {
      "point": [x, y],
      "line_start": [x1, y1],
      "line_end": [x2, y2],
      "image_index": 0
    }
  ],
  "polygons": [
    {
      "points": [[x1, y1], [x2, y2], [x3, y3], ...],
      "image_index": 0
    }
  ]
}
```

## 开发建议

### 代码组织

1. **分离关注点**：将UI和业务逻辑分离
2. **使用数据模型**：使用 `dataclass` 定义数据结构
3. **配置管理**：将配置集中管理
4. **模块化设计**：将功能拆分为独立模块

### 扩展建议

1. **添加测试**：创建单元测试和集成测试
2. **添加文档**：完善API文档和用户手册
3. **插件系统**：支持自定义测量工具
4. **多语言支持**：添加国际化支持
5. **云同步**：支持云端数据同步

## 许可证

MIT License
