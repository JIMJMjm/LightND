import ftplib
from os.path import exists as ext
from io import BytesIO
from typing import Optional


class FtpSyncManager:
    def __init__(self):
        self.ftp: Optional[ftplib.FTP] = None

    def _connect(self, host: str, port: int, username: str, password: str) -> tuple[bool, str]:
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(host, port, timeout=10)
            self.ftp.login(username, password)
            return True, "ok"
        except ftplib.all_errors as e:
            self.ftp = None
            return False, str(e)
        except OSError as e:
            self.ftp = None
            return False, str(e)

    def _disconnect(self):
        if self.ftp is None:
            return
        try:
            self.ftp.quit()
        except ftplib.all_errors:
            try:
                self.ftp.close()
            except ftplib.all_errors:
                pass
        finally:
            self.ftp = None

    def _ensure_remote_dir(self, remote_dir: str) -> tuple[bool, str]:
        if self.ftp is None:
            return False, "Not connected"
        parts = [p for p in remote_dir.strip('/').split('/') if p]
        try:
            self.ftp.cwd('/')
            for part in parts:
                try:
                    self.ftp.cwd(part)
                except ftplib.all_errors:
                    self.ftp.mkd(part)
                    self.ftp.cwd(part)
            return True, "ok"
        except ftplib.all_errors as e:
            return False, str(e)

    def test_connection(self, host: str, port: int, username: str, password: str) -> tuple[bool, str]:
        ok, msg = self._connect(host, port, username, password)
        self._disconnect()
        return ok, msg

    def upload_bank(self, host: str, port: int, username: str, password: str,
                    local_path: str = "bank.json",
                    remote_dir: str = "/lightnd/",
                    remote_file: str = "bank.json") -> tuple[bool, str]:
        if not ext(local_path):
            return False, "Local bank.json not found."

        ok, msg = self._connect(host, port, username, password)
        if not ok:
            return False, msg

        try:
            ok, msg = self._ensure_remote_dir(remote_dir)
            if not ok:
                return False, msg

            with open(local_path, 'rb') as fh:
                self.ftp.storbinary(f'STOR {remote_file}', fh)
            return True, "Upload complete."
        except ftplib.all_errors as e:
            return False, str(e)
        finally:
            self._disconnect()

    def download_bank(self, host: str, port: int, username: str, password: str,
                      remote_dir: str = "/lightnd/",
                      remote_file: str = "bank.json") -> tuple[bool, str, Optional[bytes]]:
        ok, msg = self._connect(host, port, username, password)
        if not ok:
            return False, msg, None

        try:
            try:
                self.ftp.cwd(remote_dir)
            except ftplib.all_errors:
                return False, f"Remote directory {remote_dir} not found. Upload first.", None

            try:
                self.ftp.size(remote_file)
            except ftplib.all_errors:
                return False, f"Remote file {remote_file} not found. Upload first.", None

            buffer = BytesIO()
            self.ftp.retrbinary(f'RETR {remote_file}', buffer.write)
            return True, "Download complete.", buffer.getvalue()
        except ftplib.all_errors as e:
            return False, str(e), None
        finally:
            self._disconnect()
