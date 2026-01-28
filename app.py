import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# 页面配置
st.set_page_config(page_title="圆角模糊相框工具", page_icon="🖼️")
st.title("🖼️ 圆角模糊相框工具")
st.markdown("上传照片，为您生成自适应比例的模糊圆角相框。")

# --- 核心逻辑 0：初始化默认参数 (使用 Session State) ---
# 定义默认值字典
default_values = {
    'border_scale': 0.05,
    'blur_radius': 100,
    'corner_radius': 150
}

# 如果是第一次运行，将默认值写入 session_state
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 定义重置函数：点击按钮时执行
def reset_defaults():
    for key, value in default_values.items():
        st.session_state[key] = value

# --- 侧边栏：参数设置 ---
with st.sidebar:
    st.header("参数调节")
    
    # 【改动1】添加“恢复默认”按钮，绑定回调函数
    # use_container_width=True 让按钮铺满侧边栏宽度，更好看
    st.button("↺ 恢复默认设置", on_click=reset_defaults, use_container_width=True)
    
    st.divider() # 添加一条分割线
    
    # 【改动2】给滑块绑定 key，这样它们的值就会受 session_state 控制
    # 注意：绑定 key 后，不需要再写 value=xxx，它会自动读取 session_state[key]
    
    border_scale = st.slider(
        "边框粗细比例 (Scale)", 
        0.0, 0.3, step=0.01, 
        key='border_scale',  # 绑定状态
        help="边框宽度占画面短边的比例"
    )
    
    blur_radius = st.slider(
        "背景模糊程度 (Blur)", 
        0, 200, 
        key='blur_radius',   # 绑定状态
        help="数值越大，背景越模糊"
    )
    
    corner_radius = st.slider(
        "圆角大小 (Radius)", 
        0, 500, 
        key='corner_radius'  # 绑定状态
    )
    
    st.info("💡 提示：点击上方按钮可一键还原参数。")

# --- 主体逻辑 ---
uploaded_file = st.file_uploader("点击上传图片 (支持 JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        with st.spinner('正在智能处理...'):
            # --- 核心计算 ---
            base_size = min(orig_w, orig_h)
            
            # 计算动态边框宽度 (至少保留1个像素)
            border_width = int(base_size * border_scale)
            border_width = max(border_width, 1)

            # --- 步骤 1：创建背景 ---
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            blurred_source = original_image.filter(ImageFilter.GaussianBlur(blur_radius))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            # --- 步骤 2：处理圆角 ---
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
        st.success(f"处理完成！当前分辨率: {orig_w}x{orig_h}")
        
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
