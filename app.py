"""
🚦 Trafik İşareti Tanıma Sistemi
YOLOv8 ile Eğitilmiş Model - Görsel Testi
"""

import gradio as gr
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import webbrowser
import threading
import time

# Model yükleme
print("🚀 Model yükleniyor...")
MODEL_PATH = "best.pt"

try:
    model = YOLO(MODEL_PATH)
    print(f"✅ Model başarıyla yüklendi!")
    print(f"📊 Sınıf sayısı: {len(model.names)}")
except Exception as e:
    print(f"❌ Model yüklenemedi: {e}")
    raise

def predict_image(image, confidence_threshold, iou_threshold):
    """
    Görsel üzerinde tahmin yapar
    
    Args:
        image: Input image (PIL Image or numpy array)
        confidence_threshold: Minimum güven skoru (0-1)
        iou_threshold: IoU threshold (0-1)
    
    Returns:
        Annotated image with detections
    """
    if image is None:
        return None, "❌ Lütfen bir görsel yükleyin!"
    
    try:
        # Tahmin yap
        results = model.predict(
            image,
            conf=confidence_threshold,
            iou=iou_threshold,
            verbose=False
        )
        
        # Sonuçları al
        result = results[0]
        boxes = result.boxes
        
        # Annotated görsel oluştur
        annotated_img = result.plot()
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        
        # İstatistikler
        num_detections = len(boxes)
        
        if num_detections > 0:
            # Tespit edilen sınıflar ve güven skorları
            detections_text = f"### ✅ {num_detections} Trafik İşareti Tespit Edildi!\n\n"
            
            for i, box in enumerate(boxes, 1):
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                cls_name = model.names[cls_id]
                
                detections_text += f"**{i}. {cls_name}**\n"
                detections_text += f"   📊 Güven Skoru: {conf:.2%}\n\n"
        else:
            detections_text = "### ⚠️ Hiçbir trafik işareti tespit edilemedi!\n\n"
            detections_text += "**Öneriler:**\n"
            detections_text += "- Confidence threshold'u düşürmeyi deneyin\n"
            detections_text += "- Daha net bir görsel kullanın\n"
            detections_text += "- Görseldeki trafik işaretinin belirgin olduğundan emin olun"
        
        return annotated_img, detections_text
    
    except Exception as e:
        error_msg = f"### ❌ Hata Oluştu!\n\n```\n{str(e)}\n```"
        return None, error_msg

# Gradio arayüzü CSS
custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
"""

with gr.Blocks() as demo:
    
    # Başlık
    gr.HTML("""
        <div class="header">
            <h1>🚦 Trafik İşareti Tanıma Sistemi</h1>
            <p>YOLOv8 ile Eğitilmiş Derin Öğrenme Modeli</p>
        </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Görsel Yükleme")
            
            # Görsel yükleme
            image_input = gr.Image(
                type="pil",
                label="Trafik işareti içeren görsel yükleyin",
                height=400
            )
            
            gr.Markdown("### ⚙️ Ayarlar")
            
            # Confidence threshold
            confidence_slider = gr.Slider(
                minimum=0.01,
                maximum=1.0,
                value=0.25,
                step=0.01,
                label="Güven Eşiği (Confidence Threshold)",
                info="Daha düşük değer = Daha fazla tespit (ama daha az güvenilir)"
            )
            
            # IoU threshold
            iou_slider = gr.Slider(
                minimum=0.01,
                maximum=1.0,
                value=0.45,
                step=0.01,
                label="IoU Eşiği",
                info="Çakışan tespitleri filtreleme"
            )
            
            # Tahmin butonu
            predict_btn = gr.Button(
                "🔍 Trafik İşaretlerini Tespit Et",
                variant="primary",
                size="lg"
            )
            
            # Temizle butonu
            clear_btn = gr.Button("🗑️ Temizle")
            
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Sonuçlar")
            
            # Çıktı görseli
            image_output = gr.Image(
                label="Tespit Edilen Trafik İşaretleri",
                height=400
            )
            
            # Sonuç metni
            result_text = gr.Markdown()
    
    # Örnek görseller (opsiyonel)
    gr.Markdown("### 📸 Örnek Görseller")
    gr.Markdown("*Kendi görselinizi yükleyebilir veya test için örnek görselleri kullanabilirsiniz*")
    
    # Model bilgileri
    gr.Markdown(f"""
    ---
    ### 📋 Model Bilgileri
    - **Model:** YOLOv8n (Nano)
    - **Sınıf Sayısı:** {len(model.names)}
    - **Model Dosyası:** {MODEL_PATH}
    
    ### 💡 Kullanım İpuçları
    1. Trafik işareti içeren bir görsel yükleyin
    2. Gerekirse güven eşiğini ayarlayın (varsayılan: 0.25)
    3. "Trafik İşaretlerini Tespit Et" butonuna tıklayın
    4. Sonuçları sağ tarafta görüntüleyin
    
    ### 📞 Performans Notları
    - **mAP50:** 32.5% (264 sınıf ile eğitilmiş)
    - **Precision:** 63.7%
    - **Recall:** 27.9%
    
    *Not: Düşük performans nedeniyle bazı trafik işaretleri tespit edilemeyebilir.*
    """)
    
    # Event handlers
    predict_btn.click(
        fn=predict_image,
        inputs=[image_input, confidence_slider, iou_slider],
        outputs=[image_output, result_text]
    )
    
    clear_btn.click(
        fn=lambda: (None, None, ""),
        outputs=[image_input, image_output, result_text]
    )

# Tarayıcıyı gecikmeyle aç
def open_browser():
    time.sleep(2)  # 2 saniye bekle
    url = "http://127.0.0.1:7860"
    print(f"\n🌐 Tarayıcı açılıyor: {url}")
    webbrowser.open(url)

# Uygulamayı başlat
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌐 Gradio arayüzü başlatılıyor...")
    print("="*70)
    
    # Tarayıcıyı ayrı thread'de aç
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,  # Sabit port kullan
            share=False,
            inbrowser=False,  # Manuel açacağız
            show_error=True,
            theme=gr.themes.Soft(),
            css=custom_css
        )
    except Exception as e:
        print("\n" + "="*70)
        print("❌ HATA: Uygulama başlatılamadı!")
        print("="*70)
        print(f"\n🔍 Hata detayı: {e}")
        print("\n💡 Olası çözümler:")
        print("   1. Port 7860 zaten kullanımda olabilir")
        print("   2. Gerekli paketler eksik olabilir")
        print("   3. best.pt dosyası bozuk olabilir")
        print("\n📌 Sorunu çözmek için:")
        print("   - Diğer çalışan uygulamaları kapatın")
        print("   - venv klasörünü silin ve tekrar çalıştırın")
        print("\n")
        import traceback
        traceback.print_exc()
        input("\nDevam etmek için Enter'a basın...")
        raise
