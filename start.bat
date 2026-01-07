@echo off
chcp 65001 >nul
echo ========================================================================
echo TRAFIK ISARETI TANIMA SISTEMI
echo ========================================================================
echo.

REM Proje klasörüne git
cd /d "%~dp0"

REM Python kontrolü
echo Python kontrolu yapiliyor...
python --version 2>&1
if errorlevel 1 (
    echo.
    echo HATA: Python bulunamadi!
    echo.
    echo Lutfen Python yukleyin:
    echo    https://www.python.org/downloads/
    echo.
    echo Kurulum sirasinda Add Python to PATH secenegini isaretleyin!
    echo.
    pause
    exit /b 1
)
echo Python bulundu
echo.

REM Virtual environment kontrolü ve oluşturma
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Ilk kurulum yapiliyor...
    echo    Bu islem birkac dakika surebilir.
    echo.
    echo Sanal ortam olusturuluyor...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo Sanal ortam olusturulamadi!
        echo.
        pause
        exit /b 1
    )
    echo Sanal ortam olusturuldu
) else (
    echo Sanal ortam mevcut
)

REM Gradio paketi kontrolü (kritik paket)
".venv\Scripts\python.exe" -c "import gradio" 2>nul
if errorlevel 1 (
    echo.
    echo Gerekli paketler yukleniyor...
    echo    ultralytics gradio torch vs.
    echo    Bu islem 5-10 dakika surebilir...
    echo.
    echo Internet baglantinizin stabil olduguna emin olun...
    echo.
    ".venv\Scripts\python.exe" -m pip install --upgrade pip --timeout 120 --retries 10
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --timeout 120 --retries 10
    if errorlevel 1 (
        echo.
        echo ========================================================================
        echo PAKETLER YUKLENEMEDI!
        echo ========================================================================
        echo.
        echo Olasiliklar:
        echo   1. Internet baglantiniz yok veya yavas
        echo   2. PyPI sunucusuna erisim sorunu
        echo   3. Guvenlik duvari/antivirus engelliyor
        echo.
        echo Cozum onerileri:
        echo   - Internet baglantinizi kontrol edin
        echo   - VPN deneyebilirsiniz
        echo   - Guvenlik duvarini gecici olarak kapatip tekrar deneyin
        echo   - Farkli bir agdan deneyin (mobil hotspot vs.)
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Tum paketler yuklendi
) else (
    echo Paketler yuklü
)
echo.

REM Model kontrolü
if not exist "best.pt" (
    echo.
    echo HATA: Model dosyasi best.pt bulunamadi!
    echo.
    pause
    exit /b 1
)

REM Tarayıcıyı 8 saniye sonra aç
start "" powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 8; Start-Process 'http://127.0.0.1:7860'"

REM Uygulamayı başlat
echo.
echo ========================================================================
echo Uygulama baslatiliyor...
echo Tarayici otomatik acilacak: http://127.0.0.1:7860
echo ========================================================================
echo.
".venv\Scripts\python.exe" app.py
if errorlevel 1 (
    echo.
    echo Uygulama hata ile kapandi!
    echo.
    pause
    exit /b 1
)

REM Uygulama kapandı
echo.
echo ========================================================================
echo Uygulama kapatildi
echo ========================================================================
pause

