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
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(243, 115, 53, 0.6);
    }

    /* === 其他优化 === */
    .stStatus { background-color: #161B22 !important; border: 1px solid #30363d !important; color: #c9d1d9 !important; border-radius: 12px; }
    img { border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
    #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(nft_style, unsafe_allow_html=True)

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
col1, col2 = st.columns([3, 1])
with col1:
    st.title("极简艺术工坊")
    st.markdown("上传照片，一键生成画廊级光影大片。")

# --- 5. 主体逻辑 ---
# label 设为空，因为我们已经在 CSS 里把 label 隐藏了，靠 box 内部的中文提示即可
uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.markdown("<br>", unsafe_allow_html=True)
    # 用 info 做一个补充提示，万一 CSS 加载慢了也能看到
    st.info("👆 请点击上方区域选择照片，或直接拖拽图片")

else:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.status("🚀 正在渲染光影效果...", expanded=True) as status:
            
            # --- 算法逻辑 ---
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * PARAMS['border_scale'])
            border_width = max(border_width, 1)
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            st.write("🎨 生成磨砂背景...")
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=PARAMS['corner_radius'], fill=255)

            st.write("🌑 添加立体投影...")
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
            
            status.update(label="✨ 渲染完成！", state="complete", expanded=False)

        st.markdown("### 效果预览")
        st.image(final_image, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.download_button(
            label="⬇️ 保存高清艺术成片",
            data=byte_im,
            file_name="art_frame_output.png",
            mime="image/png",
            type="primary",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"发生错误：{e}")
