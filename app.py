import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# 页面配置
st.set_page_config(page_title="圆角模糊相框工具", page_icon="🖼️")
st.title("🖼️ 圆角模糊相框工具")
st.markdown("上传照片，为其增加一个基于内容自适应的模糊圆角相框。")

# --- 侧边栏：参数设置 ---
with st.sidebar:
    st.header("参数调节")
    
    # 新增：控制外围边框的宽度
    border_width = st.slider("边框宽度 (Padding)", 0, 200, 60, help="围绕主体照片的模糊区域宽度（像素）")
    
    blur_radius = st.slider("背景模糊程度 (Blur)", 0, 200, 100, help="数值越大，背景越模糊")
    corner_radius = st.slider("圆角大小 (Radius)", 0, 300, 120, help="主体照片的圆角程度")
    
    st.info("💡 提示：调整参数后图片会自动更新。手机横屏操作体验更佳。")

# --- 主体逻辑 ---
uploaded_file = st.file_uploader("点击上传图片 (支持 JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # 读取图片
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.spinner('正在生成相框效果...'):
            # --- 核心步骤 1：创建更大的模糊背景画布 ---
            # 计算最终图像的新尺寸（原尺寸 + 四周的边框宽度）
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # 生成模糊源图像
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
            
            # 将模糊图像拉伸调整到新的大画布尺寸，作为背景
            # 使用 LANCZOS 算法保证缩放质量
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # --- 核心步骤 2：处理原图的圆角 ---
            # 创建一个和【原图】一样大的遮罩
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            # 在遮罩上画白色的圆角矩形（白色代表保留，黑色代表透明）
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=corner_radius, fill=255)

            # --- 核心步骤 3：合成 ---
            # 以模糊大图为基底
            final_image = final_background.copy()
            # 将带有圆角遮罩的原图，粘贴到大图的中心位置
            # 粘贴坐标就是左上角的偏移量，刚好是边框的宽度 (border_width, border_width)
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            # 转换为字节流以便下载和显示
            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

        # --- 结果展示 ---
        st.success("处理完成！")
        
        # 展示图片，使用容器宽度
        st.image(final_image, caption="效果预览", use_container_width=True)

        # 下载按钮
        st.download_button(
            label="⬇️ 下载处理后的图片",
            data=byte_im,
            file_name="processed_frame.png",
            mime="image/png",
            type="primary"
        )

    except Exception as e:
        st.error(f"发生错误：{e}\n请确保上传的是有效的图片文件。")
else:
    st.info("👆 请先在上方上传一张图片")
