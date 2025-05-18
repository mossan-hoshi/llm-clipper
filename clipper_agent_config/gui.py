import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .settings_manager import load_settings, save_settings, add_prompt

class ClipperAgentConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClipperAgent Config")
        self.root.geometry("600x450") # ウィンドウサイズ調整

        self.settings_data = load_settings()
        if not isinstance(self.settings_data.get("prompts"), list):
            self.settings_data["prompts"] = []

        # --- スタイル --- (オプション)
        style = ttk.Style()
        style.theme_use('clam') # よりモダンなテーマを選択 (clam, alt, default, classic)

        # --- メインフレーム --- 
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- プロンプト編集フォーム --- 
        form_frame = ttk.LabelFrame(main_frame, text="プロンプト編集", padding="10")
        form_frame.pack(fill=tk.X, pady=5)

        ttk.Label(form_frame, text="プロンプト名:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.prompt_name_entry = ttk.Entry(form_frame, width=40)
        self.prompt_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(form_frame, text="プロンプト本文:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        self.prompt_text_entry = tk.Text(form_frame, width=40, height=5, wrap=tk.WORD)
        self.prompt_text_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        # Textウィジェット用のスクロールバー
        prompt_text_scrollbar = ttk.Scrollbar(form_frame, orient=tk.VERTICAL, command=self.prompt_text_entry.yview)
        self.prompt_text_entry['yscrollcommand'] = prompt_text_scrollbar.set
        prompt_text_scrollbar.grid(row=1, column=2, sticky=tk.NS, pady=5)

        ttk.Label(form_frame, text="利用モデル:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.model_id_var = tk.StringVar()
        # ステップ1では固定値
        self.model_id_combo = ttk.Combobox(form_frame, textvariable=self.model_id_var, 
                                           values=["gemini-pro", "gemini-flash"], state="readonly")
        self.model_id_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        if self.model_id_combo['values']:
             self.model_id_combo.current(0) # デフォルト選択

        form_frame.columnconfigure(1, weight=1) # EntryとComboboxがウィンドウ幅に追従するように

        # --- ボタン --- 
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)

        self.new_button = ttk.Button(button_frame, text="新規作成", command=self.clear_form)
        self.new_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(button_frame, text="保存", command=self.save_prompt)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # --- プロンプト一覧 --- 
        list_frame = ttk.LabelFrame(main_frame, text="登録済みプロンプト", padding="10")
        list_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        self.prompt_listbox = tk.Listbox(list_frame, height=8)
        self.prompt_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0,5))
        # Listbox用のスクロールバー
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.prompt_listbox.yview)
        self.prompt_listbox['yscrollcommand'] = list_scrollbar.set
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_prompt_list()

    def clear_form(self):
        self.prompt_name_entry.delete(0, tk.END)
        self.prompt_text_entry.delete("1.0", tk.END)
        if self.model_id_combo['values']:
            self.model_id_combo.current(0)
        self.prompt_name_entry.focus_set() # フォーカスをプロンプト名に

    def save_prompt(self):
        name = self.prompt_name_entry.get().strip()
        text = self.prompt_text_entry.get("1.0", tk.END).strip()
        model = self.model_id_var.get()

        if not name:
            messagebox.showerror("エラー", "プロンプト名を入力してください。")
            return
        if not text:
            messagebox.showerror("エラー", "プロンプト本文を入力してください。")
            return
        if not model:
            messagebox.showerror("エラー", "利用モデルを選択してください。")
            return

        # ステップ1では単純に追加（重複チェックはステップ5）
        if add_prompt(name, text, model):
            messagebox.showinfo("成功", f"プロンプト '{name}' を保存しました。")
            self.settings_data = load_settings() # 保存後に再読み込み
            self.refresh_prompt_list()
            self.clear_form()
        else:
            # add_promptがFalseを返すのは現状では想定していないが、将来の重複チェック用
            messagebox.showerror("エラー", f"プロンプト '{name}' の保存に失敗しました。") 

    def refresh_prompt_list(self):
        self.prompt_listbox.delete(0, tk.END)
        prompts = self.settings_data.get("prompts", [])
        if isinstance(prompts, list):
            for i, prompt in enumerate(prompts):
                if isinstance(prompt, dict) and "name" in prompt:
                    self.prompt_listbox.insert(tk.END, f"{i+1}. {prompt['name']} ({prompt.get('model', 'N/A')})")
                else:
                    # 不正な形式のプロンプトデータはスキップまたはエラー表示
                    self.prompt_listbox.insert(tk.END, f"{i+1}. [不正なプロンプトデータ]")
        else:
            # promptsがリストでない場合（通常は起こらないはずだが念のため）
            self.prompt_listbox.insert(tk.END, "プロンプトデータの形式が不正です。")


if __name__ == '__main__':
    # このファイル単体で実行する場合（テスト用）
    # settings_manager.py で初期設定が書き込まれることを確認してから実行すると良い
    root = tk.Tk()
    app = ClipperAgentConfigApp(root)
    root.mainloop()
