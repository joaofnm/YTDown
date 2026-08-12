#!/bin/bash

echo "=== YouTube Downloader Build Script ==="
echo ""

# Detecta o sistema operacional
OS="$(uname -s)"
case "$OS" in
    Darwin*)
        echo "🖥️  Sistema: macOS"
        echo "📦 Build para macOS..."

        pyinstaller \
            --onedir \
            --windowed \
            --name "YouTubeDownloader" \
            --collect-all yt_dlp \
            --osx-bundle-identifier "com.joaofnm.youtubedownloader" \
            --clean \
            main.py

        codesign --force --deep --sign - dist/YouTubeDownloader.app 2>/dev/null
        xattr -cr dist/YouTubeDownloader.app 2>/dev/null
        echo "✅ App criado: dist/YouTubeDownloader.app"
        ;;

    Linux*)
        echo "🐧 Sistema: Linux"
        echo "📦 Build para Linux..."

        # Verifica se é Debian/Ubuntu ou Fedora
        if [ -f /etc/debian_version ]; then
            echo "📦 Detected: Debian/Ubuntu"
        elif [ -f /etc/fedora-release ]; then
            echo "📦 Detected: Fedora"
        fi

        pyinstaller \
            --onedir \
            --name "YouTubeDownloader" \
            --collect-all yt_dlp \
            --clean \
            main.py

        echo "✅ Executável criado: dist/YouTubeDownloader/YouTubeDownloader"

        # Opcional: criar .deb
        echo "📦 Criando pacote .deb..."
        mkdir -p package/DEBIAN
        mkdir -p package/usr/local/bin
        cp dist/YouTubeDownloader/YouTubeDownloader package/usr/local/bin/

        cat > package/DEBIAN/control << EOF
Package: youtube-downloader
Version: 1.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: João
Description: YouTube Video Downloader with GUI
EOF

        dpkg-deb --build package 2>/dev/null && mv package.deb YouTubeDownloader.deb 2>/dev/null
        echo "✅ Pacote .deb criado: YouTubeDownloader.deb"
        ;;

    CYGWIN*|MINGW*|MSYS*)
        echo "🪟 Sistema: Windows"
        echo "📦 Build para Windows..."

        pyinstaller \
            --onedir \
            --windowed \
            --name "YouTubeDownloader" \
            --collect-all yt_dlp \
            --clean \
            main.py

        echo "✅ Executável criado: dist/YouTubeDownloader/YouTubeDownloader.exe"
        ;;

    *)
        echo "❌ Sistema não suportado: $OS"
        exit 1
        ;;
esac

echo ""
echo "=== Build concluído! ==="
