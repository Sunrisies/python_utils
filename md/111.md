## 附录B：运算符与符号

本附录包含了Rust语法的术语表，其中包括单独出现的运算符以及其他符号，这些符号可能出现在路径、泛型、特质约束、宏、属性、注释、元组以及方括号等上下文中。

### 运算符

表B-1列出了Rust中的运算符，展示了这些运算符在上下文中的使用示例，以及简要的解释，还说明了这些运算符是否可以被重载。如果某个运算符可以被重载，则还会列出用于重载该运算符的相关特性。

<span class="caption">表B-1：运算符</span>

| 运算符 | 示例 | 说明 | 可重载的吗？ |
| ------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------- | -------------- |
| `!` | `ident!(...)`, `ident!{...}`, `ident![...]` | 宏扩展 |  |
| `!` | `!expr` | 位或逻辑补码 | `Not` |
| `!=` | `expr != expr` | 不等比较 | `PartialEq` |
| `%` | `expr % expr` | 算术余数 | `Rem` |
| `%=` | `var %= expr` | 算术余数与赋值 | `RemAssign` |
| `&` | `&expr`, `&mut expr` | 借用 |  |
| `&` | `&type`, `&mut type`, `&'a type`, `&'a mut type` | 借用指针类型 |  |
| `&` | `expr & expr` | 位运算与 | `BitAnd` |
| `&=` | `var &= expr` | 位运算与赋值 | `BitAndAssign` |
| `&&` | `expr && expr` | 短路逻辑与运算 |  |
| `*` | `expr * expr` | 算术乘法 | `Mul` |
| `*=` | `var *= expr` | 算术乘法与赋值 | `MulAssign` |
| `*` | `*expr` | 解引用 | `Deref` |
| `*` | `*const type`, `*mut type` | 原始指针 |  |
| `+` | `trait + trait`, `'a + trait` | 复合类型约束 |  |
| `+` | `expr + expr` | 算术加法 | `Add` |
| `+=` | `var += expr` | 算术加法与赋值 | `AddAssign` |
| `,` | `expr, expr` | 参数与元素分隔符 |  |
| `-` | `- expr` | 算术否定 | `Neg` |
| `-` | `expr - expr` | 算术减法 | `Sub` |
| `-=` | `var -= expr` | 算术减法与赋值 | `SubAssign` |
| `->` | `fn(...) -> type`, <code>&vert;...&vert; -> 类型</code> | 函数与闭包的返回类型 |  |
| `.` | `expr.ident` | 字段访问 |  |
| `.` | `expr.ident(expr, ...)` | 方法调用 |  |
| `.` | `expr.0`、`expr.1`等 | 元组索引 |  |
| `..` | `..`, `expr..`, `..expr`, `expr..expr` | 右排除范围字面量 | `PartialOrd` |
| `..=` | `..=expr`, `expr..=expr` | 右包含范围字面量 | `PartialOrd` |
| `..` | `..expr` | 结构体字面量更新语法 |  |
| `..` | `variant(x, ..)`, `struct_type { x, .. }` | “And the rest” 模式绑定 |  |
| `...` | `expr...expr` | （已弃用，请使用`..=`代替）在模式中：包含范围模式 |  |
| `/` | `expr / expr` | 算术除法 | `Div` |
| `/=` | `var /= expr` | 算术除法与赋值 | `DivAssign` |
| `:` | `pat: type`, `ident: type` | 约束条件 |  |
| `:` | `ident: expr` | 结构体字段初始化器 |  |
| `:` | `'a: loop {...}` | 循环标签 |  |
| `;` | `expr;` | 语句和项目终止符 |  |
| `;` | `[...; len]` | 固定大小数组语法的一部分 |  |
| `<<` | `expr << expr` | 左移 | `Shl` |
| `<<=` | `var <<= expr` | 左移和赋值 | `ShlAssign` |
| `<` | `expr < expr` | 比比较值小 | `PartialOrd` |
| `<=` | `expr <= expr` | 小于等于比较 | `PartialOrd` |
| `=` | `var = expr`, `ident = type` | 赋值/等价 |  |
| `==` | `expr == expr` | 相等性比较 | `PartialEq` |
| `=>` | `pat => expr` | 匹配臂语法的一部分 |  |
| `>` | `expr > expr` | 大于比较 | `PartialOrd` |
| `>=` | `expr >= expr` | 大于或等于的比较 | `PartialOrd` |
| `>>` | `expr >> expr` | 右移 | `Shr` |
| `>>=` | `var >>= expr` | 右移和赋值 | `ShrAssign` |
| `@` | `ident @ pat` | 模式绑定 |  |
| `^` | `expr ^ expr` | 位异或运算 | `BitXor` |
| `^=` | `var ^= expr` | 位异或运算与赋值 | `BitXorAssign` |
| <code>&vert;</code> | <code>pat &vert; pat</code> | 模式替代方案 |  |
| <code>&vert;</code> | <code>表达式 &vert; 另一个表达式</code> | 位运算或 | `BitOr` |
| <code>&vert;=</code> | <code>var &vert; = expr</code> | 位运算与赋值 | `BitOrAssign` |
| <code>&vert;&vert;</code> | <code>表达式 &vert;&vert; 另一个表达式</code> | 短路逻辑或 |  |
| `?` | `expr?` | 错误传播 |  |
### 非运算符符号

以下表格包含了所有不能作为运算符的符号；也就是说，它们并不像函数或方法调用那样起作用。

表B-2列出了那些可以独立出现且在多种情况下都有效的符号。

<span class="caption">表B-2：独立语法结构</span>

表B-3展示了在通过模块层次结构访问某个项目时出现的符号。

<span class="caption">表B-3：与路径相关的语法</span>

表B-4列出了在使用泛型类型参数时出现的符号。

<span class="caption">表B-4：泛型</span>

表B-5列出了在限制泛型类型参数与特质边界相关的上下文中出现过的符号。

<span class="caption">表B-5： trait绑定约束</span>

表B-6列出了在调用宏、定义宏以及指定项目属性时出现的符号。

<span class="caption">表B-6：宏与属性</span>

表B-7列出了用于创建注释的符号。

<span class="caption">表B-7：注释</span>

表B-8展示了使用括号的各种情境。

<span class="caption">表B-8：圆括号</span>

表B-9展示了使用花括号的各种情境。

<span class="caption">表B-9：花括号</span>

表B-10展示了方括号被使用的各种情境。

<span class="caption">表B-10：方括号</span>

| 上下文 | 说明 |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `[...]` | 数组字面量 |
| `[expr; len]` | 包含 `expr` 的 `len` 个副本的数组字面量 |
| `[type; len]` | 包含 `type` 实例的数组类型，其中每个实例都是 `len` |
| `expr[expr]` | 集合索引；可重载的(`Index`, `IndexMut`) |
| `expr[..]`, `expr[a..]`, `expr[..b]`, `expr[a..b]` | 集合索引实际上相当于集合切片操作，使用 ``Range``、``RangeFrom``、``RangeTo`` 或 ``RangeFull`` 作为“索引”。 |