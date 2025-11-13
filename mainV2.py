from pytubefix import YouTube
import os
from pathlib import Path

def download_video(url, save_path=None):
    # Define a pasta "Downloads" padrão se nenhum caminho for dado
    if save_path is None:
        save_path = str(Path.home() / "/mnt/raid_striping/Programacao/downloads")

    try:
        yt = YouTube(url)
        print(f"Baixando: {yt.title}")

        stream = yt.streams.get_highest_resolution()

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        print(f"Salvando em: {save_path}")
        stream.download(output_path=save_path)
        print(f"Download completo! Vídeo salvo em: {os.path.join(save_path, stream.default_filename)}")

    except Exception as e:
        print(f"Ocorreu um erro ao baixar {url}: {e}")



if __name__ == "__main__":

    # Coloque aqui todos os links que você quer baixar
    video_urls = []

    print(f"\n--- Iniciando downloads de {len(video_urls)} vídeos ---")

    for link in video_urls:
        download_video(link)
        print("---")

    print("Todos os downloads foram concluídos!")
