import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="极简艺术相框", page_icon="🎨", layout="centered")

# --- 2. 核心视觉样式 (含强力汉化补丁) ---
nft_style = """
<style>
    /* === 全局背景与基础样式 === */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 50% 0%, #1f1f1f 0%, #0E1117 60%);
    }
    h1, .stMarkdown p {
        font-family: "Microsoft YaHei", sans-serif !important; 
    }
    h1 { color: #FFFFFF !important; text-shadow: 0 0 20px rgba(255, 255, 255, 0.2); }
    .stMarkdown p { color: #8b949e !important; }

    /* === 上传组件美化 === */
    [data-testid='stFileUploader'] {
        background-color: #161B22;
        border: 1px dashed #30363d;
        border-radius: 20px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    [data-testid='stFileUploader']:hover {
        border-color: #58a6ff;
        background-color: #1c2128;
    }
    /* 隐藏组件自带的 Label (因为我们在外面自己写了提示) */
    [data-testid='stFileUploader'] label {
        display: none;
    }

    /* === 🔥 核心汉化黑科技 (CSS Hack) === */
    
    /* 1. 针对 "Browse files" 按钮 */
    [data-testid='stFileUploader'] button {
        visibility: hidden; /* 先把原来的按钮藏起来 */
        position: relative;
        width: 120px !important;
    }
    /* 再用伪元素手绘一个中文按钮 */
    [data-testid='stFileUploader'] button::after {
        content: "浏览本地文件";  /* <--- 这里修改按钮文字 */
        visibility: visible;
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #ffffff;
        color: #000000;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        border: 1px solid #ccc;
    }
    [data-testid='stFileUploader'] button:hover::after {
        background-color: #f0f0f0;
        border-color: #aaa;
    }

    /* 2. 针对 "Drag and drop file here" 提示语 */
    /* 把容器内的所有文字变透明，但保留图标颜色 */
    [data-testid='stFileUploader'] section > div > div {
        color: transparent !important; 
    }
    /* 补上中文提示 */
    [data-testid='stFileUploader'] section > div > div::after {
        content: "支持拖拽照片到这里"; /* <--- 这里修改提示文字 */
        color: #c9d1d9; /* 恢复文字颜色 */
        font-size: 16px;
        font-weight: bold;
        display: block;
        margin-top: -15px; /* 调整位置盖住原来的英文 */
    }
    /* 恢复 SVG 图标的颜色 (因为父级transparent了，这里要强制指定) */
    [data-testid='stFileUploader'] section > div > div > svg {
        color: #58a6ff !important;
        fill: #58a6ff !important;
    }

    /* 3. 彻底隐藏 "Limit 200MB..." 这行小字 */
    [data-testid='stFileUploader'] small {
        display: none !important;
    }

    /* === 下载按钮样式 === */
    div.stButton > button {
        background: linear-gradient(90deg, #FDC830 0%, #F37335 100%);
        color: #1f1f1f !important;
        font-weight: 800 !important;
        border: none;
        border-radius: 50px;
        padding: 15px 40px;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(243, 115, 53, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        font-family: "Microsoft YaHei", sans-serif;
    }
    div.stButton > button:hover {
        transform
