import sys
import time
import yt_dlp

def baixar_video(url, output_dir=".", max_retries=3):
    """
    Baixa o vídeo da URL fornecida no diretório especificado.
    Tenta novamente em caso de erro de rede.
    """
    opcoes = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
       # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
	'format': '18',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
        'retries': 10,
        'fragment_retries': 10,
        'file_access_retries': 5,
        'extractor_retries': 5,
        'socket_timeout': 30,
        'http_chunk_size': 10485760,
        'cookiesfrombrowser': ('chrome',),
	'extractor_args': {'youtube': {'player_client': ['web']}},  # Agora usa web
	'nocheckcertificate': True,
    }

    for tentativa in range(max_retries):
        try:
            print(f"\n🚀 Tentativa {tentativa + 1} de {max_retries}")
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                print(f"🔍 Obtendo informações do vídeo: {url}")
                ydl.download([url])
            print("✅ Download concluído com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro na tentativa {tentativa + 1}: {e}")
            if tentativa < max_retries - 1:
                espera = 5 * (tentativa + 1)
                print(f"⏳ Aguardando {espera} segundos antes de tentar novamente...")
                time.sleep(espera)
            else:
                print("❌ Todas as tentativas falharam.")
                return False

def baixar_varios_videos(urls, output_dir="."):
    """Baixa múltiplos vídeos em sequência"""
    total = len(urls)
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*50}")
        print(f"📹 Vídeo {i} de {total}")
        print(f"{'='*50}")
        baixar_video(url.strip(), output_dir)

def baixar_de_arquivo(arquivo, output_dir="."):
    """Lê URLs de um arquivo e baixa todos os vídeos"""
    try:
        with open(arquivo, 'r') as f:
            urls = [linha.strip() for linha in f if linha.strip() and not linha.startswith('#')]
        if not urls:
            print("❌ Nenhuma URL encontrada no arquivo.")
            return False
        print(f"📂 Encontradas {len(urls)} URLs no arquivo '{arquivo}'")
        baixar_varios_videos(urls, output_dir)
        return True
    except FileNotFoundError:
        print(f"❌ Arquivo '{arquivo}' não encontrado.")
        return False

def mostrar_ajuda():
    print("""
🎬 YouTube Downloader - Modo de usar:

  📌 Baixar um único vídeo:
    python script.py 'URL_DO_VIDEO'

  📌 Baixar vários vídeos (separados por espaço):
    python script.py 'URL1' 'URL2' 'URL3'

  📌 Baixar de um arquivo links.txt:
    python script.py links.txt

  📌 Especificar diretório de saída:
    python script.py 'URL' ./videos
    python script.py links.txt ./videos

  📌 Baixar playlist completa:
    python script.py 'URL_DA_PLAYLIST'

  📌 Baixar apenas um vídeo de uma playlist:
    python script.py 'URL' --no-playlist

💡 Dica: Coloque as URLs entre aspas simples para evitar erros no terminal!
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', '--ajuda']:
        mostrar_ajuda()
        sys.exit(1)

    # Verifica se o último argumento é um diretório (termina com / ou não é URL)
    diretorio = "."
    args_urls = []

    # Procura por --no-playlist nos argumentos
    no_playlist = '--no-playlist' in sys.argv
    args_limpos = [arg for arg in sys.argv[1:] if arg != '--no-playlist']

    if len(args_limpos) >= 2 and not args_limpos[-1].startswith('http'):
        diretorio = args_limpos[-1]
        args_limpos = args_limpos[:-1]

    # Caso 1: Arquivo de texto
    if len(args_limpos) == 1 and args_limpos[0].endswith('.txt'):
        baixar_de_arquivo(args_limpos[0], diretorio)

    # Caso 2: Múltiplas URLs na linha de comando
    else:
        urls = args_limpos
        if len(urls) == 1:
            url = urls[0]
            # Verifica se é playlist
            if "list=" in url and not no_playlist:
                print("📋 URL de playlist detectada!")
                print("💡 Para baixar APENAS este vídeo (não a playlist toda),")
                print("   adicione --no-playlist no final do comando")
                print(f"   Ex: python script.py '{url}' --no-playlist\n")
            baixar_video(url, diretorio)
        else:
            print(f"🎯 Baixando {len(urls)} vídeos...")
            baixar_varios_videos(urls, diretorio)
