import streamlit as st
from PIL import Image, ImageFilter, ImageDraw, ImageChops
from io import BytesIO

# 页面配置
st.set_page_config(page_title="圆角模糊相框工具", page_icon="🖼️")
st.title("🖼️ 圆角模糊相框工具")
st.markdown("上传照片，为您生成带立体阴影的自适应模糊圆角相框。")

# --- 核心逻辑 0：初始化默认参数 ---
default_values = {
    'border_scale': 0.1,  # 边框比例 10%
    'blur_radius': 100,   # 背景模糊
    'corner_radius': 150, # 圆角大小
    # 【新增】阴影默认参数
    'shadow_blur': 30,    # 阴影柔化
    'shadow_opacity': 0.6 # 阴影不透明度 (0.0 - 1.0)
}

# 写入 session_state
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 重置函数
def reset_defaults():
    for key, value in default_values.items():
        st.session_state[key] = value

# --- 侧边栏：参数设置 ---
with st.sidebar:
    st.header("参数调节")
    st.button("↺ 恢复默认设置", on_click=reset_defaults, use_container_width=True)
    st.divider()
    
    st.subheader("📐 布局与形状")
    border_scale = st.slider("边框粗细比例", 0.0, 0.3, step=0.01, key='border_scale', help="边框占画面短边的比例")
    corner_radius = st.slider("圆角大小", 0, 500, key='corner_radius')

    st.subheader("🌫️ 背景与氛围")
    blur_radius = st.slider("背景模糊程度", 0, 200, key='blur_radius')
    
    # 【新增】阴影设置分区
    st.subheader("⚫ 立体阴影")
    shadow_blur = st.slider("阴影柔化度 (Blur)", 0, 100, key='shadow_blur', help="数值越大，阴影边缘越柔和扩散")
    shadow_opacity = st.slider("阴影不透明度 (Opacity)", 0.0, 1.0, step=0.1, key='shadow_opacity', help="0为全透明，1为纯黑")

# --- 主体逻辑 ---
uploaded_file = st.file_uploader("点击上传图片 (支持 JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.spinner('正在生成立体效果...'):
            # --- 基础计算 ---
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * border_scale)
            border_width = max(border_width, 1)
            
            # 计算新画布尺寸
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # --- 步骤 1：创建背景 ---
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # --- 步骤 2：创建圆角遮罩 ---
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=corner_radius, fill=255)

            # --- 【新增】步骤 2.5：生成阴影层 ---
            if shadow_opacity > 0:
                # a. 创建一个纯黑色的图层
                black_layer = Image.new("RGBA", (orig_w, orig_h), (0, 0, 0, 255))
                
                # b. 应用圆角遮罩，得到一个边缘锋利的黑色圆角矩形
                shadow_sharp = Image.new("RGBA", (orig_w, orig_h), (0,0,0,0))
                shadow_sharp.paste(black_layer, (0, 0), mask=mask)
                
                # c. 高斯模糊，让边缘变柔和
                shadow_soft = shadow_sharp.filter(ImageFilter.GaussianBlur(shadow_blur))
                
                # d. 处理透明度 (操作 Alpha 通道)
                # 分离通道
                r, g, b, a = shadow_soft.split()
                # 将 Alpha 通道的值乘以不透明度系数
                a = a.point(lambda i: i * shadow_opacity)
                # 合并回 RGBA
                shadow_final = Image.merge("RGBA", (r, g, b, a))
                
                # e. 计算阴影偏移量 (稍微向右下偏移，偏移量与模糊度挂钩)
                offset_val = int(shadow_blur * 0.5) + 5
                shadow_pos = (border_width + offset_val, border_width + offset_val)
            else:
                shadow_final = None

            # --- 步骤 3：三层合成 ---
            final_image = final_background.copy()
            
            # 先贴阴影层 (如果在原图下面)
            if shadow_final:
                # 使用阴影自身作为 mask 进行粘贴以保持透明度
                final_image.paste(shadow_final, shadow_pos, mask=shadow_final)
                
            # 再贴原图层 (在最上面)
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

        # --- 结果展示 ---
        st.success(f"处理完成！")
        st.image(final_image, caption="立体效果预览", use_container_width=True)
        st.download_button(
            label="⬇️ 下载处理后的图片", data=byte_im, file_name="processed_frame_shadow.png", mime="image/png", type="primary"
        )

    except Exception as e:
        st.error(f"发生错误：{e}")
else:
    st.info("👆 请先在上方上传一张图片")
