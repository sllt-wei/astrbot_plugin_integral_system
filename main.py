from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import json
import os

@register("integral_system", "YourName", "积分系统插件", "1.0.0", "repo_url")
class IntegralSystem(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_dir = os.path.join("data", "integral_system")
        os.makedirs(self.data_dir, exist_ok=True)
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.api_keys_file = os.path.join(self.data_dir, "api_keys.json")
        self.products_file = os.path.join(self.data_dir, "products.json")
        self.load_data()

    def load_data(self):
        """加载用户数据、API Key和商品数据"""
        self.users = self._load_json(self.users_file, {})
        self.api_keys = self._load_json(self.api_keys_file, {})
        self.products = self._load_json(self.products_file, {})

    def _load_json(self, file_path, default):
        """从JSON文件加载数据"""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save_json(self, file_path, data):
        """保存数据到JSON文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @filter.contains("签到")
    async def sign_in(self, event: AstrMessageEvent):
        """签到功能"""
        user_id = event.get_sender_id()
        if user_id not in self.users:
            self.users[user_id] = {"integral": 0, "last_sign_in": None}
        
        # 检查是否已签到
        if self.users[user_id].get("last_sign_in") == str(event.timestamp):
            yield event.plain_result("您今天已经签到过了！")
            return
        
        # 签到奖励
        self.users[user_id]["integral"] += 10
        self.users[user_id]["last_sign_in"] = str(event.timestamp)
        self._save_json(self.users_file, self.users)
        yield event.plain_result(f"签到成功！获得10积分，当前积分：{self.users[user_id]['integral']}")

    @filter.group_member_increased()
    async def member_join(self, event: AstrMessageEvent):
        """新成员加入群组"""
        operator_id = event.message_obj.raw_message.get("operator_id")
        if operator_id and operator_id != event.get_self_id():
            if operator_id not in self.users:
                self.users[operator_id] = {"integral": 0}
            
            self.users[operator_id]["integral"] += 20
            self._save_json(self.users_file, self.users)
            yield event.send_private(
                operator_id,
                f"您邀请的好友已入群，获得20积分！当前积分：{self.users[operator_id]['integral']}"
            )

    @filter.command("exchange")
    async def exchange_api_key(self, event: AstrMessageEvent, product_id: str):
        """兑换API Key"""
        user_id = event.get_sender_id()
        if user_id not in self.users:
            yield event.plain_result("您还没有积分，请先签到或邀请好友！")
            return
        
        if product_id not in self.products:
            yield event.plain_result("商品不存在！")
            return
        
        required_integral = self.products[product_id]["integral"]
        if self.users[user_id]["integral"] < required_integral:
            yield event.plain_result(f"积分不足！需要{required_integral}积分，当前积分：{self.users[user_id]['integral']}")
            return
        
        self.users[user_id]["integral"] -= required_integral
        api_key = f"API_KEY_{user_id}_{product_id}"
        self.api_keys[user_id] = api_key
        self._save_json(self.users_file, self.users)
        self._save_json(self.api_keys_file, self.api_keys)
        yield event.plain_result(f"兑换成功！您的API Key：{api_key}")

    @filter.command("add_product")
    async def add_product(self, event: AstrMessageEvent, product_id: str, integral: int):
        """添加商品（仅管理员可用）"""
        if not event.is_admin():
            yield event.plain_result("您没有权限执行此操作！")
            return
        
        self.products[product_id] = {"integral": integral}
        self._save_json(self.products_file, self.products)
        yield event.plain_result(f"商品{product_id}添加成功，需要积分：{integral}")

    async def terminate(self):
        """插件卸载时保存数据"""
        self._save_json(self.users_file, self.users)
        self._save_json(self.api_keys_file, self.api_keys)
        self._save_json(self.products_file, self.products)
