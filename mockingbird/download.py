import json
from pathlib import Path

import httpx
from nonebot.log import logger
from utils.http_utils import AsyncHttpx

base_url = "https://pan.yropo.top/source/mockingbird/"


async def download_url(url: str, path: Path) -> bool:
    for i in range(3):
        try:
            url = (await AsyncHttpx.post(url)).url
            resp = await AsyncHttpx.download_file(url, path)
            if resp:
                return True
            else:
                continue
        except Exception as e:
            logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
    return False

# 下载资源
async def download_resource(root: Path, model_name: str):
    for file_name in ["g_hifigan.pt", "encoder.pt"]:
        if not (root / file_name).exists():
            logger.info(f"{file_name}不存在，开始下载{file_name}...请不要退出...")
            res = await download_url(url=base_url + file_name, path=root / file_name)
            if not res:
                return False
    url = f"{base_url}{model_name}/"
    for file_name in ["record.wav", f"{model_name}.pt"]:
        if not (root / model_name / file_name).exists():
            logger.info(f"{file_name}不存在，开始下载{file_name}...请不要退出...")
            res = await download_url(url + file_name, root / model_name / file_name)
            if not res:
                return False
    return True
    
# 检查资源是否存在
async def check_resource(root: Path, model_name: str):
    for file_name in ["g_hifigan.pt", "encoder.pt"]:
        if not (root / file_name).exists():
            return False
    for file_name in ["record.wav", f"{model_name}.pt"]:
        if not (root / model_name / file_name).exists():
            return False
    return True

# 更新模型列表
def get_model_list_file(file_path: Path) -> None:
    url = f"https://fastly.jsdelivr.net/gh/AkashiCoin/nonebot_plugin_mockingbird@master/nonebot_plugin_mockingbird/resource/model_list.json"
    try:
        with httpx.Client() as Client:
            data = Client.get(url).json()
            if data:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    return True
            else:
                return "更新模型列表失败..."
    except Exception as e:
        logger.error(f"Error downloading {url} .. Error: {e}")
        return "更新模型列表失败..."
