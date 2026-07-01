# NQE Workflow Skills 仓库现状报告

## 整体成熟度：教学就绪 (Teaching-Ready)

仓库已建成一个结构化的教学示例骨架，包含 12 个 skill，覆盖 NQE H2 workflow 全链路。

## ✅ 已经做好的

| 维度 | 现状 |
|---|---|
| **技能覆盖** | 12 个 skill，从 NQE 基础 → DFT → DP-GEN → DeePMD → CHMC/CPIHMC → TI/TST → KMC 全链路 |
| **测试体系** | `tests/manual_prompts.md` 含 smoke + failure + 完整测试，所有 28 个测试已通过验证 |
| **脚本** | 13 个可执行脚本（TI/TST 链、DeePMD 诊断、dpdata 转换、文件检查、后处理编排） |
| **模板** | 19 个模板，统一使用 `TODO_USER_APPROVAL` 占位符 |
| **引用文档** | 各 skill 带 official-notes 和 checklist |
| **边界防护** | 所有 skill 强制要求用户确认参数，拒绝自行编造数值 |

## ⚠️ 仍需完善的小问题

- **2 个断裂引用**：`initial-dft-dataset/SKILL.md:68` 和 `kmc-h2-efficiency/SKILL.md:78` 指向不存在的文件
- **8/9 failure-cases 为空**：仅存占位符 TODO 文件
- **无真正的 production 工作流文件**：所有数值都是占位符

## 🏭 可替代的人工操作

### 1. 数据后处理（完全替代）

| 操作 | 原人工方式 | 现脚本 |
|---|---|---|
| 从 CHMC/CPIHMC 输出提取平均力 | 打开文件、找列、复制数据 | `extract_mean_force.py` |
| TI 积分得到自由能势能面 | Excel/手算积分 | `integrate_free_energy.py` |
| 从自由能面计算 TST 速率常数 | 代入公式 k = pref·exp(-ΔF/kT) | `compute_tst_rates.py` |
| 编排完整后处理链 | 按顺序手动运行 3 个脚本 | `nqe_postprocess_runner.py` |
| 解析 DeePMD 训练日志 | 打开 lcurve.out 逐列看 | `parse_lcurve.py` |
| 文件格式完整性检查 | 肉眼核对文件结构 | `check_workflow_files.py` |
| ABACUS ↔ DeePMD 数据转换 | 手动 dpdata 命令 | `convert_with_dpdata.py` |
| 绘图（平均力、自由能曲线） | 手动 matplotlib | `plot_mean_force.py` / `plot_free_energy.py` |

### 2. 知识问答/指导（部分替代）

加载这些 skill 的 AI agent 可替代**初级导师/文档查阅**角色：
- 回答 "下一步该做什么" 的工作流问题
- 给出每个 stage 的 checklist
- 纠正概念错误（如 "CPIHMC 输出可以直接算效率吗 → 否"）
- 拒绝编造参数并要求用户确认
- 协助编写/检查配置文件结构（ABACUS INPUT、DP-GEN param.json、LAMMPS input 等）

### 3. 🚫 不能替代的（仍需人工）

- **所有计算任务**：ABACUS DFT、DP-GEN 循环、LAMMPS 探索、DeePMD 训练、CHMC/CPIHMC 采样
- **物理判断**：反应坐标定义、信任阈值选取、收敛性判断、RC 符号约定、prefactor 模型选择
- **数值设定**：k 点、截断能、赝势、系综参数、温度、步长等

## 💡 对实际生产的帮助

作为教学参考，仓库的核心价值是：

1. **工作流设计蓝图** — 12 个 stage 的上下游依赖关系、每个 stage 的输入/输出/需确认参数，可直接映射到真实项目
2. **脚本可用** — `extract_mean_force.py` → `integrate_free_energy.py` → `compute_tst_rates.py` 加上 `nqe_postprocess_runner.py` 编排，经过参数确认后可直接用于真实数据
3. **checklist 模板** — 每个 skill 的 checklist 和 failure-cases 可复用为真实项目的质量门禁
4. **代理测试套件** — `tests/manual_prompts.md` 可作为评估 AI agent 在科研工作流中行为规范的质量标准

**目前还不是生产即用型管线**，但已经是一个结构完备、可扩展的教学参考框架。
