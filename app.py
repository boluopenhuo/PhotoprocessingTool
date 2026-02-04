import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO
import requests

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="极简艺术工坊", page_icon="🍂", layout="centered")

# --- 2. 核心视觉样式 (画廊风定制) ---
gallery_style = """
<style>
    /* === 全局背景：米白/羊皮纸质感 === */
    .stApp {
        background-color: #FAF9F6;
        color: #4A4036;
    }
    
    /* === 字体系统 === */
    h1 {
        font-family: "Songti SC", "SimSun", serif !important;
        color: #2C241B !important;
        font-weight: 600;
        letter-spacing: 2px;
        text-align: center;
        padding-bottom: 10px;
        border-bottom: 1px solid #E0DCD6;
    }
    
    /* 通用文字样式 */
    .stMarkdown p, .stMarkdown h4 {
        font-family: "Songti SC", "SimSun", serif !important;
        text-align: center;
        color: #6B6158 !important;
    }
    
    /* 演示区的标题 */
    h4 {
        margin-top: 30px;
        font-weight: normal;
        font-size: 18px;
        letter-spacing: 4px;
        opacity: 0.8;
    }

    /* === 上传组件：画框风格 === */
    [data-testid='stFileUploader'] {
        background-color: #FFFFFF;
        border: 1px dashed #C4Bcb0;
        border-radius: 4px;
        padding: 40px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    [data-testid='stFileUploader']:hover {
        border-color: #78866B;
        background-color: #FCFCFA;
    }
    [data-testid='stFileUploader'] label { display: none; }

    /* === 🔥 汉化补丁 (保持不变) === */
    [data-testid='stFileUploader'] button {
        visibility: hidden;
        position: relative;
        width: 140px !important;
    }
    [data-testid='stFileUploader'] button::after {
        content: "选择影像文件";
        visibility: visible;
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #F0EEE9;
        color: #5C5248;
        border-radius: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Songti SC", serif;
        font-size: 14px;
        letter-spacing: 1px;
        cursor: pointer;
        border: none;
        transition: all 0.3s;
    }
    [data-testid='stFileUploader'] button:hover::after {
        background-color: #E6E2DC;
        color: #2C241B;
    }

    /* 隐藏文字与重写 */
    [data-testid='stFileUploader'] section > div > div > span,
    [data-testid='stFileUploader'] small,
    [data-testid='stFileUploader'] section > div > div > div {
        display: none !important;
    }
    [data-testid='stFileUploader'] section > div > div::before {
        content: "将照片轻置于此";
        color: #9C9288; 
        font-family: "Songti SC", serif;
        font-size: 15px;
        display: block;
        margin-top: 10px; 
        font-weight: normal;
    }
    [data-testid='stFileUploader'] section > div > svg {
        color: #C4Bcb0 !important;
        fill: #C4Bcb0 !important;
        width: 30px;
        height: 30px;
    }

    /* === 下载按钮 === */
    div.stButton > button {
        background-color: #78866B;
        color: #FFFFFF !important;
        border: none;
        border-radius: 4px;
        padding: 12px 30px;
        font-size: 16px;
        font-family: "Songti SC", serif;
        letter-spacing: 2px;
        box-shadow: 0 4px 10px rgba(120, 134, 107, 0.3);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 20px;
    }
    div.stButton > button:hover {
        background-color: #637058;
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(120, 134, 107, 0.4);
    }

    /* === 图片与布局 === */
    .stStatus { 
        background-color: #FFFFFF !important; 
        border: 1px solid #E0DCD6 !important; 
        color: #5C5248 !important; 
        font-family: "Songti SC", serif;
    }
    
    /* 给所有展示的图片加白边，模拟相框 */
    img { 
        border: 8px solid #FFFFFF;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); 
    }
    
    /* 分隔线样式 */
    hr {
        border-color: #E0DCD6;
        margin-top: 40px;
        margin-bottom: 20px;
        opacity: 0.5;
    }

    #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(gallery_style, unsafe_allow_html=True)

# --- 3. 核心参数 ---
PARAMS = {
    'border_scale': 0.09,
    'blur_radius': 100,
    'corner_radius': 120,
    'shadow_blur': 20,
    'shadow_opacity': 0.2,
    'shadow_offset': 0
}

# --- 4. 界面布局 ---
st.title("云端·艺术工坊")
st.markdown("定格光影 · 赋予照片呼吸感")
st.markdown("<br>", unsafe_allow_html=True)

# --- 5. 主体逻辑 ---
uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    # --- 这里是新增的底部展示区 (只在未上传时显示) ---
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---") # 优雅的分割线
    st.markdown("#### 🎞️ 效果演示") # 小标题
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # 这里放原图示例 (URL)
        st.image("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", 
                 caption="原片直出", use_container_width=True)
                 
    with col_b:
        # 这里放处理后的效果图 (为了演示，我这里暂时放了一张类似的图)
        # 💡 【重要】请在你的工具做好后，截一张图，把下面这个链接换成你自己的截图链接！
        st.image("https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", 
                 caption="艺术装裱", use_container_width=True)
    
    st.markdown("<br><p style='font-size:12px; opacity:0.6'>上传照片，即可获得右侧同款画廊级质感</p>", unsafe_allow_html=True)

else:
    # ... 已上传后的逻辑保持不变 ...
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.status("正在装裱影像...", expanded=True) as status:
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * PARAMS['border_scale'])
            border_width = max(border_width, 1)
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            st.write("渲染柔光背景...")
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=PARAMS['corner_radius'], fill=255)

            st.write("添加空气感阴影...")
            padding = int(PARAMS['shadow_blur'] * 3)
            shadow_canvas_w = orig_w + (2 * padding)
            shadow_canvas_h = orig_h + (2 * padding)
            shadow_layer = Image.new("RGBA", (shadow_canvas_w, shadow_canvas_h), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_draw.rounded_rectangle(
                (padding, padding, padding + orig_w, padding + orig_h), 
                radius=PARAMS['corner_radius'], 
                fill=(0, 0, 0, 255)
            )
            shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(PARAMS['shadow_blur']))
            r, g, b, a = shadow_blurred.split()
            a = a.point(lambda i: i * PARAMS['shadow_opacity'])
            shadow_final = Image.merge("RGBA", (r, g, b, a))
            shadow_pos = (
                border_width + PARAMS['shadow_offset'] - padding, 
                border_width + PARAMS['shadow_offset'] - padding
            )

            final_image = final_background.copy()
            final_image.paste(shadow_final, shadow_pos, mask=shadow_final)
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            status.update(label="装裱完成", state="complete", expanded=False)

        st.markdown("<br>", unsafe_allow_html=True)
        st.image(final_image, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.download_button(
                label="收藏这幅作品",
                data=byte_im,
                file_name="gallery_art.png",
                mime="image/png",
                type="primary",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"发生错误：{e}")
