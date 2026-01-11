# 股票异动监控系统 - React 版本

这是一个从Vue.js迁移到React的股票异动监控系统。使用React 18+、TypeScript、Vite和Arco Design组件库构建。

## 功能特性

- 📊 **股票数据展示** - 10日和30日偏离值榜单
- 🎨 **主题切换** - 支持深色/浅色模式
- 📱 **响应式设计** - 完美适配各种屏幕尺寸
- 🔄 **实时数据更新** - 从后端API获取最新数据
- 📝 **更新日志** - 查看系统更新历史
- ⚡ **高性能** - 使用Zustand进行状态管理

## 技术栈

- **框架**: React 18+
- **语言**: TypeScript
- **构建工具**: Vite
- **UI组件库**: @arco-design/web-react
- **状态管理**: Zustand
- **路由**: React Router v6
- **样式**: SCSS
- **HTTP客户端**: Axios

## 项目结构

```
src/
├── components/          # React 组件
│   ├── ThemeToggle.tsx  # 主题切换按钮
│   ├── InfoBox.tsx      # 信息提示框
│   ├── Changelog.tsx    # 更新日志
│   ├── Watermark.tsx    # 水印组件
│   ├── StockTable.tsx   # 股票表格
│   ├── TPlusCard.tsx    # T+n 数据卡片
│   └── EditModal.tsx    # 编辑模态框
├── pages/               # 页面组件
│   ├── Home.tsx         # 首页
│   └── Info.tsx         # 信息页面
├── hooks/               # 自定义 Hooks
│   └── useTheme.ts      # 主题管理 Hook
├── stores/              # Zustand 状态管理
│   └── stockStore.ts    # 股票数据 Store
├── utils/               # 工具函数
│   └── api.ts           # API 请求工具
├── styles/              # 全局样式
│   ├── main.scss        # 全局样式入口
│   ├── _variables.scss  # 样式变量
│   └── _mixins.scss     # 样式混合
├── App.tsx              # 主应用组件
└── main.tsx             # 应用入口
```

## 快速开始

### 安装依赖

```bash
cd react-frontend
pnpm install
```

### 开发模式

```bash
pnpm dev
```

应用将在 `http://127.0.0.1:3000` 启动

### 构建生产版本

```bash
pnpm build
```

### 预览生产版本

```bash
pnpm preview
```

## API 配置

项目已配置API代理，将 `/api` 请求转发到 `http://127.0.0.1:5000`

在 `vite.config.ts` 中配置：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true,
      rewrite: (path) => path
    }
  }
}
```

## 主题系统

项目支持深色/浅色主题切换，使用CSS变量实现：

- **亮色主题**: 白色背景，深色文字
- **深色主题**: 深空量子蓝配色方案

主题偏好保存在 `localStorage` 中，支持系统主题检测。

## 样式架构

采用模块化SCSS系统：

- `_variables.scss` - 布局变量（间距、圆角、字体等）
- `_mixins.scss` - 常用样式混合（玻璃拟态、悬停效果等）
- `main.scss` - 全局样式入口
- 各组件独立的 `.scss` 文件

## 状态管理

使用Zustand管理股票数据：

```typescript
const stockStore = useStockStore()
stockStore.fetchBothStocks()  // 获取数据
stockStore.sortedStocks10     // 10日排序数据
stockStore.sortedStocks30     // 30日排序数据
```

## 路由配置

- `/` - 首页（股票异动监控）
- `/info` - 信息页面（个人名片）

## 响应式设计

项目使用响应式设计，支持以下断点：

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

## 浏览器支持

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

## 许可证

MIT

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
