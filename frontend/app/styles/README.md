# 样式架构指南

## 目录结构

```
styles/
├── main.scss              # 全局样式入口
├── _variables.scss        # 通用的非颜色变量 (布局、圆角、字体大小)
├── _mixins.scss           # SCSS Mixins - 常用样式混合
└── themes/                # 主题定义文件夹
    ├── index.scss         # 汇总所有主题
    ├── base.scss          # 定义变量名（接口），提供默认值
    └── dark.scss          # 深色主题 - 深空量子蓝
```

## 使用指南

### 1. 在组件中导入样式

```vue
<style lang="scss" scoped>
@use '@/styles/_variables.scss' as *;
@use '@/styles/_mixins.scss' as *;

.my-component {
  padding: $spacing-lg;
  border-radius: $radius-md;
  @include glass-effect();
  @include hover-lift();
}
</style>
```

### 2. 使用颜色变量

```scss
// 背景色
background: $bg-primary;      // #0B0E11
background: $bg-secondary;    // #151A21
background: $bg-tertiary;     // rgba(21, 26, 33, 0.7)

// 品牌色
color: $color-primary;        // #2962FF
color: $color-primary-light;  // #3D5AFE

// 文字颜色
color: $text-primary;         // #EAECEF
color: $text-secondary;       // #E1E4E8

// 涨跌颜色
color: $color-up;             // #2EBD85
color: $color-down;           // #F6465D
```

### 3. 使用布局变量

```scss
// 间距
padding: $spacing-sm;   // 0.5rem
padding: $spacing-md;   // 1rem
padding: $spacing-lg;   // 1.5rem

// 圆角
border-radius: $radius-sm;    // 8px
border-radius: $radius-md;    // 12px
border-radius: $radius-lg;    // 16px

// 字体大小
font-size: $font-size-sm;     // 0.875rem
font-size: $font-size-base;   // 1rem
font-size: $font-size-lg;     // 1.125rem
```

### 4. 使用 Mixins

```scss
// 玻璃拟态效果
@include glass-effect();
@include glass-effect(0.8, 15px);  // 自定义透明度和模糊度

// 悬停效果
@include hover-lift();

// 响应式网格
@include responsive-grid(220px, 1.5rem);

// 弹性布局
@include flex-center();
@include flex-between();

// 文字截断
@include text-truncate();
@include text-truncate-lines(3);

// 渐变文字
@include gradient-text();
@include gradient-text(#FF0000, #00FF00);

// 过渡效果
@include transition(all, 0.3s, ease-in-out);
```

### 5. 添加新主题

1. 在 `themes/` 目录下创建新文件，如 `light.scss`
2. 定义所有必要的变量（参考 `base.scss`）
3. 在 `themes/index.scss` 中导入新主题

```scss
// themes/light.scss
$bg-primary: #FFFFFF;
$bg-secondary: #F5F5F5;
$text-primary: #1F2937;
// ... 其他变量
```

## 变量命名规范

- **背景色**: `$bg-*` (primary, secondary, tertiary, overlay)
- **品牌色**: `$color-*` (primary, primary-light, primary-glow)
- **文字色**: `$text-*` (primary, secondary, muted)
- **涨跌色**: `$color-*` (up, down)
- **边框色**: `$border-*` (color, color-light)
- **阴影色**: `$shadow-*`, `$glow-*`

## 最佳实践

1. **优先使用变量** - 不要硬编码颜色值
2. **使用 Mixins** - 减少重复代码
3. **响应式设计** - 使用 `$breakpoint-*` 变量
4. **一致的间距** - 使用 `$spacing-*` 变量
5. **保持主题一致** - 所有颜色都应该来自主题变量

## 迁移指南

如果你有旧的 CSS 文件，按以下步骤迁移：

1. 将硬编码的颜色替换为变量
2. 将重复的样式提取为 Mixins
3. 使用 `@use` 替代 `@import`
4. 在组件中导入必要的样式文件

