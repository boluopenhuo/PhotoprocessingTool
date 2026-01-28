import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# 页面配置
st.set_page_config(page_title="圆角模糊相框工具", page_icon="🖼️")
st.title("🖼️ 圆角模糊相框工具")
st.markdown("上传照片，为您生成自适应比例的模糊圆角相框。")

# --- 侧边栏：参数设置 ---
with st.sidebar:
    st.header("参数调节")
    
    # 【改动1】这里改成了百分比比例，范围 0.0 到 0.5 (即 0% - 50%)
    border_scale = st.slider("边框粗细比例 (Scale)", 0.0, 0.3, 0.05, step=0.01, help="边框宽度占画面短边的比例，确保不同分辨率下视觉效果一致")
    
    blur_radius = st.slider("背景模糊程度 (Blur)", 0, 200, 100, help="数值越大，背景越模糊")
    
    # 【改动2】圆角也建议改为相对比例，或者保留像素调节。
    # 为了简单直观，这里保留像素调节，但增加了范围以适应大图
    corner_radius = st.slider("圆角大小 (Radius)", 0, 500, 150)
    
    st.info("💡 提示：现在边框宽度会根据图片分辨率自动缩放，手机电脑效果一致。")

# --- 主体逻辑 ---
uploaded_file = st.file_uploader("点击上传图片 (支持 JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.spinner('正在智能处理...'):
            # --- 核心计算：根据比例计算实际像素 ---
            # 取长宽中较短的一边作为基准
            base_size = min(orig_w, orig_h)
            
            # 计算动态边框宽度 (至少保留1个像素)
            border_width = int(base_size * border_scale)
            border_width = max(border_width, 1)

            # --- 步骤 1：创建更大的模糊背景画布 ---
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # 生成模糊源图像
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
            
            # 拉伸作为背景
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # --- 步骤 2：处理原图圆角 ---
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=corner_radius, fill=255)

            # --- 步骤 3：合成 ---
            final_image = final_background.copy()
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

        # --- 结果展示 ---
        st.success(f"处理完成！当前分辨率: {orig_w}x{orig_h}，自动匹配边框宽度: {border_width}px")
        
        st.image(final_image, caption="效果预览", use_container_width=True)

        st.download_button(
            label="⬇️ 下载处理后的图片",
            data=byte_im,
            file_name="processed_frame.png",
            mime="image/png",
            type="primary"
        )

    except Exception as e:
        st.error(f"发生错误：{e}")
else:
    st.info("👆 请先在上方上传一张图片")
