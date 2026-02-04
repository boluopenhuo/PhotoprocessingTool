import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# 页面配置：设置标题和图标
st.set_page_config(page_title="极简圆角相框", page_icon="🖼️", layout="centered")

# 标题与简介
st.title("🖼️ 极简圆角相框")
st.markdown("上传照片，一键生成带有自然阴影的圆角画廊效果。")

# --- 核心参数配置 (已固定为你满意的最佳值) ---
PARAMS = {
    'border_scale': 0.09,    # 边框比例
    'blur_radius': 100,      # 背景模糊度
    'corner_radius': 120,    # 圆角大小
    'shadow_blur': 20,       # 阴影柔化
    'shadow_opacity': 0.2,   # 阴影浓度 (淡雅风格)
    'shadow_offset': 0       # 阴影距离 (居中)
}

# --- 主体逻辑 ---
# 隐藏 Streamlit 默认的汉堡菜单和页脚，让界面极致干净
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
# label_visibility="collapsed" 是为了隐藏"Choose a file"这行字，只保留按钮，更极简

if uploaded_file is None:
    # 未上传时显示一个友好的提示框
    st.info("👆 请点击上方区域上传一张照片")

else:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        # 显示处理状态
        with st.status("正在打造艺术相框...", expanded=True) as status:
            
            # --- 1. 基础计算 ---
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * PARAMS['border_scale'])
            border_width = max(border_width, 1)
            
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # --- 2. 生成背景 ---
            st.write("🎨 正在渲染模糊背景...")
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # --- 3. 处理圆角 ---
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=PARAMS['corner_radius'], fill=255)

            # --- 4. 生成阴影 ---
            st.write("🌑 正在添加立体投影...")
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
            
            # 透明度处理
            r, g, b, a = shadow_blurred.split()
            a = a.point(lambda i: i * PARAMS['shadow_opacity'])
            shadow_final = Image.merge("RGBA", (r, g, b, a))
            
            shadow_pos = (
                border_width + PARAMS['shadow_offset'] - padding, 
                border_width + PARAMS['shadow_offset'] - padding
            )

            # --- 5. 合成 ---
            final_image = final_background.copy()
            final_image.paste(shadow_final, shadow_pos, mask=shadow_final)
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            status.update(label="处理完成！", state="complete", expanded=False)

        # --- 结果展示 ---
        st.image(final_image, use_container_width=True)
        
        # 居中显示的下载按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="⬇️ 保存图片",
                data=byte_im,
                file_name="art_frame.png",
                mime="image/png",
                type="primary",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"发生错误：{e}")
