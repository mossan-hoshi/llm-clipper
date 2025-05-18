import tkinter as tk
from clipper_agent_config.gui import ClipperAgentConfigApp

def main():
    root = tk.Tk()
    app = ClipperAgentConfigApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
