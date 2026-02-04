import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# 页面配置
st.set_page_config(page_title="圆角模糊相框工具", page_icon="🖼️")
st.title("🖼️ 圆角模糊相框工具")
st.markdown("上传照片，为您生成带立体自然阴影的自适应相框。")

# --- 核心逻辑 0：初始化默认参数 ---
default_values = {
    'border_scale': 0.1,    # 边框比例
    'blur_radius': 100,     # 背景模糊
    'corner_radius': 120,   # 圆角大小
    # 【默认值优化】模仿图二的效果：阴影重、模糊大、距离近
    'shadow_blur': 50,      # 阴影模糊度
    'shadow_opacity': 0.5,  # 阴影浓度
    'shadow_offset': 15     # 阴影距离 (新增参数)
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
    border_scale = st.slider("边框粗细比例", 0.0, 0.3, step=0.01, key='border_scale')
    corner_radius = st.slider("圆角大小", 0, 500, key='corner_radius')

    st.subheader("🌫️ 背景与氛围")
    blur_radius = st.slider("背景模糊程度", 0, 200, key='blur_radius')
    
    # 【阴影设置升级】
    st.subheader("⚫ 立体阴影")
    shadow_blur = st.slider("阴影柔化度 (Blur)", 0, 150, key='shadow_blur', help="决定阴影边缘的羽化程度")
    shadow_opacity = st.slider("阴影不透明度 (Opacity)", 0.0, 1.0, step=0.05, key='shadow_opacity')
    # 新增：独立控制阴影距离
    shadow_offset = st.slider("阴影距离 (Distance)", -50, 100, key='shadow_offset', help="阴影相对于照片的偏移距离，值越小越贴合")

# --- 主体逻辑 ---
uploaded_file = st.file_uploader("点击上传图片 (支持 JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.spinner('正在生成自然阴影...'):
            # --- 基础计算 ---
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * border_scale)
            border_width = max(border_width, 1)
            
            # 1. 计算大背景尺寸
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            # 2. 生成背景层
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # 3. 创建主图圆角遮罩
            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=corner_radius, fill=255)

            # --- 【关键修复】步骤 4：生成防裁切阴影层 ---
            if shadow_opacity > 0 and shadow_blur > 0:
                # 为了防止高斯模糊时边缘被切断，我们需要给阴影层加一个“扩张缓冲区”
                # 缓冲区大小通常设为模糊半径的 3 倍即可保证边缘平滑过渡
                padding = int(shadow_blur * 3)
                
                # 创建一个比原图大一圈的临时画布
                shadow_canvas_w = orig_w + (2 * padding)
                shadow_canvas_h = orig_h + (2 * padding)
                shadow_layer = Image.new("RGBA", (shadow_canvas_w, shadow_canvas_h), (0, 0, 0, 0))
                
                # 在画布中心画黑色圆角矩形
                shadow_draw = ImageDraw.Draw(shadow_layer)
                shadow_draw.rounded_rectangle(
                    (padding, padding, padding + orig_w, padding + orig_h), 
                    radius=corner_radius, 
                    fill=(0, 0, 0, 255)
                )
                
                # 对整个大画布进行模糊 (这样边缘就不会被切断了！)
                shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
                
                # 处理透明度
                r, g, b, a = shadow_blurred.split()
                a = a.point(lambda i: i * shadow_opacity)
                shadow_final = Image.merge("RGBA", (r, g, b, a))
                
                # 计算粘贴坐标：
                # 基础位置 (border_width) + 用户偏移 (shadow_offset) - 缓冲区偏移 (padding)
                shadow_paste_x = border_width + shadow_offset - padding
                shadow_paste_y = border_width + shadow_offset - padding
                shadow_pos = (shadow_paste_x, shadow_paste_y)
            else:
                shadow_final = None

            # --- 步骤 5：合成 ---
            final_image = final_background.copy()
            
            # 贴阴影
            if shadow_final:
                # 阴影层可能比背景大，需要裁剪粘贴或者允许负坐标（PIL允许）
                final_image.paste(shadow_final, shadow_pos, mask=shadow_final)
                
            # 贴原图
            final_image.paste(original_image, (border_width, border_width), mask=mask)

            buf = BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

        # --- 结果展示 ---
        st.success(f"处理完成！阴影已优化防裁切。")
        st.image(final_image, caption="自然立体效果", use_container_width=True)
        st.download_button(
            label="⬇️ 下载处理后的图片", data=byte_im, file_name="processed_natural_shadow.png", mime="image/png", type="primary"
        )

    except Exception as e:
        st.error(f"发生错误：{e}")
else:
    st.info("👆 请先在上方上传一张图片")
