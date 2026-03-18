# -*- coding: utf8 -*-
import os
import json
import time
from dotenv import load_dotenv
from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

# 🌟 关键：向上找两层目录，准确读取到 LOGIC-COACH/.env 文件
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

class AliyunFileTransService:
    def __init__(self):
        # 从环境变量读取配置
        self.ak_id = os.getenv('ALIYUN_AK_ID')
        self.ak_secret = os.getenv('ALIYUN_AK_SECRET')
        self.app_key = os.getenv('ALIYUN_APPKEY')
        
        self.region_id = "cn-shanghai"
        self.product = "nls-filetrans"
        self.api_version = "2018-08-17"
        
        # 读取网络环境配置 (优先走配置，默认走外网)
        use_internal = os.getenv('USE_INTERNAL_NETWORK', 'False').lower() == 'true'
        
        if use_internal:
            self.domain = 'filetrans-vpc.cn-shanghai.aliyuncs.com'
            print("🌐 [阿里云 ASR] 已切换为 VPC 内网请求 (服务器免流模式)")
        else:
            self.domain = 'filetrans.cn-shanghai.aliyuncs.com'
            print("🌐 [阿里云 ASR] 已切换为公网请求 (本地开发模式)")
            
        # 初始化客户端
        self.client = AcsClient(self.ak_id, self.ak_secret, self.region_id)

    def transcribe(self, file_link, valid_times=None):
        """
        提交录音文件识别任务 (支持长语音)
        """
        postRequest = CommonRequest()
        postRequest.set_domain(self.domain)
        postRequest.set_version(self.api_version)
        postRequest.set_product(self.product)
        postRequest.set_action_name("SubmitTask")
        postRequest.set_method('POST')

        # 🌟 核心业务参数配置
        task_config = {
            "appkey": self.app_key,
            "file_link": file_link,
            "version": "4.0",
            "enable_words": False,               
            "auto_split": True,                  
            "enable_sample_rate_adaptive": True  
        }
        
        if valid_times:
            task_config["valid_times"] = valid_times
            print(f"⏱️ 开启截断识别，时间段：{valid_times}")

        postRequest.add_body_params("Task", json.dumps(task_config))
        
        try:
            print("🎙️ 正在提交 ASR 转写任务给阿里云...")
            postResponse = self.client.do_action_with_exception(postRequest)
            postResponse = json.loads(postResponse)
            
            if postResponse.get("StatusText") == "SUCCESS":
                task_id = postResponse.get("TaskId")
                print(f"✅ 任务提交成功，TaskID: {task_id}")
                return self._wait_for_result(task_id)
            else:
                print(f"❌ 任务提交失败: {postResponse}")
                return None
                
        except (ServerException, ClientException) as e:
            print(f"❌ 提交任务时发生 SDK 异常: {e}")
            return None

    def _wait_for_result(self, task_id):
        """轮询获取识别结果"""
        getRequest = CommonRequest()
        getRequest.set_domain(self.domain)
        getRequest.set_version(self.api_version)
        getRequest.set_product(self.product)
        getRequest.set_action_name("GetTaskResult")
        getRequest.set_method('GET')
        getRequest.add_query_param("TaskId", task_id)

        print("⏳ 正在云端处理中 (请耐心等待，通常需要音频时长的 1/10 时间)...")
        while True:
            try:
                getResponse = self.client.do_action_with_exception(getRequest)
                getResponse = json.loads(getResponse)
                statusText = getResponse.get("StatusText")

                if statusText in ["RUNNING", "QUEUEING"]:
                    time.sleep(3) 
                elif statusText == "SUCCESS":
                    print("🎉 录音转写完成！")
                    return getResponse.get("Result")
                else:
                    print(f"❌ 转写失败或包含无效片段: {statusText}")
                    return None
                    
            except (ServerException, ClientException) as e:
                print(f"❌ 查询状态时发生网络异常: {e}")
                time.sleep(5) 


# ==========================================
# 仅用于本地快速单测
# ==========================================
if __name__ == "__main__":
    asr_service = AliyunFileTransService()
    test_audio_url = "https://gw.alipayobjects.com/os/bmw-prod/0574ee2e-f494-45a5-820f-63aee583045a.wav"
    result = asr_service.transcribe(test_audio_url)
    
    if result:
        print("\n=== 最终结构化对话提取 ===")
        sentences = result.get("Sentences", [])
        for s in sentences:
            speaker = s.get("SpeakerId", "?")
            begin_sec = s.get("BeginTime") / 1000
            text = s.get("Text")
            print(f"[Speaker {speaker} | {begin_sec:.1f}s]: {text}")