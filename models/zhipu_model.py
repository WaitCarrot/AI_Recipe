import os
from zhipuai import ZhipuAI

class ZhipuModel:
    def __init__(self):
        self.client = ZhipuAI(api_key="d2ad332fbdf122498e45e70563723e89.R4gtZhvynrh2x95Z")
        
    def get_response(self, messages):
        messages = [{"role": "user", "content": "请回复：你好",} ,] 
        response = self.client.chat.asyncCompletions.create(
            model="glm-4-0520",
            messages=messages,
            #stream=True
        )
        print(response)
        return response
        
    def process_parallel_responses(self, data):
        # 构建用户基础信息
        user_info = self._format_user_info(data)
        
        # 只处理三个主要方案，不包括综合建议
        prompts = {
            'supplement': f"根据客户提供的信息：{user_info}\n请为客户出具详细的营养补剂方案，输出格式要求如下：**{{营养补剂名称}}**\n- {{结合客户情况，给出推荐理由}}",
            'tcm': f"根据客户提供的信息：{user_info}\n请为客户出具详细的中医调理方案，输出格式要求如下：**{{中医药材名称}}**\n- {{结合客户情况，给出推荐理由}}",
            'diet': f"根据客户提供的信息：{user_info}\n请为客户出具详细的饮食方案，输出格式要求如下：**{{饮食类别名称，如主食、蔬菜、水果、肉类等}}**\n- {{结合客户情况，给出推荐理由}}"
        }
        
        # 为每个类型创建消息
        messages = {
            k: [{"role": "user", "content": v}] for k, v in prompts.items()
        }
        
        # 返回所有响应流
        return {
            k: self.get_response(v) for k, v in messages.items()
        }
        
    def _format_user_info(self, data):
        """格式化用户输入的信息"""
        info = f"""
        年龄：{data.get('age')}
        性别：{data.get('gender')}
        身高：{data.get('height')}
        体重：{data.get('weight')}
        职业：{data.get('occupation')}
        运动频率：{data.get('exercise_frequency')}
        睡眠质量：{data.get('sleep_quality')}
        饮食习惯：{data.get('eating_habits')}
        消化状况：{data.get('digestion')}
        压力水平：{data.get('stress_level')}
        月经情况：{data.get('menstruation')}
        关节肌肉状况：{data.get('joint_muscle')}
        近期体重变化：{data.get('weight_change')}
        过敏敏感情况：{data.get('allergy_sensitivity')}
        体质类型：{data.get('constitution')}
        面色：{data.get('complexion')}
        舌苔状况：{data.get('tongue')}
        脉象：{data.get('pulse')}
        """
        return info
