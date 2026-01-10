# 样式系统快速参考

## 导入样式

```vue
<style lang="scss" scoped>
@use '@/styles/_variables.scss' as *;
@use '@/styles/_mixins.scss' as *;
</style>
```

## 颜色速查表

| 用途 | 变量 | 值 |
|------|------|-----|
| 主背景 | `$bg-primary` | #0B0E11 |
| 次背景 | `$bg-secondary` | #151A21 |
| 半透明背景 | `$bg-tertiary` | rgba(21, 26, 33, 0.7) |
| 主品牌色 | `$color-primary` | #2962FF |
| 品牌色浅 | `$color-primary-light` | #3D5AFE |
| 品牌色光晕 | `$color-primary-glow` | #1E88E5 |
| 主文字 | `$text-primary` | #EAECEF |
| 次文字 | `$text-secondary` | #E1E4E8 |
| 上涨 | `$color-up` | #2EBD85 |
| 下跌 | `$color-down` | #F6465D |

## 间距速查表

| 变量 | 值 |
|------|-----|
| `$spacing-xs` | 0.25rem (4px) |
| `$spacing-sm` | 0.5rem (8px) |
| `$spacing-md` | 1rem (16px) |
| `$spacing-lg` | 1.5rem (24px) |
| `$spacing-xl` | 2rem (32px) |
| `$spacing-2xl` | 2.5rem (40px) |

## 圆角速查表

| 变量 | 值 |
|------|-----|
| `$radius-sm` | 8px |
| `$radius-md` | 12px |
| `$radius-lg` | 16px |
| `$radius-xl` | 20px |
| `$radius-full` | 50% |

## 字体大小速查表

| 变量 | 值 |
|------|-----|
| `$font-size-xs` | 0.75rem |
| `$font-size-sm` | 0.875rem |
| `$font-size-base` | 1rem |
| `$font-size-lg` | 1.125rem |
| `$font-size-xl` | 1.5rem |
| `$font-size-2xl` | 1.75rem |
| `$font-size-3xl` | 2.5rem |

## Mixins 速查表

### 效果类

```scss
@include glass-effect();              // 玻璃拟态
@include hover-lift();                // 悬停提升
@include neon-glow(#2962FF);          // 霓虹发光
@include glow-border();               // 发光边框
```

### 布局类

```scss
@include flex-center();               // 弹性中心
@include flex-between();              // 弹性间距
@include responsive-grid();           // 响应式网格
@include absolute-center();           // 绝对居中
```

### 文字类

```scss
@include text-truncate();             // 单行截断
@include text-truncate-lines(3);      // 多行截断
@include gradient-text();             // 渐变文字
```

### 响应式类

```scss
@include responsive-font($mobile, $tablet, $desktop);
@include responsive-spacing($mobile, $tablet, $desktop);
```

### 动画类

```scss
@include transition(all, 0.3s, ease-in-out);
@include animation-delay(0.2s);
```

## 常见用法示例

### 卡片容器

```scss
.card {
  @include glass-effect();
  @include hover-lift();
  padding: $spacing-lg;
  border-radius: $radius-lg;
}
```

### 按钮

```scss
.button {
  padding: $spacing-md $spacing-lg;
  border-radius: $radius-sm;
  background: $color-primary;
  color: $text-primary;
  @include transition(all);
  
  &:hover {
    background: $color-primary-light;
    box-shadow: 0 0 12px rgba($color-primary, 0.4);
  }
}
```

### 标题

```scss
.title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  @include gradient-text();
  @include text-truncate();
}
```

### 响应式容器

```scss
.container {
  max-width: $max-width-container;
  margin: 0 auto;
  padding: $spacing-lg;
  
  @media (max-width: $breakpoint-md) {
    padding: $spacing-md;
  }
}
```

## 断点速查表

| 变量 | 值 |
|------|-----|
| `$breakpoint-sm` | 640px |
| `$breakpoint-md` | 768px |
| `$breakpoint-lg` | 1024px |
| `$breakpoint-xl` | 1280px |
| `$breakpoint-2xl` | 1536px |

## 过渡速查表

| 变量 | 值 |
|------|-----|
| `$transition-fast` | 0.2s |
| `$transition-base` | 0.3s |
| `$transition-slow` | 0.6s |
| `$easing-ease-out` | cubic-bezier(0.4, 0, 0.2, 1) |

