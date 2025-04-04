import json
import time
import uuid
import hashlib
import random
from typing import Optional, Dict, Any, Literal, List
import requests
import asyncio

# 模型映射
MODEL_MAP = {
    "jimeng-2.1": "high_aes_general_v21_L:general_v2.1_L",
    "jimeng-2.0-pro": "high_aes_general_v20_L:general_v2.0_L",
    "jimeng-2.0": "high_aes_general_v20:general_v2.0",
    "jimeng-1.4": "high_aes_general_v14:general_v1.4",
    "jimeng-xl-pro": "text2img_xl_sft",
}

# 常量定义
DEFAULT_MODEL = "jimeng-2.1"
MODEL_NAME = "jimeng"
DEFAULT_ASSISTANT_ID = "513695"
VERSION_CODE = "5.8.0"
PLATFORM_CODE = "7"
DRAFT_VERSION = "3.0.2"

# 生成随机ID
DEVICE_ID = str(int(random.random() * 999999999999999999 + 7000000000000000000))
WEB_ID = str(int(random.random() * 999999999999999999 + 7000000000000000000))

class Util:
    @staticmethod
    def uuid(separator: bool = True) -> str:
        """生成UUID
        
        Args:
            separator: 是否保留分隔符
            
        Returns:
            UUID字符串
        """
        uuid_str = str(uuid.uuid4())
        return uuid_str if separator else uuid_str.replace("-", "")

# 生成用户ID
USER_ID = Util.uuid(False)

