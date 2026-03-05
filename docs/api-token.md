# Star Office UI API Token 鉴权文档

## 概述

Star Office UI 提供了一套完整的 API Token 鉴权机制，用于安全地管理 API 访问权限。

## Token 类型

### 1. Admin Token
- **用途**：管理所有 API Token（生成、撤销、列表）
- **文件位置**：
  - Docker：`/app/admin-token.json`
  - 开发环境：`backend/admin-token.json`

### 2. API Token
- **用途**：用于普通 API 访问验证
- **文件位置**：
  - Docker：`/app/api-tokens.json`
  - 开发环境：`backend/api-tokens.json`

## API 接口

### Token 管理接口

| 接口 | 方法 | 功能 | 鉴权方式 |
|------|------|------|----------|
| `/api/v1/admin/token` | GET | 获取 Admin Token 状态 | X-Admin-Token |
| `/api/v1/admin/token` | POST | 轮换 Admin Token | X-Admin-Token |
| `/api/v1/admin/token/generate` | POST | 生成新的 API Token | X-Admin-Token |
| `/api/v1/admin/tokens` | GET | 列出所有 API Token | X-Admin-Token |
| `/api/v1/admin/token/<token>` | DELETE | 撤销指定的 API Token | X-Admin-Token |

## 请求头说明

| 请求头 | 说明 | 示例 |
|--------|------|------|
| `X-Admin-Token` | Admin 管理 Token | `X-Admin-Token: your-admin-token` |
| `X-API-Token` | 普通 API Token | `X-API-Token: your-api-token` |

## 使用示例

### 1. 获取 Admin Token 状态

```bash
curl http://localhost/api/v1/admin/token \
  -H "X-Admin-Token: your-admin-token"
```

响应：
```json
{
  "success": true,
  "has_admin_token": true
}
```

### 2. 生成新的 API Token

```bash
curl -X POST http://localhost/api/v1/admin/token/generate \
  -H "X-Admin-Token: your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"name":"我的Token"}'
```

响应：
```json
{
  "success": true,
  "token": "HkCboIC8fcKSsy4QOH3l6EMOhr6Q_0PFYNwSUfyAg1w",
  "name": "我的Token",
  "created_at": "2026-03-05T01:02:59.045464"
}
```

### 3. 列出所有 API Token

```bash
curl http://localhost/api/v1/admin/tokens \
  -H "X-Admin-Token: your-admin-token"
```

响应：
```json
{
  "success": true,
  "tokens": [
    {
      "name": "我的Token",
      "created_at": "2026-03-05T01:02:59.045464",
      "enabled": true,
      "token_preview": "HkCboIC8..."
    }
  ]
}
```

### 4. 撤销 Token

```bash
curl -X DELETE http://localhost/api/v1/admin/token/HkCboIC8fcKSsy4QOH3l6EMOhr6Q_0PFYNwSUfyAg1w \
  -H "X-Admin-Token: your-admin-token"
```

响应：
```json
{
  "success": true,
  "message": "Token revoked"
}
```

### 5. 轮换 Admin Token

```bash
curl -X POST http://localhost/api/v1/admin/token \
  -H "X-Admin-Token: your-admin-token"
```

响应：
```json
{
  "success": true,
  "admin_token": "new-admin-token-here"
}
```

## 当前部署的 Token

| 类型 | Token | 说明 |
|------|-------|------|
| Admin | `-Zac0PZEARxyLCxgHL-nW752ta9dHPYGIDWN9r5inq4` | 主 Admin Token |
| API | `HkCboIC8fcKSsy4QOH3l6EMOhr6Q_0PFYNwSUfyAg1w` | 测试 Token |

## 安全建议

1. **妥善保管 Token**：Admin Token 具有最高权限，请勿泄露
2. **定期轮换**：建议定期更换 Admin Token
3. **最小权限原则**：根据需要生成不同的 API Token，避免共用
4. **生产环境注意**：
   - 修改默认的 Admin Token
   - 使用强密码策略
   - 限制 Token 的有效期

## 错误响应

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 缺少必要的 Token 请求头 |
| 403 | Token 验证失败 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

错误响应示例：
```json
{
  "error": "Missing X-Admin-Token header"
}
```
