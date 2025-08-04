## 题目 1: 反向对称矩阵 (Toeplitz Matrix) 与向量的乘积

题目中定义的“反向对称矩阵”在数学上通常被称为 **托普利茨矩阵 (Toeplitz Matrix)**。其核心特征是每条从左上到右下的对角线上的元素都是常数。给定 $A_{i,j} = a_{n-1+i-j}$，这正是一个 $n \times n$ 托普利茨矩阵的定义。

朴素的矩阵向量乘法需要 $O(n^2)$ 的时间复杂度。然而，利用托普利茨矩阵的特殊结构，我们可以通过快速傅里叶变换 (FFT) 将计算加速，因为矩阵向量乘法可以被看作是一种卷积运算。 [1, 6, 7]

### 1. 算法设计 (伪代码)

设 $y = A \cdot v$，则其第 $i$ 个元素为：
$y_i = \sum_{j=0}^{n-1} A_{i,j} v_j = \sum_{j=0}^{n-1} a_{n-1+i-j} v_j$

这个求和的形式非常接近卷积。为了将其转化为标准的多项式乘法形式（卷积），我们可以进行一些变换。
令 $u_k = v_{n-1-k}$，即向量 $v$ 的逆序。
令 $c_k = a_{k}$，这是给定的压缩表示。
则原式可以改写为：
$y_i = \sum_{k=0}^{n-1} a_{i+k} u_k$
这个形式的计算结果 $y_i$ 对应于两个多项式乘积的特定系数。
具体来说，如果我们定义两个多项式：
$C(x) = \sum_{k=0}^{2n-2} a_k x^{2n-2-k}$
$U(x) = \sum_{k=0}^{n-1} u_k x^k$

它们的乘积 $P(x) = C(x) \cdot U(x)$ 中 $x^{2n-2-i}$ 项的系数恰好是 $\sum_{k=0}^{n-1} a_{i+k} u_k$，也就是我们要求的 $y_i$。

因此，我们可以利用基于 FFT 的快速多项式乘法来计算这个结果。

**伪代码:**

```plaintext
function ToeplitzVectorMultiply(a, v):
  // a: 压缩表示的数组，长度为 2n-1 (a_0, ..., a_{2n-2})
  // v: 输入向量，长度为 n (v_0, ..., v_{n-1})
  
  n = length(v)
  
  // 1. 构造用于多项式乘法的系数向量
  // C(x) 的系数向量 (a_{2n-2}, a_{2n-3}, ..., a_0)
  a_poly = reverse(a) 
  
  // U(x) 的系数向量 (u_0, ..., u_{n-1})，其中 u 是 v 的逆序
  // u = (v_{n-1}, v_{n-2}, ..., v_0)
  u_poly = reverse(v)

  // 2. 确定 FFT 的大小 N
  // N 必须是 2 的幂，并且大于等于两个多项式乘积的阶数
  // deg(C) = 2n-2, deg(U) = n-1, deg(P) = 3n-3
  // 所以 N >= (3n-3) + 1 = 3n-2
  N = smallest_power_of_2_greater_than(3n - 2)
  
  // 3. 对系数向量进行零填充
  a_padded = pad_with_zeros(a_poly, N)
  u_padded = pad_with_zeros(u_poly, N)
  
  // 4. 执行 FFT
  fft_a = FFT(a_padded)
  fft_u = FFT(u_padded)
  
  // 5. 在频域中进行逐点相乘
  fft_product = fft_a * fft_u  // Element-wise product
  
  // 6. 执行逆 FFT (IFFT) 转换回时域（系数域）
  product_coeffs = IFFT(fft_product)
  
  // 7. 提取结果
  // y_i 是 P(x) 中 x^{2n-2-i} 项的系数
  y = new_vector(n)
  for i from 0 to n-1:
    y[i] = product_coeffs[2n - 2 - i]
  
  return y


```
