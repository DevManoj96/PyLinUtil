import tkinter as tk
from tkinter import messagebox, simpledialog
import shutil
import subprocess
import threading
import speedtest
import requests


default_font = ("Segoe UI", 12)


def detect_package_manager():
    managers = ['apt', 'dnf', 'yum', 'zypper', 'pacman', 'xbps-install', 'rpm', 'emerge', 'apk']
    for mgr in managers:
        if shutil.which(mgr):
            return mgr
    return ""

pkgManager = detect_package_manager()

class PyLinUtil:
    def __init__(self, root):
        self.root = root
        self.root.title("PyLinUtil")
        self.root.geometry('640x480')
        self.root.resizable(False, False)

        self.popups = []
        self.labels = []
        self.listboxes = []
        self.buttons = []

        self.IsAppPopupAvail = False
        self.IsSysToolsPopupAvail = False
        self.isNetSpeedCheckPopupAvail = False
        self.isSysCleanupPopupAvail = False
        self.isPublicIPCheckAvail = False
        self.isSysUpdatePopupAvail = False

        self.isThemedark = False

        self.topHeading = tk.Label(self.root, text="PyLinUtil", font=("Segoe UI", 20), width=20, height=3)
        self.topHeading.pack(padx=5, pady=5)
        self.labels.append(self.topHeading)

        self.appInstall_btn = tk.Button(self.root, text="Install Apps", command=self.app_installer, width=9, height=2, font=default_font)
        self.appInstall_btn.pack(padx=5, pady=5,)
        self.buttons.append(self.appInstall_btn)

        self.sysTools_btn = tk.Button(self.root, text="System Tools", command=self.sys_tools, width=9, height=2, font=default_font)
        self.sysTools_btn.pack(padx=5, pady=5)
        self.buttons.append(self.sysTools_btn)

        self.toggleTheme_btn = tk.Button(self.root, text="Toggle Theme", command=self.toggleTheme, width=9, height=2, font=default_font)
        self.toggleTheme_btn.pack(padx=5, pady=5)
        self.buttons.append(self.toggleTheme_btn)

        self.exit_btn = tk.Button(self.root, text="Exit", command=self.root.quit, width=9, height=2, font=default_font)
        self.exit_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exit_btn)

    
    def app_installer(self):
        if self.IsAppPopupAvail:
            self.appPopup.lift()
            return

        self.IsAppPopupAvail = True

        self.appPopup = tk.Toplevel(self.root)
        self.appPopup.title("Install Apps")
        self.appPopup.geometry('500x600')
        self.appPopup.resizable(False, False)
        self.popups.append(self.appPopup)
        
        self.pkgList = tk.Listbox(self.appPopup, width=50, height=20, font=default_font)
        self.pkgList.pack(padx=5, pady=5)
        self.listboxes.append(self.pkgList)
        
        
        selectedPkgs = []
        def select_pkg():
            selection = self.pkgList.curselection()
            if not selection:
                messagebox.showerror("Input Error", "Select package to install.", parent=self.appPopup)
                return
            
            index = selection[0]
            tick_sign = "✔️"
            old_value = self.pkgList.get(index)
            if '=' in old_value:
                return
        
            
            if tick_sign in old_value:
                self.pkgList.delete(index)
                new_value = ""
                for i in old_value.strip():
                    if i in tick_sign:
                        continue
                    new_value += i
                self.pkgList.insert(index, new_value)

                deselect_pkg(new_value)
                return
            
            self.pkgList.delete(index)
            self.pkgList.insert(index, f"{old_value}            {tick_sign}")
            
            pKg = ""
            for i in old_value:
                if i in "0123456789. ":
                    continue
                pKg += i

            if pKg in selectedPkgs:
                pass
            else:
                selectedPkgs.append(pKg)

        def deselect_pkg(pkg):
            pKg = ""
            for i in pkg:
                if i in "0123456789. ":
                    continue
                pKg += i
            selectedPkgs.remove(pKg)

        def pkginstaller():
            self.installPkg_btn.config(state='disabled')
            pkginstall = {
                'apt': 'sudo -S apt install ',
                'dnf': 'sudo -S dnf install ',
                'yum': 'sudo -S yum install ',
                'zypper': 'sudo -S zypper install ',
                'pacman': 'sudo -S pacman -S ',
                'xbps-install': 'sudo -S xbps-install -S ',
                'rpm': 'sudo -S rpm -i ',
                'emerge': 'sudo -S emerge ',
                'apk': 'sudo -S apk add ',
            }
            try:
                passwd = simpledialog.askstring("Authentication Required", "Enter your sudo password:", parent=self.appPopup, show="*")
                
                if not passwd:
                    messagebox.showwarning("Warning", "Password is required for installation.", parent=self.appPopup)
                    self.installPkg_btn.config(state='normal')
                    return

                if not selectedPkgs:
                    messagebox.showerror("Error", "Nothing to install, Select packages first.", parent=self.appPopup)
                    self.installPkg_btn.config(state='normal')
                    return

                if pkgManager not in pkginstall:
                    messagebox.showerror("Error", f"Unsupported package manager: {pkgManager}", parent=self.appPopup)
                    self.installPkg_btn.config(state='normal')
                    return
            except:
                self.installPkg_btn.config(state='normal')
                return


            print(f"Installing essential packges.")
            for pkg in ["xterm", "flatpak"]:
                command = f"{pkginstall[pkgManager]} {pkg}"
                subprocess.run(command, shell=True, capture_output=True, text=True, input=f"{passwd}\n")

            print(f"SelectedPkgs: {selectedPkgs}")

            for pkg in selectedPkgs:
                try:
                    command = f"{pkginstall[pkgManager]} {pkg}"

                    result = subprocess.run(command, shell=True, capture_output=True, text=True, input=f"{passwd}\n")
                    print(f"Installing: {pkg}")

                    if result.returncode == 0:
                        print(f"Installed: {pkg}")                
                    else:
                        messagebox.showerror("Error", f"Failed to install {pkg}\n{result.stderr}", parent=self.appPopup)

                except Exception as e:
                    messagebox.showerror("Error", f"{pkg}: {e}", parent=self.appPopup)
            self.installPkg_btn.config(state='normal')

        def pkginstallThread():
            thread = threading.Thread(target=pkginstaller)
            thread.start()  
        
        def exit_appInstall():
            self.IsAppPopupAvail = False
            self.appPopup.destroy()
        
        packages = [
            ["Discord", "Jitsi", "Signal", "Slack", "Telegram", "Thunderbird", "ZapZap", "Zoom"], # Communication Apps
            
            ["Github Desktop", "JetBrains Toolbook", "Meld", "Neovim", "Ngrok", "Sublime Text", "VS Code", "VS Codium", "Zed"], # Developer Apps

            ["WPS Office", "FreeOffice", "LibreOffice", "OnlyOffice"], # Office Suites

            ["Evince", "MuPDF", "PDF Studio", "PDF Studio Viewer"], # PDF Suites

            ["Brave", "Google Chrome", "Chromium", "LibreWolf", "Lynx", "Firefox", "Thorium", "Zen Browser", "Vivaldi", "Tor Browser", "Waterfox", "opera"], # Web Browser

            ["Wine", "Bottles", "Steam", "Lutris", "Heroic Game Launcher"], # Gaming utils 

            ["Alacritty", "Android Debloater", "Zsh", "Bash Prompt", "Docker", "Ghostty", "Podman", "Podman-compose", "Fastfetch", "Cmatrix", "Cowsay", "Sl", "btop", "htop", "Rofi", "Flatpak", "Python", "Java"], # Others
        ]
                
        # Insert Communication apps in listbox
        self.pkgList.config(state='normal')
        self.pkgList.insert(tk.END, f"{"="*13} Communication Apps {"="*13}")
        for idx, pkg in enumerate(packages[0], start=1):
            self.pkgList.insert(tk.END, f"{idx}. {pkg}")
        

        # Insert Developer apps in listbox
        self.pkgList.config(state='normal')
        self.pkgList.insert(tk.END, f"{"="*13} Developer Apps {"="*13}")
        for idx, pkg in enumerate(packages[1], start=1):
            self.pkgList.insert(tk.END, f"{idx}. {pkg}")
        

        # Insert Office suites in listbox
        self.pkgList.config(state='normal')
        self.pkgList.insert(tk.END, f"{"="*13} Office Suites {"="*13}") 
        for idx, pkg in enumerate(packages[2], start=1):
            self.pkgList.insert(tk.END, f"{idx}. {pkg}")
        

        # Insert PDF suites in listbox
        self.pkgList.config(state='normal')
        self.pkgList.insert(tk.END, f"{"="*13} PDF Suites {"="*13}")
        for idx, pkg in enumerate(packages[3], start=1):
            self.pkgList.insert(tk.END, f"{idx}. {pkg}")
        

        # Insert Web browsers in listbox
        self.pkgList.config(state='normal')
        self.pkgList.insert(tk.END, f"{"="*13} Web Browser {"="*13}")
        for idx, pkg in enumerate(packages[4], start=1):
            self.pkgList.insert(tk.END, f"{idx}. {pkg}")
        

        # Insert Other softwares in listbox
        self.pkgList.config(state='normal')
        self.pkgList.insert(tk.END, f"{"="*13} Other Softwares {"="*13}")
        for idx, pkg in enumerate(packages[5], start=1):
            self.pkgList.insert(tk.END, f"{idx}. {pkg}")
        
        

        self.selPkg_btn = tk.Button(self.appPopup, text="Select/Deselect", command=select_pkg, width=9, height=1, font=default_font)
        self.selPkg_btn.pack(padx=5, pady=5)
        self.buttons.append(self.selPkg_btn)

        self.installPkg_btn = tk.Button(self.appPopup, text="Install", command=pkginstallThread, width=9, height=1, font=default_font)
        self.installPkg_btn.pack(padx=5, pady=5)
        self.buttons.append(self.installPkg_btn)

        self.exitAppInstall_btn = tk.Button(self.appPopup, text="Exit", command=exit_appInstall, width=9, height=1, font=default_font)
        self.exitAppInstall_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exitAppInstall_btn)

    def sys_tools(self):
        if self.IsSysToolsPopupAvail:
            self.sysToolsPopup.lift()
            return

        self.IsSysToolsPopupAvail = True
        
        self.sysToolsPopup = tk.Toplevel(self.root)
        self.sysToolsPopup.title("System Tools")
        self.sysToolsPopup.geometry('450x460')
        self.sysToolsPopup.resizable(False, False)
        self.popups.append(self.sysToolsPopup)

        def netCheck():
            self.netCheck_btn.config(state='disabled')
            def start_checking():
                try:
                    result = subprocess.run(["ping", "-c", "4", "www.google.com"], text=False, shell=False, capture_output=False)
                    
                    if result.returncode == 0:
                        messagebox.showinfo("Internet Check", "✅ Your internet is working properly.", parent=self.sysToolsPopup)
                        self.netCheck_btn.config(state='normal')
                    else:
                        messagebox.showinfo("Internet Check", "❌ Your internet is not working properly.")
                        self.netCheck_btn.config(state='normal')

                except Exception as e:
                    messagebox.showerror("Error", f"{e}", parent=self.sysToolsPopup)
                    self.netCheck_btn.config(state='normal')

            thread = threading.Thread(target=start_checking)
            thread.start()
                      

        def netspeedcheck():
            self.netSpeedCheck()

        def publicIpCheck():
            self.publicIPCheck()

        def sysupdate():
            self.sysUpdate()
            
        def sysCleanup():
            self.sysCleanup()

        def exit_sysTools():
            self.IsSysToolsPopupAvail = False
            self.sysToolsPopup.destroy()

        self.netCheck_btn = tk.Button(self.sysToolsPopup, text="Internet Check", command=netCheck, width=9, height=2, font=default_font)
        self.netCheck_btn.pack(padx=5, pady=5)
        self.buttons.append(self.netCheck_btn)

        self.netSpeedCheck_btn = tk.Button(self.sysToolsPopup, text="Speed Check", command=netspeedcheck, width=9, height=2, font=default_font)
        self.netSpeedCheck_btn.pack(padx=5, pady=5)
        self.buttons.append(self.netSpeedCheck_btn)

        self.publicIPCheck_btn = tk.Button(self.sysToolsPopup, text="Public IP", command=publicIpCheck, width=9, height=2, font=default_font)
        self.publicIPCheck_btn.pack(padx=5, pady=5)
        self.buttons.append(self.publicIPCheck_btn)

        self.sysUpdate_btn = tk.Button(self.sysToolsPopup, text="System Update", command=sysupdate, width=9, height=2, font=default_font)
        self.sysUpdate_btn.pack(padx=5, pady=5)
        self.buttons.append(self.sysUpdate_btn)

        self.sysCleanup_btn = tk.Button(self.sysToolsPopup, text="System Cleanup", command=sysCleanup, width=9, height=2, font=default_font)
        self.sysCleanup_btn.pack(padx=5, pady=5)
        self.buttons.append(self.sysCleanup_btn)


        self.exitSysTools_btn = tk.Button(self.sysToolsPopup, text="Exit", command=exit_sysTools, width=9, height=2, font=default_font)
        self.exitSysTools_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exitSysTools_btn)
        
    def netSpeedCheck(self):
        if self.isNetSpeedCheckPopupAvail:
            self.netSpeedCheckPopup.lift()
            return
        
        self.isNetSpeedCheckPopupAvail = True

        self.netSpeedCheckPopup = tk.Toplevel(self.sysToolsPopup)
        self.netSpeedCheckPopup.title("Internet Speed Check")
        self.netSpeedCheckPopup.geometry('450x460')
        self.netSpeedCheckPopup.resizable(False, False)
        self.popups.append(self.netSpeedCheckPopup)

        st = speedtest.Speedtest()

        def run_check():
            try:
                self.netSpeedLabel.config(text="Please wait...")

                st.get_best_server()
    
                self.netSpeedResult.insert(tk.END, f"{"="*13} Internet Speed Check {"="*13}")
                self.netSpeedResult.insert(tk.END, f"Download Speed: {st.download() / 1000000:.2f} Mbps")
                self.netSpeedResult.insert(tk.END, f"Upload Speed: {st.upload() / 1000000:.2f} Mbps")
                self.netSpeedResult.insert(tk.END, f"Ping: {st.results.ping:.2f} ms")

                self.netSpeedLabel.config(text="Done.")            
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

        def exit_netSpeedCheck():
            self.isNetSpeedCheckPopupAvail = False
            self.netSpeedCheckPopup.destroy()

        self.netSpeedResult = tk.Listbox(self.netSpeedCheckPopup, width=50, height=15, font=default_font)
        self.netSpeedResult.pack(padx=5, pady=5)
        self.listboxes.append(self.netSpeedResult)

        self.netSpeedLabel = tk.Label(self.netSpeedCheckPopup, text="", font=default_font)
        self.netSpeedLabel.pack(padx=5, pady=5)
        self.labels.append(self.netSpeedLabel)

        self.exitNetSpeedCheck_btn = tk.Button(self.netSpeedCheckPopup, text="Exit", command=exit_netSpeedCheck, width=9, height=2, font=default_font)
        self.exitNetSpeedCheck_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exitNetSpeedCheck_btn)

        thread = threading.Thread(target=run_check)
        thread.start()        

    def publicIPCheck(self):
        if self.isPublicIPCheckAvail:
            self.publicIPCheckPopup.lift()
            return
        
        self.isPublicIPCheckAvail = True

        self.publicIPCheckPopup = tk.Toplevel(self.sysToolsPopup)
        self.publicIPCheckPopup.title("Public IP Check")
        self.publicIPCheckPopup.geometry('450x460')
        self.publicIPCheckPopup.resizable(False, False)
        self.popups.append(self.publicIPCheckPopup)

        def run_check():
            try:
                self.publicIPCheckResult.insert(tk.END, f"{"="*13} Public IP Check {"="*13}")
                response = requests.get('https://ipinfo.io/json')
                response.raise_for_status()
                data = response.json()

                self.publicIPCheckResult.insert(tk.END, f"IP: {data['ip']}")
                self.publicIPCheckResult.insert(tk.END, f"City: {data['city']}")
                self.publicIPCheckResult.insert(tk.END, f"Region: {data['region']}")
                self.publicIPCheckResult.insert(tk.END, f"Country: {data['country']}")
                self.publicIPCheckResult.insert(tk.END, f"Location: {data['loc']}")
                self.publicIPCheckResult.insert(tk.END, f"Organization: {data['org']}")
                self.publicIPCheckResult.insert(tk.END, f"Postal: {data['postal']}")
                self.publicIPCheckResult.insert(tk.END, f"Timezone: {data['timezone']}")

            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"{e}")

        def exit_publicIPCheck():
            self.isPublicIPCheckAvail = False
            self.publicIPCheckPopup.destroy()

        self.publicIPCheckResult = tk.Listbox(self.publicIPCheckPopup, width=50, height=15, font=default_font)
        self.publicIPCheckResult.pack(padx=5, pady=5)
        self.listboxes.append(self.publicIPCheckResult)

        self.exitPublicIPCheck_btn = tk.Button(self.publicIPCheckPopup, text="Exit", command=exit_publicIPCheck, width=9, height=2, font=default_font)
        self.exitPublicIPCheck_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exitPublicIPCheck_btn)

        thread = threading.Thread(target=run_check)
        thread.start()
        
    def sysUpdate(self):
        self.sysUpdate_btn.config(state='disabled')
        if self.isSysUpdatePopupAvail:
            self.sysUpdatePopup.lift()
            return

        self.isSysUpdatePopupAvail = True

        self.sysUpdatePopup = tk.Toplevel(self.sysToolsPopup)
        self.sysUpdatePopup.title("System Update")
        self.sysUpdatePopup.geometry('450x460')       
        self.sysUpdatePopup.resizable(False, False)
        self.popups.append(self.sysUpdatePopup) 

        def run_update():
            passwd = simpledialog.askstring("Authentication Required", "Enter your sudo password:", parent=self.sysUpdatePopup, show="*")
            
            if not passwd:
                messagebox.showwarning("Warning", "Password is required for installation.", parent=self.sysUpdatePopup)
                exit_sysUpdate()
                return

            if pkgManager:
                commands = {
                    'apt' : [
                        "sudo -S apt update -y",
                        "sudo -S apt full-upgrade -y",
                        "sudo -S apt autoremove --purge -y",
                        "sudo -S apt autoclean -y",
                    ],

                    'dnf' : [
                        "sudo -S dnf upgrade --refresh -y",
                        "sudo -S dnf autoremove -y"
                    ],

                    'yum' : [
                        "sudo -S yum update -y",
                        "sudo -S autoremove -y"
                    ],

                    'zypper' : [
                        "sudo -S zypper refresh",
                        "sudo -S zypper update -y",
                        "sudo -S zypper clean -a"
                    ],

                    'pacman' : [
                        "sudo -S pacman -Sy archlinux-keyring",
                        "sudo -S pacman -Syu --noconfirm"
                    ],

                    'xbps-install' : [
                        "sudo -S xbps-install -Syu"
                    ],

                    'rpm' : [
                        "sudo -S rpm -Uvh --replacepkgs --replacefiles *.rpm"
                    ],

                    'emerge' : [
                        "sudo -S emerge --sync",
                        "sudo -S emerge -uUDN @world",
                        "sudo -S emerge --depclean"
                    ],

                    'apk' : [
                        "sudo -S apk update",
                        "sudo -S apk upgrade"
                    ],
                }

                for cmd in commands[pkgManager]:
                    try:
                        self.sysUpdateResult.insert(tk.END, f"Running: {cmd}")
                        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, input=f"{passwd}\n")

                        if result.returncode == 0:
                            self.sysUpdateResult.insert(tk.END, f"Done: {cmd}")
                        else:
                            self.sysUpdateResult.insert(tk.END, f"[!]: {cmd}")
                            continue

                    except Exception as e:
                        self.sysUpdateResult.insert(tk.END, f"[Error]: {e}")
                        continue
            else:
                messagebox.showwarning("Warning", "Unkown package manager detected.", parent=self.sysUpdatePopup)
                exit_sysUpdate()
                return


        def exit_sysUpdate():
            self.isSysUpdatePopupAvail = False
            self.sysUpdate_btn.config(state='normal')
            self.sysUpdatePopup.destroy()

        self.sysUpdateResult = tk.Listbox(self.sysUpdatePopup, width=50, height=15, font=default_font)
        self.sysUpdateResult.pack(padx=5, pady=5)
        self.listboxes.append(self.sysUpdateResult)

        self.exitSysUpdate_btn = tk.Button(self.sysUpdatePopup, text="Exit", command=exit_sysUpdate, width=9, height=2, font=default_font)
        self.exitSysUpdate_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exitSysUpdate_btn)

        thread = threading.Thread(target=run_update)
        thread.start()

    def sysCleanup(self):
        if self.isSysCleanupPopupAvail:
            self.sysCleanupPopup.lift()
            return

        self.isSysCleanupPopupAvail = True       

        self.sysCleanupPopup = tk.Toplevel(self.sysToolsPopup)
        self.sysCleanupPopup.title("System Cleanup")
        self.sysCleanupPopup.geometry('450x460')
        self.sysCleanupPopup.resizable(False, False)
        self.popups.append(self.sysCleanupPopup)

        def run_cleanup():            
            passwd = simpledialog.askstring("Authentication Required", "Enter your sudo password:", parent=self.sysCleanupPopup, show="*")
            
            if not passwd:
                messagebox.showwarning("Warning", "Password is required for installation.", parent=self.sysCleanupPopup)
                exit_sysCleanup()
                return


            if pkgManager:
                commands = {
                    'apt' : [
                        "sudo -S apt autoremove --purge -y",
                        "sudo -S apt autoclean -y",
                        "sudo -S apt clean -y",
                        "sudo -S journalctl --vacuum-time=3d",
                        "sudo -S rm -rf /var/log/* /var/cache/*",
                        "sudo -S dpkg --configure -a",
                        "sudo -S apt -f install",
                    ],

                    'dnf' : [
                        "sudo -S dnf autoremove -y",
                        "sudo -S dnf clean all",
                        "sudo -S rm -rf /var/cache/dnf",
                        "sudo -S journalctl --vacuum-time=3d",
                        "sudo -S rm -rf /var/log/*",
                    ],

                    'yum' : [
                        "sudo -S yum autoremove -y",
                        "sudo -S yum clean all",
                        "sudo -S rm -rf /var/cache/yum",
                        "sudo -S journalctl --vacuum-time=3d",
                        "sudo -S rm -rf /var/log/*",
                    ],

                    'zypper' : [
                        "sudo -S zypper rm -u $(zypper packages --orphaned | awk 'NR>2 {print $3}')",
                        "sudo -S zypper clean -a",
                        "sudo -S rm -rf /var/cache/zypp",
                        "sudo -S journalctl --vacuum-time=3d",
                        "sudo -S rm -rf /var/log/*",
                    ],

                    'pacman' : [
                        "sudo -S pacman -Rns $(pacman -Qtdq) 2>/dev/null",
                        "sudo -S pacman -Sc --noconfirm",
                        "sudo -S paccache -r", 
                        "sudo -S journalctl --vacuum-time=3d",
                        "sudo -S rm -rf /var/log/*",
                    ],

                    'xbps-install' : [
                        "sudo -S xbps-remove -Oo",
                        "sudo -S xbps-remove -o",
                        "sudo -S xbps-remove -Rns $(xbps-query -p pkgver -O)",
                        "sudo -S rm -rf /var/cache/xbps",
                        "sudo -S journalctl --vacuum-time=3d",
                        "sudo -S rm -rf /var/log/*",
                    ],

                    'rpm' : [
                        "sudo -S rpm --rebuilddb",
                        "sudo -S rpm -qa | grep -v $(rpm -qa) | xargs sudo rpm -e --nodeps",
                        "sudo -S rm -rf /var/lib/rpm/__db*",
                        "sudo -S rpm --initdb",
                        "sudo -S rm -rf /var/cache/*",
                        "sudo -S journalctl --vacuum-time=3d",
                    ],

                    'emerge' : [
                        "sudo -S emerge --depclean",
                        "sudo -S eclean-dist --deep",
                        "sudo -S eclean-pkg --deep",
                        "sudo -S rm -rf /var/log/*",
                        "sudo -S journalctl --vacuum-time=3d",
                    ],

                    'apk' : [
                        "sudo -S apk cache clean",
                        "sudo -S apk cache -v",
                        "sudo -S apk del $(apk info -o)",
                        "sudo -S rm -rf /var/cache/apk/*",
                        "sudo -S rm -rf /var/log/*",
                    ],
                }
                    
                for cmd in commands[pkgManager]:
                    try:
                        self.sysCleanupResult.insert(tk.END, f"Running: {cmd}")
                        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, input=f"{passwd}\n")

                        if result.returncode == 0:
                            self.sysCleanupResult.insert(tk.END, f"Done: {cmd}")
                        else:
                            self.sysCleanupResult.insert(tk.END, f"[!]: {cmd}")
                            continue

                    except Exception as e:
                        self.sysCleanupResult.insert(tk.END, f"[Error]: {e}")
                        continue
            else:
                commands = [
                    "sudo -S rm -rf /home/$USER/.cache/*",
                    "sudo -S rm -rf /tmp/*",
                    "sudo -S journalctl --vacuum-size=100M"
                ]

                for cmd in commands:
                    try:
                        self.sysCleanupResult.insert(tk.END, f"Running: {cmd}")
                        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, input=f"{passwd}\n")

                        if result.returncode == 0:
                            self.sysCleanupResult.insert(tk.END, f"Done: {cmd}")
                        else:
                            self.sysCleanupResult.insert(tk.END, f"[!]: {cmd}")
                            continue
                    except Exception as e:
                        self.sysCleanupResult.insert(tk.END, f"[Error]: {e}")
                        continue
                    


        def exit_sysCleanup():
            self.isSysCleanupPopupAvail = False
            self.sysCleanupPopup.destroy()

        self.sysCleanupResult = tk.Listbox(self.sysCleanupPopup, width=50, height=15, font=default_font)
        self.sysCleanupResult.pack(padx=5, pady=5)
        self.listboxes.append(self.sysCleanupResult)

        self.exitSysCleanup_btn = tk.Button(self.sysCleanupPopup, text="Exit", command=exit_sysCleanup, width=9, height=2, font=default_font)
        self.exitSysCleanup_btn.pack(padx=5, pady=5)
        self.buttons.append(self.exitSysCleanup_btn)

        thread = threading.Thread(target=run_cleanup)
        thread.start()


    def toggleTheme(self):
        dark_theme = {
            "bg_color": "#0F111A",      # main background
            "fg_color": "#E4E6EB",      # main text color
            "btn_bg": "#1F222E",        # button background
            "btn_fg": "#E4E6EB",        # button text
            "active_bg": "#3A86FF",     # active/hover color
            "list_bg": "#161821",       # listbox background
            "list_fg": "#DADADA",       # listbox text
            "accent": "#3A86FF",        # highlight/accent
        }

        light_theme = {
            "bg_color": "#F5F6FA",      # main background
            "fg_color": "#1E1E1E",      # main text color
            "btn_bg": "#E9EAED",        # button background
            "btn_fg": "#1E1E1E",        # button text
            "active_bg": "#0078D4",     # active/hover color
            "list_bg": "#FFFFFF",       # listbox background
            "list_fg": "#000000",       # listbox text
            "accent": "#0078D4",        # highlight/accent
        }

        self.theme = light_theme if self.isThemedark else dark_theme

        self.isThemedark = not self.isThemedark

        self.root.configure(bg=self.theme["bg_color"])

        for label in self.labels:
            label.configure(bg=self.theme["bg_color"], fg=self.theme["fg_color"])

        for button in self.buttons:
            button.configure(bg=self.theme["btn_bg"], fg=self.theme["btn_fg"], activebackground=self.theme["active_bg"], activeforeground="#FFFFFF")

        for listbox in self.listboxes:
            listbox.configure(bg=self.theme["list_bg"], fg=self.theme["list_fg"], selectbackground=self.theme["accent"],selectforeground="#FFFFFF")

        for popup in self.popups:
            popup.configure(bg=self.theme["bg_color"])



if __name__ == "__main__":
    root = tk.Tk()
    app = PyLinUtil(root)
    root.mainloop()



