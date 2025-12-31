import tkinter as tk
from tkinter import ttk, messagebox
from clipper_agent.settings import (
    load_available_models,
    load_settings,
    save_settings,
    add_prompt,
    update_prompt,
    delete_prompt,
    get_prompt_by_name,
    set_default_prompt,
    set_log_level,
)

class ToolTip:
    """シンプルなツールチップ実装"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # ツールチップウィンドウの作成
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # ウィンドウ枠を非表示
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip_window, text=self.text, background="#FFFFDD",
                        relief="solid", borderwidth=1, padding=(5, 2))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def create_tooltip(widget, text):
    """ウィジェットにツールチップを追加するヘルパー関数"""
    return ToolTip(widget, text)

class ClipperAgentConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ClipperAgent Config")
        self.root.geometry("600x450") # ウィンドウサイズ調整

        self.settings_data = load_settings()
        if not isinstance(self.settings_data.get("prompts"), list):
            self.settings_data["prompts"] = []
            
        # 編集モードのフラグと現在編集中のプロンプト名
        self.edit_mode = False
        self.current_prompt_name = None

        # --- スタイル --- (オプション)
        style = ttk.Style()
        style.theme_use('clam') # よりモダンなテーマを選択 (clam, alt, default, classic)

        # --- メインフレーム --- 
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- 全体設定 ---
        general_settings_frame = ttk.LabelFrame(main_frame, text="一般設定", padding="10")
        general_settings_frame.pack(fill=tk.X, pady=(0, 5))

        # ログレベル設定
        ttk.Label(general_settings_frame, text="ログレベル:").pack(side=tk.LEFT, padx=5)
        self.log_level_var = tk.StringVar(value=self.settings_data.get("log_level", "INFO"))
        self.log_level_combo = ttk.Combobox(
            general_settings_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "ERROR"],
            state="readonly",
            width=10
        )
        self.log_level_combo.pack(side=tk.LEFT, padx=5)
        self.log_level_combo.bind("<<ComboboxSelected>>", self.on_log_level_change)
        create_tooltip(self.log_level_combo, "アプリケーションのログ出力レベルを設定します。")

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
        available_models = load_available_models()
        if available_models:
            combo_values = available_models
            self.model_status_var = tk.StringVar(value=".envからモデルリストを読み込みました")
        else:
            combo_values = ["gemini-pro", "gemini-flash"]
            self.model_status_var = tk.StringVar(value=".envが見つからないかAVAILABLE_MODELSが未設定です。デフォルト値を使用します。")

        self.model_id_combo = ttk.Combobox(
            form_frame,
            textvariable=self.model_id_var,
            values=combo_values,
            state="readonly",
        )
        self.model_id_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        if self.model_id_combo["values"]:
            self.model_id_combo.current(0)

        self.model_status_label = ttk.Label(form_frame, textvariable=self.model_status_var, foreground="#666666")
        self.model_status_label.grid(row=3, column=1, padx=5, pady=(0, 5), sticky=tk.W)

        form_frame.columnconfigure(1, weight=1) # EntryとComboboxがウィンドウ幅に追従するように

        # --- ボタン --- 
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=1, padx=5, pady=10, sticky=tk.E)

        self.new_button = ttk.Button(button_frame, text="フォームクリア", command=self.clear_form)
        self.new_button.pack(side=tk.LEFT, padx=5)
        # ツールチップを追加
        create_tooltip(self.new_button, "入力フォームをクリアして新規入力状態にします。保存するには保存ボタンを押してください。")

        self.save_button = ttk.Button(button_frame, text="保存", command=self.save_prompt)
        self.save_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.save_button, "入力内容を新規プロンプトとして保存、または既存プロンプトを更新します。")

        # --- プロンプト一覧 --- 
        list_frame = ttk.LabelFrame(main_frame, text="登録済みプロンプト", padding="10")
        list_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        
        # リストと操作ボタンを含む上部フレーム
        list_content_frame = ttk.Frame(list_frame)
        list_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 削除ボタンを含む下部フレーム
        list_button_frame = ttk.Frame(list_frame)
        list_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.default_button = ttk.Button(list_button_frame, text="デフォルトに設定", command=self.set_default_prompt)
        self.default_button.pack(side=tk.LEFT)
        create_tooltip(self.default_button, "選択したプロンプトをデフォルトとして設定します。")

        self.delete_button = ttk.Button(list_button_frame, text="削除", command=self.delete_selected_prompt)
        self.delete_button.pack(side=tk.RIGHT)
        create_tooltip(self.delete_button, "選択したプロンプトを削除します。")

        self.prompt_listbox = tk.Listbox(list_content_frame, height=8)
        self.prompt_listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        # Listbox用のスクロールバー
        list_scrollbar = ttk.Scrollbar(list_content_frame, orient=tk.VERTICAL, command=self.prompt_listbox.yview)
        self.prompt_listbox['yscrollcommand'] = list_scrollbar.set
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # プロンプト一覧でダブルクリックイベントを追加
        self.prompt_listbox.bind('<Double-1>', self.prompt_listbox_double_click)
        create_tooltip(self.prompt_listbox, "ダブルクリックでプロンプトを編集できます。")

        self.refresh_prompt_list()

    def clear_form(self):
        """フォームをクリアして新規作成モードに設定"""
        self.prompt_name_entry.delete(0, tk.END)
        self.prompt_text_entry.delete("1.0", tk.END)
        if self.model_id_combo['values']:
            self.model_id_combo.current(0)
        self.prompt_name_entry.focus_set() # フォーカスをプロンプト名に
        
        # 編集モードをリセット
        self.edit_mode = False
        self.current_prompt_name = None
        self.save_button.config(text="保存")

    def save_prompt(self):
        """プロンプトの保存または更新"""
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

        if self.edit_mode and self.current_prompt_name:
            # 編集モードの場合は更新
            if update_prompt(self.current_prompt_name, name, text, model):
                messagebox.showinfo("成功", f"プロンプト '{name}' を更新しました。")
                self.settings_data = load_settings()  # 保存後に再読み込み
                self.refresh_prompt_list()
                self.clear_form()
            else:
                messagebox.showerror("エラー", "同名のプロンプトが既に存在するか、更新に失敗しました。")
        else:
            # 新規作成モードの場合は追加
            if add_prompt(name, text, model):
                messagebox.showinfo("成功", f"プロンプト '{name}' を保存しました。")
                self.settings_data = load_settings()  # 保存後に再読み込み
                self.refresh_prompt_list()
                self.clear_form()
            else:
                messagebox.showerror("エラー", f"プロンプト名 '{name}' は既に存在します。別の名前を指定してください。")

    def refresh_prompt_list(self):
        """プロンプト一覧を更新"""
        self.prompt_listbox.delete(0, tk.END)
        prompts = self.settings_data.get("prompts", [])
        if isinstance(prompts, list):
            for i, prompt in enumerate(prompts):
                if isinstance(prompt, dict) and "name" in prompt:
                    display_name = prompt['name']
                    if self.settings_data.get("default_prompt_name") == prompt["name"]:
                        display_name = f"* {display_name}"  # デフォルトを示す
                    self.prompt_listbox.insert(tk.END, f"{i+1}. {display_name} ({prompt.get('model', 'N/A')})")
                else:
                    # 不正な形式のプロンプトデータはスキップまたはエラー表示
                    self.prompt_listbox.insert(tk.END, f"{i+1}. [不正なプロンプトデータ]")
        else:
            # promptsがリストでない場合（通常は起こらないはずだが念のため）
            self.prompt_listbox.insert(tk.END, "プロンプトデータの形式が不正です。")
            
    def prompt_listbox_double_click(self, event):
        """プロンプト一覧でダブルクリックされた時の処理"""
        selected_index = self.prompt_listbox.curselection()
        if not selected_index:
            return
        
        # 選択されたアイテムのインデックスを取得
        prompts = self.settings_data.get("prompts", [])
        if 0 <= selected_index[0] < len(prompts):
            prompt = prompts[selected_index[0]]
            self.load_prompt_for_edit(prompt)
    
    def load_prompt_for_edit(self, prompt):
        """指定されたプロンプトをフォームに読み込む"""
        if not isinstance(prompt, dict) or "name" not in prompt:
            messagebox.showerror("エラー", "不正なプロンプトデータです。")
            return
        
        # フォームをクリア
        self.clear_form()
        
        # プロンプトデータをフォームに設定
        self.prompt_name_entry.insert(0, prompt.get("name", ""))
        self.prompt_text_entry.insert("1.0", prompt.get("text", ""))
        
        # モデルの選択
        model = prompt.get("model", "")
        values = list(self.model_id_combo["values"])
        if model in values:
            self.model_id_combo.current(values.index(model))
        elif values:
            self.model_id_combo.current(0)
        
        # 編集モードに設定
        self.edit_mode = True
        self.current_prompt_name = prompt.get("name", "")
        self.save_button.config(text="更新")
    
    def delete_selected_prompt(self):
        """選択されたプロンプトを削除"""
        selected_index = self.prompt_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("情報", "削除するプロンプトを選択してください。")
            return
        
        # 選択されたアイテムのインデックスを取得
        prompts = self.settings_data.get("prompts", [])
        if 0 <= selected_index[0] < len(prompts):
            prompt = prompts[selected_index[0]]
            prompt_name = prompt.get("name", "")
            
            # 確認ダイアログを表示
            confirm = messagebox.askyesno("確認", f"プロンプト '{prompt_name}' を削除しますか？")
            if not confirm:
                return
            
            # 削除実行
            if delete_prompt(prompt_name):
                messagebox.showinfo("成功", f"プロンプト '{prompt_name}' を削除しました。")
                self.settings_data = load_settings()  # 削除後に再読み込み
                self.refresh_prompt_list()
                
                # 編集中のプロンプトが削除された場合はフォームをクリア
                if self.edit_mode and self.current_prompt_name == prompt_name:
                    self.clear_form()
            else:
                messagebox.showerror("エラー", f"プロンプト '{prompt_name}' の削除に失敗しました。")

    def set_default_prompt(self):
        """選択されたプロンプトをデフォルトとして設定"""
        selected_index = self.prompt_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("情報", "デフォルトに設定するプロンプトを選択してください。")
            return

        prompts = self.settings_data.get("prompts", [])
        if 0 <= selected_index[0] < len(prompts):
            prompt = prompts[selected_index[0]]
            prompt_name = prompt.get("name", "")
            try:
                set_default_prompt(prompt_name)
                messagebox.showinfo("成功", f"'{prompt_name}' をデフォルトプロンプトに設定しました。")
                self.settings_data = load_settings()
                self.refresh_prompt_list()
            except ValueError as e:
                messagebox.showerror("エラー", str(e))

    def on_log_level_change(self, event):
        """ログレベルが変更された時の処理"""
        new_level = self.log_level_var.get()
        try:
            set_log_level(new_level)
            self.settings_data = load_settings() # 設定を再読み込み
            # messagebox.showinfo("成功", f"ログレベルを {new_level} に変更しました。") # 頻繁に変更するものではないかもしれないが、確認はあってもいい。今回は静かに保存。
        except ValueError as e:
             messagebox.showerror("エラー", str(e))


if __name__ == '__main__':
    # このファイル単体で実行する場合（テスト用）
    # clipper_agent.settings で初期設定が書き込まれることを確認してから実行すると良い
    root = tk.Tk()
    app = ClipperAgentConfigApp(root)
    root.mainloop()
