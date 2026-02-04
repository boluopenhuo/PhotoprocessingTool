import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="质感边框", page_icon="🌊", layout="centered")

# --- 2. 核心视觉样式 (莫兰迪·雾霾蓝定制版) ---
style_css = """
<style>
    /* === 全局配色与背景 === */
    .stApp {
        background-color: #F9FAFB; /* 极淡的冷灰白，比米黄更清爽 */
        color: #2C3E50; /* 深蓝灰文字 */
        background-image: radial-gradient(#E5E7EB 1px, transparent 1px); /* 极细的背景噪点 */
        background-size: 20px 20px;
    }

    /* === 1. 强化标题层级 === */
    h1 {
        font-family: "Source Han Sans CN", "Microsoft YaHei", "PingFang SC", sans-serif !important;
        font-weight: 800; /* 加粗 */
        color: #2C3E50 !important;
        font-size: 42px !important; /* 放大字号 */
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -1px;
        text-shadow: 2px 2px 0px rgba(255,255,255,1); /* 白色硬投影，增加立体感 */
    }
    
    /* 自定义副标题样式 */
    .subtitle {
        font-family: "Source Han Sans CN", "Microsoft YaHei", sans-serif;
        font-weight: 300; /* 极细 */
        font-size: 16px;
        color: #95A5A6; /* 浅灰 */
        text-align: center;
        margin-top: 10px;
        margin-bottom: 50px; /* 增加与上传区的间距 (呼吸感) */
        letter-spacing: 2px;
    }

    /* === 2. 优化上传区域 (交互质感) === */
    [data-testid='stFileUploader'] {
        background-color: rgba(255, 255, 255, 0.6);
        border: 2px dashed #CFD8DC; /* 默认浅灰虚线 */
        border-radius: 12px; /* 圆角 */
        padding: 40px 20px;
        /* 内部细网格纹理 */
        background-image: linear-gradient(rgba(123, 141, 153, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(123, 141, 153, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Hover 状态：变为实线主题色边框 */
    [data-testid='stFileUploader']:hover {
        border-color: #7B8D99; /* 雾霾蓝 */
        border-style: solid; 
        background-color: rgba(255, 255, 255, 1);
        box-shadow: 0 10px 30px rgba(123, 141, 153, 0.15);
        transform: translateY(-2px);
    }
    
    [data-testid='stFileUploader'] label { display: none; }

    /* === 按钮汉化与美化 (雾霾蓝主题) === */
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary'] {
        visibility: hidden;
        position: relative;
        width: 160px !important; /* 稍微加宽 */
    }
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary']::after {
        content: "浏览本地文件";
        visibility: visible;
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #7B8D99; /* 雾霾蓝底色 */
        color: #FFFFFF;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Microsoft YaHei", sans-serif;
        font-weight: 500;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(123, 141, 153, 0.3);
        transition: all 0.2s;
    }
    /* 按钮 Hover */
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary']:hover::after {
        background-color: #60707A; /* 深一点的蓝灰 */
        transform: scale(1.02);
    }

    /* 提示文字重写 */
    [data-testid='stFileUploader'] section > div > div > span,
    [data-testid='stFileUploader'] small,
    [data-testid='stFileUploader'] section > div > div > div {
        display: none !important;
    }
    /* 增加图标大小和颜色 */
    [data-testid='stFileUploader'] section > div > svg {
        color: #95A5A6 !important;
        width: 40px !important;
        height: 40px !important;
        margin-bottom: 10px;
    }
    /* 新的引导文案 */
    [data-testid='stFileUploader'] section > div > div::before {
        content: "点击或拖拽图片到这里";
        color: #7B8D99; 
        font-family: "Microsoft YaHei", sans-serif;
        font-size: 15px;
        font-weight: 500;
        display: block;
    }

    /* === 3. 效果演示区 (拍立得风格) === */
    /* 给演示图片加统一的白边和阴影 */
    img { 
        border: 10px solid #FFFFFF;
        border-radius: 4px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); 
        transition: transform 0.3s;
    }
    img:hover {
        transform: scale(1.01);
    }
    
    /* 图片下方的标签卡片 */
    .img-label {
        background-color: #E8ECEF;
        color: #60707A;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        width: fit-content;
        margin: 15px auto 0 auto; /* 居中 */
        letter-spacing: 1px;
    }

    /* === 下载按钮 === */
    div.stButton > button {
        background: linear-gradient(135deg, #7B8D99 0%, #60707A 100%); /* 渐变蓝灰 */
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        padding: 15px 30px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 2px;
        box-shadow: 0 8px 20px rgba(123, 141, 153, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 30px;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(123, 141, 153, 0.5);
    }

    /* === 布局调整 === */
    .stStatus { 
        background-color: #FFFFFF !important; 
        border: 1px solid #E5E7EB !important; 
        color: #60707A !important; 
        border-radius: 8px;
    }
    
    /* 底部文字居中 */
    .bottom-text {
        text-align: center;
        color: #BDC3C7;
        font-size: 12px;
        margin-top: 40px;
        font-weight: 300;
    }

    /* 隐藏默认元素 */
    #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

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

# 标题 (加粗, 深色)
st.markdown("<h1>质感边框</h1>", unsafe_allow_html=True)

# 副标题 (极细, 浅灰, 增加间距)
st.markdown("<div class='subtitle'>定格光影 · 赋予照片呼吸感</div>", unsafe_allow_html=True)

# --- 5. 主体逻辑 ---
uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    # --- 底部演示区 (留白增加) ---
    
    # 使用空白占位符增加间距 (50px)
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    
    # 演示区布局
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.image("demo_original.jpg", use_container_width=True)
        # 标签组件
        st.markdown("<div class='img-label'>原图 ORIGINAL</div>", unsafe_allow_html=True)
                 
    with col_b:
        st.image("demo_processed.png", use_container_width=True)
        # 标签组件 (高亮色)
        st.markdown("<div class='img-label' style='background-color: #D6EAF8; color: #34495E;'>效果 EFFECT</div>", unsafe_allow_html=True)
    
    # 底部提示文字 (居中, 小字)
    st.markdown("<div class='bottom-text'>上传照片，即刻生成同款画廊级质感</div>", unsafe_allow_html=True)

else:
    # ... 已上传后的逻辑 ...
    try:
        original_image = Image.open(uploaded_file).convert("RGBA")
        orig_w, orig_h = original_image.size

        # 状态栏也优化一下文案
        with st.status("正在进行影像处理...", expanded=True) as status:
            base_size = min(orig_w, orig_h)
            border_width = int(base_size * PARAMS['border_scale'])
            border_width = max(border_width, 1)
            new_w = orig_w + (2 * border_width)
            new_h = orig_h + (2 * border_width)

            st.write("构建雾感背景...")
            blurred_source = original_image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
            final_background = blurred_source.resize((new_w, new_h), Image.LANCZOS)

            mask = Image.new("L", (orig_w, orig_h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, orig_w, orig_h), radius=PARAMS['corner_radius'], fill=255)

            st.write("渲染立体光影...")
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
            
            status.update(label="处理完成", state="complete", expanded=False)

        st.markdown("<br>", unsafe_allow_html=True)
        st.image(final_image, use_container_width=True)
        # 结果图下方也加个标签
        st.markdown("<div class='img-label' style='background-color: #D6EAF8; color: #34495E;'>成片 RESULT</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.download_button(
                label="保存高清大图",
                data=byte_im,
                file_name="texture_border_art.png",
                mime="image/png",
                type="primary",
                use_container_width=True
            )
        
        # 底部也加上版权
        st.markdown("<div class='bottom-text'>Designed for Photography · 2026</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"发生错误：{e}")
