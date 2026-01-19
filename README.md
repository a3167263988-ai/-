# OKX 自动交易 + 复盘系统（Paper-First）

> **默认仅模拟盘**，实盘需要显式开启 `LIVE_TRADING_ENABLED=true`。

## 目标与边界
- LLM 只输出候选交易计划（JSON）+ 简短解释，不得直接下单。
- 下单只能由 Execution Engine 执行，并且必须通过 Risk Engine。
- 交易与复盘全链路审计入库（快照、信号、LLM 输出、风控裁决、订单、回执、成交、费用、滑点、退出原因等）。

## 架构概览
- **FastAPI**：控制面 API、手动风控开关、审计查询。
- **TimescaleDB/Postgres**：K 线、特征、审计、交易等数据。
- **Redis + Celery**：异步任务、数据采集、定时回放/复盘。
- **Prometheus + Grafana + Alertmanager**：监控告警。

### 数据流
```
市场数据/事件 -> Data Quality -> 特征 -> 信号 -> Regime/Uncertainty -> Planner(LLM/规则)
       -> Risk Engine(硬规则) -> Execution Engine -> 交易所回执/成交 -> 审计与复盘
```

## 目录结构
```
app/                        # FastAPI 入口
packages/                   # 业务模块
  adapters/                 # 新闻/Trends/链上适配器
  audit/                    # 审计落库
  common/                   # 配置、DB、日志
  data/                     # Data quality
  execution/                # 执行引擎 & 状态机
  planner/                  # 计划生成 & JSON Schema 校验
  regime/                   # 状态识别
  risk/                     # 风控引擎
  signals/                  # 信号提取
  tasks/                    # Celery 任务
infra/                      # Prometheus/Grafana/Alertmanager
migrations/                 # Alembic
examples/                   # 计划样例
```

## 快速开始（Docker Compose）
1. 复制环境文件：
   ```bash
   cp .env.example .env
   ```
2. 启动全栈：
   ```bash
   make up
   ```
3. 初始化数据库：
   ```bash
   make migrate
   ```
4. API 健康检查：
   ```bash
   curl http://localhost:8000/health
   ```

### 访问地址
- API: http://localhost:8000
- Grafana: http://localhost:3000（默认 admin/admin）
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093

## 风控关键参数（默认）
- 最大名义杠杆：100x
- 单笔最大亏损：10%（硬上限）
- 最大回撤：40% 自动暂停
- 必须带止损，否则拒绝
- 仓位由止损距离反推：
  ```
  notional_usd = equity * risk_budget_pct / (stop_distance_pct + fee_buffer_pct + slippage_buffer_pct)
  ```

## API 示例
- 生成计划（规则/LLM）：
  ```bash
  curl -X POST "http://localhost:8000/plans/generate?symbol=BTC-USDT&market_type=perp" \
    -H "X-API-Token: change_me"
  ```
- 执行计划（paper）：
  ```bash
  curl -X POST "http://localhost:8000/plans/execute" \
    -H "X-API-Token: change_me" \
    -H "Content-Type: application/json" \
    -d @examples/plan_trend.json
  ```
- 暂停/恢复开仓：
  ```bash
  curl -X POST "http://localhost:8000/risk/pause" -H "X-API-Token: change_me"
  curl -X POST "http://localhost:8000/risk/resume" -H "X-API-Token: change_me"
  ```

## 安全建议
- API Key 最小权限，仅限交易与读取。
- 建议开启 IP 白名单。
- 生产环境中请使用 Secrets 管理（不要提交密钥）。
- 日志默认脱敏（key/secret/token/password）。

## 服务器规格建议
- **常驻 CPU**：8 vCPU / 32GB 内存以上（行情/特征/多周期指标）。
- **GPU**：仅用于训练/推理 LLM/深度模型，可按需使用。

## 说明
- LLM 仅提供候选交易计划，最终执行必须通过风控裁决。
- 若外部数据源失败，系统会降级而不中断主流程。

