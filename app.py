import streamlit as st
from PIL import Image, ImageFilter, ImageDraw
from io import BytesIO
import zipfile # 引入zip库用于打包下载

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="安安边框", page_icon="🐽", layout="centered")

# --- 2. 核心视觉样式 (莫兰迪·雾霾蓝定制版) ---
style_css = """
<style>
    /* === 全局配色与背景 === */
    .stApp {
        background-color: #F9FAFB;
        color: #2C3E50;
        background-image: radial-gradient(#E5E7EB 1px, transparent 1px);
        background-size: 20px 20px;
    }

    /* === 标题层级 === */
    h1 {
        font-family: "Source Han Sans CN", "Microsoft YaHei", "PingFang SC", sans-serif !important;
        font-weight: 800;
        color: #2C3E50 !important;
        font-size: 42px !important;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -1px;
        text-shadow: 2px 2px 0px rgba(255,255,255,1);
    }
    
    .subtitle {
        font-family: "Source Han Sans CN", "Microsoft YaHei", sans-serif;
        font-weight: 300;
        font-size: 16px;
        color: #95A5A6;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 50px;
        letter-spacing: 2px;
    }

    /* === 上传区域 (交互质感) === */
    [data-testid='stFileUploader'] {
        background-color: rgba(255, 255, 255, 0.6);
        border: 2px dashed #CFD8DC;
        border-radius: 12px;
        padding: 40px 20px;
        background-image: linear-gradient(rgba(123, 141, 153, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(123, 141, 153, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    [data-testid='stFileUploader']:hover {
        border-color: #7B8D99;
        border-style: solid; 
        background-color: rgba(255, 255, 255, 1);
        box-shadow: 0 10px 30px rgba(123, 141, 153, 0.15);
        transform: translateY(-2px);
    }
    [data-testid='stFileUploader'] label { display: none; }

    /* === 按钮美化 === */
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
        background-color: #7B8D99;
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
    [data-testid='stFileUploader'] [data-testid='baseButton-secondary']:hover::after {
        background-color: #60707A;
        transform: scale(1.02);
    }

    /* 提示文字重写 */
    [data-testid='stFileUploader'] section > div > div > span,
    [data-testid='stFileUploader'] small,
    [data-testid='stFileUploader'] section > div > div > div {
        display: none !important;
    }
    [data-testid='stFileUploader'] section > div > svg {
        color: #95A5A6 !important;
        width: 40px !important;
        height: 40px !important;
        margin-bottom: 10px;
    }
    [data-testid='stFileUploader'] section > div > div::before {
        content: "点击或拖拽多张图片到这里 (支持批量)"; /* 修改文案提示批量 */
        color: #7B8D99; 
        font-family: "Microsoft YaHei", sans-serif;
        font-size: 15px;
        font-weight: 500;
        display: block;
    }

    /* === 图片与演示区 === */
    img { 
        border: 10px solid #FFFFFF;
        border-radius: 4px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); 
        transition: transform 0.3s;
    }
    img:hover { transform: scale(1.01); }
    
    .img-label {
        background-color: #E8ECEF;
        color: #60707A;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        width: fit-content;
        margin: 15px auto 0 auto;
        letter-spacing: 1px;
    }

    /* === 下载按钮 === */
    div.stButton > button {
        background: linear-gradient(135deg, #7B8D99 0%, #60707A 100%);
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

    /* === 布局 === */
    .stStatus { 
        background-color: #FFFFFF !important; 
        border: 1px solid #E5E7EB !important; 
        color: #60707A !important; 
        border-radius: 8px;
    }
    .bottom-text {
        text-align: center;
        color: #BDC3C7;
        font-size: 12px;
        margin-top: 40px;
        font-weight: 300;
    }
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

# --- 核心处理函数 (复用逻辑) ---
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
# 开启多文件上传 accept_multiple_files=True
uploaded_files = st.file_uploader(" ", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# 如果没有上传文件 -> 显示演示区
if not uploaded_files:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.image("demo_original.jpg", use_container_width=True)
        st.markdown("<div class='img-label'>原图 ORIGINAL</div>", unsafe_allow_html=True)
    with col_b:
        st.image("demo_processed.png", use_container_width=True)
        st.markdown("<div class='img-label' style='background-color: #D6EAF8; color: #34495E;'>效果 EFFECT</div>", unsafe_allow_html=True)
    st.markdown("<div class='bottom-text'>上传照片，即刻生成同款画廊级质感</div>", unsafe_allow_html=True)

# 如果上传了文件 -> 进入处理流程
else:
    # === 场景 A：单张模式 (保持原有的大图体验) ===
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
            st.markdown("<div class='img-label' style='background-color: #D6EAF8; color: #34495E;'>成片 RESULT</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                # 保持单张直接下载 PNG
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

# === 场景 B：批量模式 (移动端优化版) ===
    else:
        try:
            processed_data = [] # 存储 (图片对象, 文件名)
            zip_buffer = BytesIO()
            
            # 1. 批量处理逻辑
            with st.status(f"正在为 {len(uploaded_files)} 张照片添加质感...", expanded=True) as status:
                progress_bar = st.progress(0)
                
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for i, file in enumerate(uploaded_files):
                        img = Image.open(file)
                        res_img = process_single_image(img, file.name)
                        
                        if res_img:
                            # 转为字节流
                            img_byte_arr = BytesIO()
                            res_img.save(img_byte_arr, format='PNG')
                            img_bytes = img_byte_arr.getvalue()
                            
                            # 存入 ZIP
                            output_filename = f"framed_{file.name.split('.')[0]}.png"
                            zf.writestr(output_filename, img_bytes)
                            
                            # 存入列表用于展示
                            processed_data.append((res_img, output_filename, img_bytes))
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                
                status.update(label="全部处理完成！", state="complete", expanded=False)

            # --- 2. 移动端优化展示区 ---
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 顶部提示
            st.markdown("""
            <div style="background-color: #E8ECEF; padding: 10px; border-radius: 8px; color: #60707A; font-size: 13px; text-align: center; margin-bottom: 20px;">
                💡 手机用户提示：<br>点击下方按钮直接下载，或 <b>长按图片</b> 保存到相册
            </div>
            """, unsafe_allow_html=True)

            # 遍历展示每一张图 (流式布局)
            for idx, (img, name, byte_data) in enumerate(processed_data):
                # 卡片容器
                with st.container():
                    # 显示大图
                    st.image(img, use_container_width=True)
                    
                    # 布局：左边序号，右边大大的下载按钮
                    c1, c2 = st.columns([1, 3])
                    
                    with c1:
                        # 序号标签
                        st.markdown(f"""
                        <div style="
                            background-color: #F0F2F5; 
                            color: #95A5A6; 
                            padding: 12px 0; 
                            text-align: center; 
                            border-radius: 8px; 
                            font-weight: bold;
                            margin-top: 10px;">
                            #{idx+1}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c2:
                        # 每一张图都有独立的下载按钮
                        st.download_button(
                            label=f"⬇️ 保存这张图片",
                            data=byte_data,
                            file_name=name,
                            mime="image/png",
                            key=f"btn_{idx}", # 必须设置唯一的 key
                            type="secondary", # 使用次级样式，不抢视觉
                            use_container_width=True
                        )
                    
                    # 分割线
                    st.markdown("<hr style='border:0; border-top:1px dashed #E5E7EB; margin: 30px 0;'>", unsafe_allow_html=True)

            # --- 3. 底部依然保留 ZIP 下载 (作为备选) ---
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

