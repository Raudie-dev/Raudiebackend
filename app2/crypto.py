from django.conf import settings
from cryptography.fernet import Fernet
import base64

def _get_fernet():
    key = getattr(settings, 'CRYPTO_KEY', None)
    if not key:
        # Fallback si no está definida en settings, pero se recomienda tenerla
        key = base64.urlsafe_b64encode(b"RaudieCryptoSecretKey1234567890="[:32])
    return Fernet(key)

def encrypt_value(text):
    if not text:
        return ""
    f = _get_fernet()
    return f.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt_value(cipher_text):
    if not cipher_text:
        return ""
    f = _get_fernet()
    try:
        return f.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
    except Exception:
        return cipher_text # fallback to plain text if decryption fails
