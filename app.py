import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO
import zipfile

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="安安边框", page_icon="🐽", layout="centered")

# --- 2. 核心视觉样式 (深海渐变定制版) ---
style_css = """
<style>
    /* === 全局配色与背景 === */
    .stApp {
        /* 使用最浅的冰川蓝作为环境底色，营造通透感 */
        background-color: #F4F9FD; 
        color: #021024; /* 深邃黑蓝文字 */
        
        /* 顶部增加一个淡淡的渐变光晕，呼应 C1E8FF */
        background-image: linear-gradient(to bottom, #E3F2FD 0%, #F4F9FD 400px);
    }

    /* === 1. 标题层级 === */
    h1 {
        font-family: "Source Han Sans CN", "Microsoft YaHei", sans-serif !important;
        font-weight: 900;
        color: #052659 !important; /* 海军蓝 */
        font-size: 46px !important;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -1px;
        /* 增加一点科技感的投影 */
        text-shadow: 0px 2px 0px rgba(255,255,255,0.8);
    }
    
    /* 副标题 */
    .subtitle {
        font-family: "Microsoft YaHei", sans-serif;
        font-weight: 400;
        font-size: 15px;
        color: #5483B3; /* 钢蓝色 */
        text-align: center;
        margin-top: 5px;
        margin-bottom: 40px;
        letter-spacing: 1.5px;
    }

    /* === 2. 上传区域 (深海质感) === */
    [data-testid='stFileUploader'] {
        background-color: rgba(255, 255, 255, 0.7);
        border: 2px dashed #7DA0CA; /* 迷雾蓝边框 */
        border-radius: 16px;
        padding: 40px 20px;
        /* 极其细腻的斜纹理 */
        background-image: repeating-linear-gradient(
            45deg,
            rgba(193, 232, 255, 0.1),
            rgba(193, 232, 255, 0.1) 10px,
            rgba(255, 255, 255, 0.1) 10px,
            rgba(255, 255, 255, 0.1) 20px
        );
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Hover 状态：加深颜色，增强立体感 */
    [data-testid='stFileUploader']:hover {
        border-color: #052659; /* 海军蓝实线 */
        border-style: solid; 
        background-color: #FFFFFF;
        box-shadow: 0 15px 40px rgba(5, 38, 89, 0.1); /* 深蓝阴影 */
        transform: translateY(-2px);
    }
    
    [data-testid='stFileUploader'] label { display: none; }

    /* === 按钮美化 (渐变蓝) === */
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary'] {
        visibility: hidden;
        position: relative;
        width: 160px !important;
    }
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary']::after {
        content: "浏览本地文件";
        visibility: visible;
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        /* 按钮背景：使用 C1E8FF 到 7DA0CA 的浅色渐变 */
        background: linear-gradient(135deg, #7DA0CA 0%, #5483B3 100%);
        color: #FFFFFF;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Microsoft YaHei", sans-serif;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 4px 10px rgba(84, 131, 179, 0.3);
        transition: all 0.2s;
    }
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary']:hover::after {
        background: linear-gradient(135deg, #5483B3 0%, #052659 100%); /* Hover变深 */
        transform: scale(1.02);
    }

    /* 引导文字 */
    [data-testid='stFileUploader'] section > div > div > span,
    [data-testid='stFileUploader'] small,
    [data-testid='stFileUploader'] section > div > div > div {
        display: none !important;
    }
    [data-testid='stFileUploader'] section > div > svg {
        color: #5483B3 !important; /* 图标颜色 */
        width: 45px !important;
        height: 45px !important;
        margin-bottom: 15px;
        filter: drop-shadow(0px 4px 6px rgba(84, 131, 179, 0.2));
    }
    [data-testid='stFileUploader'] section > div > div::before {
        content: "点击或拖拽图片到这里 (支持批量)";
        color: #052659; 
        font-family: "Microsoft YaHei", sans-serif;
        font-size: 16px;
        font-weight: 600;
        display: block;
    }

    /* === 图片与演示区 === */
    img { 
        border: 10px solid #FFFFFF;
        border-radius: 6px;
        /* 投影稍微带一点点蓝色 */
        box-shadow: 0 15px 35px rgba(2, 16, 36, 0.1); 
        transition: transform 0.3s;
    }
    img:hover { transform: scale(1.01); }
    
    /* 标签样式：使用冰川蓝 C1E8FF 背景 */
    .img-label {
        background-color: #C1E8FF; 
        color: #052659; /* 深蓝字 */
        padding: 6px 18px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
        width: fit-content;
        margin: 15px auto 0 auto;
        letter-spacing: 1px;
    }

    /* === 下载按钮 (主按钮) === */
    div.stButton > button {
        /* 强烈的深海渐变 */
        background: linear-gradient(135deg, #052659 0%, #5483B3 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        padding: 16px 30px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 2px;
        box-shadow: 0 10px 25px rgba(5, 38, 89, 0.4); /* 深色投影 */
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 30px;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(5, 38, 89, 0.5);
    }
    
    /* 批量下载时的次级按钮 (灰色/淡蓝) */
    [data-testid="baseButton-secondary"] {
        border-color: #7DA0CA !important;
        color: #052659 !important;
    }

    /* === 布局优化 === */
    .stStatus { 
        background-color: #FFFFFF !important; 
        border: 1px solid #C1E8FF !important; 
        color: #052659 !important; 
        border-radius: 10px;
    }
    .bottom-text {
        text-align: center;
        color: #7DA0CA;
        font-size: 12px;
        margin-top: 50px;
        font-weight: 400;
        opacity: 0.8;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# --- 3. 核心参数 ---
PARAMS = {
    'border_scale': 0.09,
    'blur_radius': 100,
    'corner_radius': 10,
    'shadow_blur': 20,
    'shadow_opacity': 0.2,
    'shadow_offset': 0
}

# --- 核心处理函数 ---
def process_single_image(image, filename):
    try:
        image = image.convert("RGBA")
        orig_w, orig_h = image.size
        
        base_size = min(orig_w, orig_h)
        border_width = int(base_size * PARAMS['border_scale'])
        border_width = max(border_width, 1)
        new_w = orig_w + (2 * border_width)
        new_h = orig_h + (2 * border_width)

        # 背景
        blurred_source = image.filter(ImageFilter.GaussianBlur(PARAMS['blur_radius']))
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
        final_image.paste(image, (border_width, border_width), mask=mask)
        
        return final_image
    except Exception as e:
        return None

# --- 4. 界面布局 ---
st.markdown("<h1>安安边框</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>一键生成自适应模糊边框，打造画廊级质感</div>", unsafe_allow_html=True)

# --- 5. 主体逻辑 ---
uploaded_files = st.file_uploader(" ", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# 未上传状态
if not uploaded_files:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.image("demo_original.jpg", use_container_width=True)
        # 使用冰川蓝标签
        st.markdown("<div class='img-label'>原图 ORIGINAL</div>", unsafe_allow_html=True)
    with col_b:
        st.image("demo_processed.png", use_container_width=True)
        # 使用高亮标签
        st.markdown("<div class='img-label' style='background-color: #052659; color: #FFFFFF;'>效果 EFFECT</div>", unsafe_allow_html=True)
    st.markdown("<div class='bottom-text'>上传照片，即刻生成同款画廊级质感</div>", unsafe_allow_html=True)

# 上传后状态
else:
    # === 场景 A：单张模式 ===
    if len(uploaded_files) == 1:
        file = uploaded_files[0]
        try:
            original_image = Image.open(file)
            
            with st.status("正在进行影像处理...", expanded=True) as status:
                st.write("渲染立体光影...")
                final_image = process_single_image(original_image, file.name)
                
                buf = BytesIO()
                final_image.save(buf, format="PNG")
                byte_im = buf.getvalue()
                status.update(label="处理完成", state="complete", expanded=False)

            st.markdown("<br>", unsafe_allow_html=True)
            st.image(final_image, use_container_width=True)
            st.markdown("<div class='img-label' style='background-color: #052659; color: #FFFFFF;'>成片 RESULT</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                output_name = f"framed_{file.name.split('.')[0]}.png"
                st.download_button(
                    label="保存高清大图",
                    data=byte_im,
                    file_name=output_name,
                    mime="image/png",
                    type="primary",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"处理图片时发生错误: {e}")

    # === 场景 B：批量模式 (移动端优化) ===
    else:
        try:
            processed_data = [] 
            zip_buffer = BytesIO()
            
            with st.status(f"正在为 {len(uploaded_files)} 张照片添加质感...", expanded=True) as status:
                progress_bar = st.progress(0)
                
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for i, file in enumerate(uploaded_files):
                        img = Image.open(file)
                        res_img = process_single_image(img, file.name)
                        
                        if res_img:
                            img_byte_arr = BytesIO()
                            res_img.save(img_byte_arr, format='PNG')
                            img_bytes = img_byte_arr.getvalue()
                            
                            output_filename = f"framed_{file.name.split('.')[0]}.png"
                            zf.writestr(output_filename, img_bytes)
                            processed_data.append((res_img, output_filename, img_bytes))
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                
                status.update(label="全部处理完成！", state="complete", expanded=False)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # 移动端提示条 (使用淡蓝色背景)
            st.markdown("""
            <div style="background-color: #E3F2FD; padding: 12px; border-radius: 8px; color: #052659; font-size: 13px; text-align: center; margin-bottom: 20px; border: 1px solid #C1E8FF;">
                💡 手机用户提示：<br>点击下方按钮直接下载，或 <b>长按图片</b> 保存到相册
            </div>
            """, unsafe_allow_html=True)

            for idx, (img, name, byte_data) in enumerate(processed_data):
                with st.container():
                    st.image(img, use_container_width=True)
                    
                    c1, c2 = st.columns([1, 3])
                    
                    with c1:
                        # 序号标签 (深蓝配色)
                        st.markdown(f"""
                        <div style="
                            background-color: #F0F4F8; 
                            color: #5483B3; 
                            padding: 12px 0; 
                            text-align: center; 
                            border-radius: 8px; 
                            font-weight: bold;
                            margin-top: 10px;">
                            #{idx+1}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c2:
                        st.download_button(
                            label=f"⬇️ 保存这张图片",
                            data=byte_data,
                            file_name=name,
                            mime="image/png",
                            key=f"btn_{idx}",
                            type="secondary",
                            use_container_width=True
                        )
                    
                    st.markdown("<hr style='border:0; border-top:1px dashed #C1E8FF; margin: 30px 0;'>", unsafe_allow_html=True)

            with st.expander("📦 电脑端？点此一键打包下载 (.zip)"):
                st.download_button(
                    label=f"下载压缩包 ({len(uploaded_files)}张)",
                    data=zip_buffer.getvalue(),
                    file_name="anan_framed_photos.zip",
                    mime="application/zip",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"批量处理时发生错误: {e}")

    # 底部版权
    st.markdown("<div class='bottom-text'>Designed for Photography · 2026</div>", unsafe_allow_html=True)


