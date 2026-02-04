import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO
import base64

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="ArtFrame Pro", page_icon="🎨", layout="centered")

# --- 2. 核心视觉样式 (CSS注入) ---
# 这里是实现“高仿”的关键，我们重写了几乎所有组件的样式
nft_style = """
<style>
    /* 全局背景：深邃黑 */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 50% 0%, #1f1f1f 0%, #0E1117 60%);
    }

    /* 标题样式 */
    h1 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    
    /* 说明文字 */
    .stMarkdown p {
        color: #8b949e !important;
        font-size: 1.1rem;
    }

    /* 上传组件区域美化 */
    [data-testid='stFileUploader'] {
        background-color: #161B22;
        border: 1px dashed #30363d;
        border-radius: 20px;
        padding: 30px;
        transition: all 0.3s ease;
    }
    [data-testid='stFileUploader']:hover {
        border-color: #58a6ff;
        background-color: #1c2128;
        box-shadow: 0 0 30px rgba(0,0,0,0.5);
    }
    /* 隐藏上传组件原本的难看Label */
    [data-testid='stFileUploader'] label {
        color: #c9d1d9;
        font-weight: bold;
    }

    /* 核心按钮样式 (仿照参考图的 Place a Bid 按钮) */
    div.stButton > button {
        background: linear-gradient(90deg, #FDC830 0%, #F37335 100%); /* 橙黄渐变 */
        color: #1f1f1f !important; /* 深色文字增加对比 */
        font-weight: 800 !important;
        border: none;
        border-radius: 50px; /* 胶囊形状 */
        padding: 15px 40px;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(243, 115, 53, 0.4); /* 橙色光晕 */
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(243, 115, 53, 0.6);
        color: #000 !important;
    }

    /* 状态提示框美化 */
    .stStatus {
        background-color: #161B22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 12px;
    }
    
    /* 图片展示区圆角 */
    img {
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    /* 隐藏默认菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(nft_style, unsafe_allow_html=True)

# --- 3. 核心参数 (保持不变) ---
PARAMS = {
    'border_scale': 0.09,
    'blur_radius': 100,
    'corner_radius': 120,
    'shadow_blur': 20,
    'shadow_opacity': 0.2,
    'shadow_offset': 0
}

# --- 4. 界面布局 ---
# 使用 columns 让标题看起来更灵动
col1, col2 = st.columns([3, 1])
with col1:
    st.title("ArtFrame Studio")
    st.markdown("Create gallery-grade visuals in seconds.")

# --- 5. 主体逻辑 ---
uploaded_file = st.file_uploader("Drop your image here", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    # 占位空间，保持页面美观
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👆 请上传照片体验暗黑霓虹风格")

else:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        # 使用 expander 或 status 让处理过程看起来更有科技感
        with st.status("🚀 Processing AI visual effects...", expanded=True) as status:
            
            # --- 算法逻辑 (完全保持原样) ---
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * PARAMS['border_scale'])
            border_width = max(border_width, 1)
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # 背景
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # 遮罩
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=PARAMS['corner_radius'], fill=255)

            # 阴影
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

            # 合成
            final_image = final_background.copy()
            final_image.paste(shadow_final, shadow_pos, mask=shadow_final)
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            status.update(label="✨ Image ready!", state="complete", expanded=False)

        # --- 结果展示 ---
        st.markdown("### Preview")
        st.image(final_image, use_container_width=True)
        
        # 间距
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 下载按钮 (CSS会将其渲染成黄色渐变胶囊按钮)
        st.download_button(
            label="Download Artwork",
            data=byte_im,
            file_name="artframe_dark_edition.png",
            mime="image/png",
            type="primary", # 配合CSS中的div.stButton
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Error: {e}")
