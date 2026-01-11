# 快速启动指南

## 项目概述

这是一个从Vue.js迁移到React的**股票异动监控系统**。该项目使用现代化的技术栈，包括React 18+、TypeScript、Vite和Arco Design组件库。

## 已完成的工作

✅ **项目配置**
- Vite + React 18 + TypeScript 5.9
- 路径别名配置 (`@/` 指向 `src/`)
- API代理配置 (转发到 `http://127.0.0.1:5000`)
- ESLint + TypeScript 严格模式

✅ **样式系统**
- 模块化SCSS架构
- 深空量子蓝配色方案
- 深色/浅色主题支持
- 响应式设计

✅ **核心功能**
- 7个React组件（ThemeToggle、InfoBox、Changelog、Watermark、StockTable、TPlusCard、EditModal）
- 2个页面（首页、信息页面）
- Zustand状态管理
- React Router v6路由
- 自定义Hooks（useTheme）
- API工具函数

## 快速开始

### 1. 安装依赖（如果还未安装）

```bash
cd react-frontend
pnpm install
```

### 2. 启动开发服务器

```bash
pnpm dev
```

应用将在 `http://127.0.0.1:3000` 启动

### 3. 构建生产版本

```bash
pnpm build
```

### 4. 预览生产版本

```bash
pnpm preview
```

## 项目结构

```
src/
├── components/          # React 组件
├── pages/               # 页面组件
├── hooks/               # 自定义 Hooks
├── stores/              # Zustand 状态管理
├── utils/               # 工具函数
├── styles/              # 全局样式
├── App.tsx              # 主应用组件
└── main.tsx             # 应用入口
```

## 主要特性

- 📊 **股票数据展示** - 10日和30日偏离值榜单
- 🎨 **主题切换** - 深色/浅色模式
- 📱 **响应式设计** - 完美适配各种屏幕
- 🔄 **实时数据更新** - 从后端API获取
- 📝 **更新日志** - 查看系统更新历史
- ⚡ **高性能** - Zustand状态管理

## 路由配置

- `/` - 首页（股票异动监控）
- `/info` - 信息页面（个人名片）

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.2.0 | UI框架 |
| TypeScript | 5.9.3 | 类型检查 |
| Vite | 7.2.4 | 构建工具 |
| Arco Design | 2.57.0 | UI组件库 |
| Zustand | 4.4.1 | 状态管理 |
| React Router | 6.20.0 | 路由管理 |
| Axios | 1.13.2 | HTTP客户端 |
| SCSS | 1.69.5 | 样式预处理 |

## 环境要求

- Node.js >= 16
- pnpm >= 8

## 常见问题

### Q: 如何修改API地址？
A: 在 `vite.config.ts` 中修改 `server.proxy['/api'].target`

### Q: 如何修改主题颜色？
A: 在 `src/styles/_variables.scss` 中修改颜色变量

### Q: 如何添加新的页面？
A: 在 `src/pages/` 中创建新的 `.tsx` 文件，然后在 `App.tsx` 中添加路由

## 下一步

1. 启动后端服务器（Flask应用）
2. 运行 `pnpm dev` 启动前端
3. 访问 `http://127.0.0.1:3000` 查看应用

## 许可证

MIT

