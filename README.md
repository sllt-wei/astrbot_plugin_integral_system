# astrbot_plugin_integral_system
astrbot积分系统插件，支持邀请好友、签到、兑换API Key等功能

---

## 插件功能

1. **签到积分**：用户每日签到可获得积分。
2. **邀请奖励**：邀请好友进群可获得额外积分。
3. **积分兑换**：使用积分兑换API Key或其他商品。
4. **商品管理**：管理员可添加或管理可兑换商品。

## 安装方法

1. 克隆插件仓库到 `AstrBot/data/plugins` 目录：
   ```bash
   git clone https://github.com/your-repo/astrbot_plugin_integral_system

2. 启动AstrBot，在插件管理界面启用本插件。

 使用说明
签到：发送 /sign_in 命令。
邀请好友：发送 /invite 命令（模拟）。
兑换商品：发送 /exchange <product_id> 命令。
添加商品（管理员）：发送 /add_product <product_id> <integral> 命令。
