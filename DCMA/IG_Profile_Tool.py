import customtkinter as ctk
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired
import pyotp
import time
import random
import threading
from tkinter import scrolledtext

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class IGTool(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instagram Profile Editor Tool - by Grok")
        self.geometry("980x740")

        self.accounts = []
        self.is_running = False

        # Title
        ctk.CTkLabel(self, text="Instagram Profile Editor Tool", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        # Load file
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(file_frame, text="File accounts.txt:").pack(side="left", padx=10)
        self.file_entry = ctk.CTkEntry(file_frame, width=450)
        self.file_entry.pack(side="left", padx=5)
        self.file_entry.insert(0, "accounts.txt")
        ctk.CTkButton(file_frame, text="Load Accounts", command=self.load_accounts).pack(side="left", padx=10)

        # Thông tin đổi
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=15, padx=20, fill="x")
        ctk.CTkLabel(info_frame, text="New Bio:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.bio_entry = ctk.CTkEntry(info_frame, width=680)
        self.bio_entry.grid(row=0, column=1, padx=10, pady=5)
        self.bio_entry.insert(0, "Bio mới test tool 🔥 2026")

        ctk.CTkLabel(info_frame, text="New Website:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.website_entry = ctk.CTkEntry(info_frame, width=680)
        self.website_entry.grid(row=1, column=1, padx=10, pady=5)
        self.website_entry.insert(0, "https://yourwebsite.com")

        ctk.CTkLabel(info_frame, text="New Full Name:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.name_entry = ctk.CTkEntry(info_frame, width=680)
        self.name_entry.grid(row=2, column=1, padx=10, pady=5)
        self.name_entry.insert(0, "Tên Mới")

        # Log
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(pady=15, padx=20, fill="both", expand=True)
        ctk.CTkLabel(log_frame, text="Log:").pack(anchor="w", padx=10)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, bg="#1e1e1e", fg="#00ff88", font=("Consolas", 10))
        self.log_text.pack(padx=10, pady=5, fill="both", expand=True)

        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=15)
        self.start_btn = ctk.CTkButton(btn_frame, text="▶ START", width=170, height=45, fg_color="green", command=self.start_process)
        self.start_btn.pack(side="left", padx=30)
        self.stop_btn = ctk.CTkButton(btn_frame, text="■ STOP", width=170, height=45, fg_color="red", command=self.stop_process, state="disabled")
        self.stop_btn.pack(side="left", padx=30)

        self.log("Tool sẵn sàng. Load file accounts.txt trước khi chạy.")

    def log(self, message):
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")

    def load_accounts(self):
        file_path = self.file_entry.get().strip()
        try:
            self.accounts = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2:
                        acc = {
                            "username": parts[0],
                            "password": parts[1],
                            "twofa_secret": parts[3] if len(parts) > 3 and parts[3] else None
                        }
                        self.accounts.append(acc)
            self.log(f"✅ Đã load {len(self.accounts)} tài khoản!")
        except Exception as e:
            self.log(f"❌ Lỗi load file: {e}")

    def start_process(self):
        if not self.accounts:
            self.log("❗ Vui lòng load file accounts.txt trước!")
            return
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self.run_process, daemon=True).start()

    def stop_process(self):
        self.is_running = False
        self.log("⛔ Tool đã dừng!")

    def run_process(self):
        cl = Client()

        for i, acc in enumerate(self.accounts, 1):
            if not self.is_running: break

            self.log(f"[{i}/{len(self.accounts)}] Đang xử lý: {acc['username']}")

            login_success = False
            for attempt in range(3):   # Thử tối đa 3 lần
                try:
                    self.log(f"   → Lần {attempt+1}: Login bằng UID + Pass + 2FA...")

                    if acc["twofa_secret"]:
                        totp = pyotp.TOTP(acc["twofa_secret"])
                        code = totp.now()
                        self.log(f"   2FA Code: {code}")
                        cl.login(acc["username"], acc["password"], verification_code=code)
                    else:
                        cl.login(acc["username"], acc["password"])

                    self.log("   ✅ Login thành công!")
                    login_success = True
                    break

                except LoginRequired:
                    self.log("   ⚠️  LoginRequired → Thử lại sau 10s...")
                    time.sleep(10)
                except TwoFactorRequired:
                    self.log("   ⚠️  Cần 2FA thủ công → Vui lòng nhập code từ app Authenticator:")
                    code = input("Nhập mã 6 số 2FA: ").strip()   # tạm thời dùng input, sau có thể làm GUI
                    cl.login(acc["username"], acc["password"], verification_code=code)
                    login_success = True
                    break
                except Exception as e:
                    self.log(f"   ❌ Lỗi login: {e}")
                    time.sleep(random.uniform(8, 15))

            if not login_success:
                self.log(f"   ❌ Bỏ qua acc {acc['username']} sau 3 lần thử\n")
                continue

            # Đổi profile
            try:
                cl.account_edit(
                    biography=self.bio_entry.get(),
                    full_name=self.name_entry.get(),
                    website=self.website_entry.get(),
                    external_url=self.website_entry.get()
                )
                self.log(f"   ✅ Đổi website + bio thành công!")
            except LoginRequired:
                self.log("   ❌ LoginRequired khi đổi profile → Acc có thể bị Instagram chặn tạm thời")
            except Exception as e:
                self.log(f"   ❌ Lỗi đổi profile: {e}")

            # Delay
            delay = random.uniform(20, 45)
            self.log(f"   Nghỉ {delay:.1f} giây trước acc tiếp theo...\n")
            time.sleep(delay)

        self.log("🎉 Hoàn thành chạy tool!")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.is_running = False


if __name__ == "__main__":
    app = IGTool()
    app.mainloop()