class APIException(Exception):
    """API异常类"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

class ErrorCode:
    """错误码定义"""
    API_REQUEST_FAILED = "API_REQUEST_FAILED"
    API_IMAGE_GENERATION_FAILED = "API_IMAGE_GENERATION_FAILED"
    API_IMAGE_GENERATION_INSUFFICIENT_POINTS = "API_IMAGE_GENERATION_INSUFFICIENT_POINTS"
    API_CONTENT_FILTERED = "API_CONTENT_FILTERED"

def get_sign(uri: str, platform_code: str, version_code: str, device_time: int) -> str:
    """生成签名
    
    Args:
        uri: 请求路径
        platform_code: 平台代码
        version_code: 版本号
        device_time: 设备时间戳
    
    Returns:
        生成的签名字符串
    """
    sign_str = f"9e2c|{uri[-7:]}|{platform_code}|{version_code}|{device_time}||11ac"
    return hashlib.md5(sign_str.encode()).hexdigest()

def check_result(response: requests.Response) -> Dict[str, Any]:
    """检查API响应结果
    
    Args:
        response: requests响应对象
    
    Returns:
        处理后的响应数据
    
    Raises:
        APIException: 当API返回错误时抛出
    """
    result = response.json()
    ret = result.get('ret')
    errmsg = result.get('errmsg', '')
    data = result.get('data')

    # 如果ret不是数字，返回原始数据
    try:
        ret = str(int(ret))
    except (ValueError, TypeError):
        return result

    if ret == '0':
        return data
    if ret == '5000':
        raise APIException(
            ErrorCode.API_IMAGE_GENERATION_INSUFFICIENT_POINTS,
            f"[无法生成图像]: 即梦积分可能不足，{errmsg}"
        )
    raise APIException(
        ErrorCode.API_REQUEST_FAILED,
        f"[请求jimeng失败]: {errmsg}"
    )

async def request(
    method: str,
    uri: str,
    cookie: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    response_type: Optional[str] = None,
) -> Dict[str, Any]:
    """发送请求到jimeng API
    
    Args:
        method: 请求方法
        uri: 请求路径
        cookie: 即梦网站的cookie
        data: 请求体数据
        params: URL参数
        headers: 请求头
        response_type: 响应类型
    
    Returns:
        处理后的响应数据
    """
    device_time = int(time.time())
    sign = get_sign(uri, PLATFORM_CODE, VERSION_CODE, device_time)
    
    # 构建请求参数
    default_params = {
        "aid": DEFAULT_ASSISTANT_ID,
        "device_platform": "web",
        "region": "CN",
        "web_id": WEB_ID,
    }
    if params:
        default_params.update(params)
    
    # 构建请求头
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Cookie": cookie,
        "Device-Time": str(device_time),
        "Sign": sign,
        "Sign-Ver": "1",
        "Pf": PLATFORM_CODE,
        "Referer": "https://jimeng.jianying.com",
        "Appid": DEFAULT_ASSISTANT_ID,
        "Appvr": VERSION_CODE,
    }
    if headers:
        default_headers.update(headers)
    
    response = requests.request(
        method=method,
        url=f"https://jimeng.jianying.com{uri}",
        params=default_params,
        headers=default_headers,
        json=data,
        timeout=15
    )
    
    # 流式响应直接返回
    if response_type == 'stream':
        return response
        
    return check_result(response)

async def wait_for_generation(cookie: str, history_id: str) -> List[str]:
    """等待图片生成完成并获取结果
    
    Args:
        cookie: 即梦网站的cookie
        history_id: 历史记录ID
    
    Returns:
        生成的图片URL列表
    """
    if not history_id:
        raise APIException(ErrorCode.API_IMAGE_GENERATION_FAILED, "记录ID不存在")
    
    status = 20
    fail_code = None
    item_list = []
    
    # 图片信息配置
    image_info = {
        "width": 2048,
        "height": 2048,
        "format": "webp",
        "image_scene_list": [
            {
                "scene": "smart_crop",
                "width": size,
                "height": size,
                "uniq_key": f"smart_crop-w:{size}-h:{size}",
                "format": "webp",
            }
            for size in [360, 480, 720]
        ] + [
            {
                "scene": "smart_crop",
                "width": 720,
                "height": 480,
                "uniq_key": "smart_crop-w:720-h:480",
                "format": "webp",
            },
            {
                "scene": "smart_crop",
                "width": 360,
                "height": 240,
                "uniq_key": "smart_crop-w:360-h:240",
                "format": "webp",
            },
            {
                "scene": "smart_crop",
                "width": 240,
                "height": 320,
                "uniq_key": "smart_crop-w:240-h:320",
                "format": "webp",
            },
            {
                "scene": "smart_crop",
                "width": 480,
                "height": 640,
                "uniq_key": "smart_crop-w:480-h:640",
                "format": "webp",
            }
        ] + [
            {
                "scene": "normal",
                "width": size,
                "height": size,
                "uniq_key": str(size),
                "format": "webp",
            }
            for size in [2400, 1080, 720, 480, 360]
        ]
    }
    
    while status == 20:
        await asyncio.sleep(1)  # 等待1秒
        
        result = await request(
            "post",
            "/mweb/v1/get_history_by_ids",
            cookie=cookie,
            data={
                "history_ids": [history_id],
                "image_info": image_info,
                "http_common_info": {
                    "aid": int(DEFAULT_ASSISTANT_ID),
                }
            }
        )
        
        if not result.get(history_id):
            raise APIException(ErrorCode.API_IMAGE_GENERATION_FAILED, "记录不存在")
            
        record = result[history_id]
        status = record["status"]
        fail_code = record.get("fail_code")
        item_list = record.get("item_list", [])
    
    if status == 30:
        if fail_code == '2038':
            raise APIException(ErrorCode.API_CONTENT_FILTERED)
        else:
            raise APIException(ErrorCode.API_IMAGE_GENERATION_FAILED)
    
    # 提取图片URL
    return [
        item.get("image", {}).get("large_images", [{}])[0].get("image_url")
        or item.get("common_attr", {}).get("cover_url")
        for item in item_list
        if item
    ]

async def generate_image(
    cookie: str,
    prompt: str,
    model: Literal["jimeng-2.1", "jimeng-2.0-pro", "jimeng-2.0", "jimeng-1.4", "jimeng-xl-pro"] = DEFAULT_MODEL,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    sample_strength: float = 0.75,
) -> List[str]:
    """生成图片
    
    Args:
        cookie: 即梦网站的cookie
        prompt: 提示词
        model: 模型名称
        negative_prompt: 反向提示词
        width: 图片宽度
        height: 图片高度
        sample_strength: 采样强度
    
    Returns:
        生成的图片URL列表
    """
    
    # 获取实际的模型标识符
    model_identifier = MODEL_MAP[model]
    
    # 生成必要的参数
    component_id = str(uuid.uuid4())
    device_time = int(time.time())
    uri = "/mweb/v1/aigc_draft/generate"
    
    # 获取签名
    sign = get_sign(uri, PLATFORM_CODE, VERSION_CODE, device_time)
    
    # 构建请求参数
    babi_param = {
        "scenario": "image_video_generation",
        "feature_key": "aigc_to_image",
        "feature_entrance": "to_image",
        "feature_entrance_detail": f"to_image-{model_identifier}"
    }
    
    data = {
        "extend": {
            "root_model": model_identifier,
            "template_id": ""
        },
        "submit_id": str(uuid.uuid4()),
        "metrics_extra": json.dumps({
            "templateId": "",
            "generateCount": 1,
            "promptSource": "custom",
            "templateSource": "",
            "lastRequestId": "",
            "originRequestId": ""
        }),
        "draft_content": json.dumps({
            "type": "draft",
            "id": str(uuid.uuid4()),
            "min_version": DRAFT_VERSION,
            "is_from_tsn": True,
            "version": DRAFT_VERSION,
            "main_component_id": component_id,
            "component_list": [{
                "type": "image_base_component",
                "id": component_id,
                "min_version": DRAFT_VERSION,
                "generate_type": "generate",
                "aigc_mode": "workbench",
                "abilities": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "generate": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "core_param": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "model": model_identifier,
                            "prompt": prompt,
                            "negative_prompt": negative_prompt,
                            "seed": int(time.time() * 1000) % 100000000 + 2500000000,
                            "sample_strength": sample_strength,
                            "image_ratio": 1,
                            "large_image_info": {
                                "type": "",
                                "id": str(uuid.uuid4()),
                                "height": height,
                                "width": width
                            }
                        },
                        "history_option": {
                            "type": "",
                            "id": str(uuid.uuid4())
                        }
                    }
                }
            }]
        }),
        "http_common_info": {
            "aid": int(DEFAULT_ASSISTANT_ID)
        }
    }
    
    response = await request(
        "post", 
        "/mweb/v1/aigc_draft/generate",
        cookie=cookie,
        data=data
    )
    
    # 从aigc_data中获取history_record_id
    aigc_data = response.get('aigc_data', {})
    history_id = aigc_data.get('history_record_id')
    
    # 等待生成完成并返回结果
    return await wait_for_generation(cookie, history_id)
