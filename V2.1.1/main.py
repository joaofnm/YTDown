import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import yt_dlp

# Força o diretório de trabalho correto para o .app
if getattr(sys, 'frozen', False):
    # Muda para Downloads como padrão para salvar os vídeos
    os.chdir(os.path.expanduser("~/Downloads"))

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("700x600")

        # Variáveis
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.downloading = False
        self.cancel_download = False

        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL Entry
        ttk.Label(main_frame, text="URL do Vídeo/Playlist:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Botões de ação rápida
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=5)

        ttk.Button(btn_frame, text="Adicionar URL", command=self.add_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Limpar URLs", command=self.clear_urls).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Carregar de Arquivo", command=self.load_from_file).pack(side=tk.LEFT, padx=2)

        # Lista de URLs
        ttk.Label(main_frame, text="Lista de URLs para baixar:").grid(row=2, column=0, sticky=tk.W, pady=5)

        # Listbox com scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.url_listbox = tk.Listbox(list_frame, height=6, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=scrollbar.set)

        self.url_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Diretório de saída
        ttk.Label(options_frame, text="Diretório de saída:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dir_entry = ttk.Entry(options_frame, textvariable=self.output_dir, width=40)
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        ttk.Button(options_frame, text="Procurar...", command=self.browse_directory).grid(row=0, column=2, pady=5)

        # Formato
        ttk.Label(options_frame, text="Formato:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="Auto (Melhor disponível)")
        self.format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, state="readonly", width=30)
        self.format_combo['values'] = (
            'Auto (Melhor disponível)',
            '18 (MP4 480p)',
            '22 (MP4 720p)',
            '137+140 (MP4 1080p)',
            'best (Melhor qualidade)',
            'bestaudio (Apenas áudio)'
        )
        self.format_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)

        # No playlist checkbox
        self.no_playlist_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Baixar apenas este vídeo (não a playlist)",
                       variable=self.no_playlist_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Botões de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.download_btn = ttk.Button(control_frame, text="Iniciar Download",
                                      command=self.start_download, width=20)
        self.download_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = ttk.Button(control_frame, text="Cancelar",
                                    command=self.cancel_downloads, state=tk.DISABLED, width=20)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # Progresso
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.progress_label = ttk.Label(main_frame, text="Aguardando...")
        self.progress_label.grid(row=7, column=0, columnspan=3, pady=5)

        # Log
        ttk.Label(main_frame, text="Log:").grid(row=8, column=0, sticky=tk.W, pady=5)

        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.log_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Configurar pesos da grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(9, weight=1)

    def add_url(self):
        url = self.url_entry.get().strip()
        if url:
            if url.startswith(('http://', 'https://')):
                self.url_listbox.insert(tk.END, url)
                self.url_entry.delete(0, tk.END)
                self.log(f"URL adicionada: {url}")
            else:
                messagebox.showerror("Erro", "URL inválida! Deve começar com http:// ou https://")
        else:
            messagebox.showwarning("Aviso", "Digite uma URL primeiro!")

    def clear_urls(self):
        self.url_listbox.delete(0, tk.END)
        self.log("Lista de URLs limpa")

    def load_from_file(self):
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo de URLs",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    urls = [linha.strip() for linha in f if linha.strip() and not linha.startswith('#')]

                for url in urls:
                    if url.startswith(('http://', 'https://')):
                        self.url_listbox.insert(tk.END, url)

                self.log(f"{len(urls)} URLs carregadas do arquivo '{filename}'")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler arquivo: {e}")

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Selecionar diretório de saída")
        if directory:
            self.output_dir.set(directory)
            self.log(f"Diretório definido: {directory}")

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def get_format_code(self):
        format_map = {
            'Auto (Melhor disponível)': 'best[ext=mp4]/best',
            '18 (MP4 480p)': '18/best[height<=480]/best',
            '22 (MP4 720p)': '22/best[height<=720]/best',
            '137+140 (MP4 1080p)': '137+140/bestvideo+bestaudio/best',
            'best (Melhor qualidade)': 'bestvideo+bestaudio/best',
            'bestaudio (Apenas áudio)': 'bestaudio/best',
        }
        return format_map.get(self.format_var.get(), 'best[ext=mp4]/best')

    def download_video(self, url, output_dir):
        format_code = self.get_format_code()

        opcoes = {
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format': format_code,
            'merge_output_format': 'mp4',
            'quiet': True,
            'verbose': False,
            'no_warnings': True,
            'retries': 10,
            'fragment_retries': 10,
            'file_access_retries': 5,
            'extractor_retries': 5,
            'socket_timeout': 30,
            'http_chunk_size': 10485760,
            'extractor_args': {'youtube': {'player_client': ['web', 'android', 'ios']}},
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'progress_hooks': [self.progress_hook],
        }

        # Se for áudio, não precisa mesclar
        if 'audio' in format_code:
            opcoes['merge_output_format'] = None

        if self.no_playlist_var.get():
            opcoes['noplaylist'] = True

        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                self.log(f"🔍 Obtendo informações do vídeo: {url}")
                ydl.download([url])
            return True
        except Exception as e:
            self.log(f"❌ Erro: {e}")
            return False

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            self.root.after(0, lambda: self.progress_label.config(text=f"Baixando: {percent} - {speed}"))
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_label.config(text="Processando arquivo..."))

    def start_download(self):
        if self.downloading:
            messagebox.showwarning("Aviso", "Download já em andamento!")
            return

        urls = list(self.url_listbox.get(0, tk.END))
        if not urls:
            messagebox.showwarning("Aviso", "Adicione URLs primeiro!")
            return

        self.downloading = True
        self.cancel_download = False
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress_bar.start()

        # Iniciar download em thread separada
        thread = threading.Thread(target=self.download_thread, args=(urls,))
        thread.daemon = True
        thread.start()

    def download_thread(self, urls):
        output_dir = self.output_dir.get()
        total = len(urls)
        success = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            if self.cancel_download:
                break

            self.root.after(0, lambda i=i, total=total: self.log(f"\n{'='*50}"))
            self.root.after(0, lambda i=i, total=total: self.log(f"📹 Vídeo {i} de {total}"))
            self.root.after(0, lambda: self.log(f"{'='*50}"))

            if self.download_video(url, output_dir):
                success += 1
                self.root.after(0, lambda: self.log("✅ Download concluído!"))
            else:
                failed += 1

            # Atualizar progresso
            self.root.after(0, lambda i=i, total=total, success=success, failed=failed: self.progress_label.config(
                text=f"Progresso: {i}/{total} (Sucesso: {success}, Falhas: {failed})"
            ))

        # Finalizar
        self.root.after(0, self.download_finished, success, failed)

    def download_finished(self, success, failed):
        self.downloading = False
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()

        if self.cancel_download:
            self.log("\n⛔ Download cancelado pelo usuário")
            messagebox.showinfo("Cancelado", "Download cancelado!")
        else:
            message = f"Download concluído!\n\nSucesso: {success}\nFalhas: {failed}"
            self.log(f"\n{'='*50}")
            self.log(message)
            messagebox.showinfo("Concluído", message)

        self.progress_label.config(text="Download concluído")

    def cancel_downloads(self):
        if self.downloading:
            self.cancel_download = True
            self.log("⛔ Cancelando downloads... (pode levar alguns segundos)")
            self.cancel_btn.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
