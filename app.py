import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="极简艺术相框", page_icon="🎨", layout="centered")

# --- 2. 核心视觉样式 (CSS注入) ---
nft_style = """
<style>
    /* 全局背景：深邃黑 + 径向渐变 */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 50% 0%, #1f1f1f 0%, #0E1117 60%);
    }

    /* 标题样式 - 增加中文字重 */
    h1 {
        color: #FFFFFF !important;
        font-family: "Microsoft YaHei", "PingFang SC", sans-serif; 
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    
    /* 副标题/说明文字 */
    .stMarkdown p {
        color: #8b949e !important;
        font-size: 1.1rem;
        font-family: "Microsoft YaHei", sans-serif;
    }

    /* 上传组件美化 */
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
    /* 强行修改上传组件内部文字颜色 */
    [data-testid='stFileUploader'] label {
        color: #c9d1d9;
        font-weight: bold;
    }
    /* 隐藏上传组件自带的 Small text */
    [data-testid='stFileUploader'] small {
        color: #6e7681;
    }

    /* 核心按钮样式 (霓虹渐变) */
    div.stButton > button {
        background: linear-gradient(90deg, #FDC830 0%, #F37335 100%); /* 橙黄渐变 */
        color: #1f1f1f !important;
        font-weight: 800 !important;
        border: none;
        border-radius: 50px; /* 胶囊形状 */
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
        color: #000 !important;
    }

    /* 状态提示框美化 */
    .stStatus {
        background-color: #161B22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 12px;
    }
    
    /* 图片圆角与阴影 */
    img {
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    /* 隐藏多余元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(nft_style, unsafe_allow_html=True)

# --- 3. 核心参数 (保持之前调整好的最佳值) ---
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
# label_visibility="visible" 但通过CSS自定义了样式，这里文案设为空格避免重复
uploaded_file = st.file_uploader("点击或拖拽上传图片", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👆 请在上方上传照片，体验暗黑霓虹风格")

else:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        # 使用 st.status 显示处理状态
        with st.status("🚀 正在渲染光影效果...", expanded=True) as status:
            
            # --- 算法逻辑 ---
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * PARAMS['border_scale'])
            border_width = max(border_width, 1)
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # 1. 背景
            st.write("🎨 生成磨砂背景...")
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # 2. 遮罩
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=PARAMS['corner_radius'], fill=255)

            # 3. 阴影
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

            # 4. 合成
            final_image = final_background.copy()
            final_image.paste(shadow_final, shadow_pos, mask=shadow_final)
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            status.update(label="✨ 渲染完成！", state="complete", expanded=False)

        # --- 结果展示 ---
        st.markdown("### 效果预览")
        st.image(final_image, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 下载按钮
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
