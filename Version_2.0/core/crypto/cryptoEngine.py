import os
import zlib
import base64

from io import BytesIO
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



def get_algorithm_signature():
    """
    le signature numerique de chaque algorithme est représentés par un hash md5(hexdigest), avec comme valeur:
    indice 0: AES_MODE_CFB_128
    indice 1: AES_MODE_CFB_192
    indice 2: AES_MODE_CFB_256
    indice 3: AES_MODE_CBC_128
    indice 4: AES_MODE_CBC_192
    indice 5: AES_MODE_CBC_256
    indice 6: AES_MODE_OFB_128
    indice 7: AES_MODE_OFB_192
    indice 8: AES_MODE_OFB_256
    :return:
    """
    return [
        b'03a74b2649f0eda7ec8caf1566895fea',
        b'66488aa029b0b4b853b4b02c35d177ee',
        b'432cc2fc269e4c003ad2d86fb9a9e0f4',
        b'2195bc8cdf6407bd690b3556b3f00aa0',
        b'2c298d7795057ce4a23cd7cf560688d8',
        b'cd745cd9963a8ebd28ab407c4f79db16',
        b'b49637186c259f9afe7c1d6dce1d91b4',
        b'9679b0c9da450ad07c521455fcfaad09',
        b'c228e1502e4df0d25ee0384713fb78c4'
    ]


def derive_crypto_key(pwd, keySize):
    """
    Cette fonction derive le contenu de la variable pwd en une clé cryptographique
    :param pwd: la clé à derivé
    :param keySize: la taille de la clé derivée
    :return
    """
    w_pwd = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length=int(keySize / 8),
        salt=b'\xbf%\xa5*8\xddw\x9a4\xca\x82m\xa7,\x89\xd0',
        iterations=100000,
    )
    return w_pwd.derive(pwd.encode('utf-8'))

def encrypt_password(password, encryption_key):
    """
    Cette fonction chiffre le mot de passe de l'utilisateur
    :param password: le mot de passe à chiffré
    :param encryption_key: la clé de chiffrement
    :return
    """
    try:
        compressed_text = zlib.compress(password)

        session_key = derive_crypto_key(encryption_key, 256)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        cipher_text, tag = cipher_aes.encrypt_and_digest(compressed_text)

        encrypted_payload = cipher_aes.nonce + tag + cipher_text
        encrypted = base64.encodebytes(encrypted_payload)

        return encrypted
    except Exception:
        return None

def decrypt_password(encrypted_password, decryption_key):
    """
    Cette fonction dechiffre le mot de passe de l'utilisateur
    :param encrypted_password: le chiffré du mot de passe
    :param decryption_key: la clé de dchiffrement
    :return
    """
    try:
        encrypted_bytes = BytesIO(base64.decodebytes(encrypted_password))

        nonce = encrypted_bytes.read(16)
        tag = encrypted_bytes.read(16)
        cipher_text = encrypted_bytes.read()

        session_key = derive_crypto_key(decryption_key, 256)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(cipher_text, tag)
        plaintext = zlib.decompress(decrypted)

        return plaintext.decode('utf-8')
    except:
        return None

def encrypt_file(file, encryption_key, encryption_algorithm, algo_signature, callback=None):
    """
    Cette methode fait un chiffrement sur un fichier
    :param file: le fichier à chiffré
    :param encryption_key: la clé de chiffremnt
    :param encryption_algorithm: le mode de chiffrement AES à utilisé
    :param algo_signature: la signature de l'algorithme de chiffrement
    :param callback: une fonction callback à appelée(une fonction de mise a jour de la progression par exemple)
    :return
    """
    try:
        encryption_mode = AES.MODE_CBC
        match encryption_algorithm:
            case "AES_CBC":
                encryption_mode = AES.MODE_CBC
            case "AES_CFB":
                encryption_mode = AES.MODE_CFB
            case "AES_OFB":
                encryption_mode = AES.MODE_OFB

        file_size = os.path.getsize(file)
        current_size = 0
        if callback:
            callback(0)

        chunk_size = 10 * (1024 * 1024)  # 10 Mo
        iv = get_random_bytes(16)
        cipher = AES.new(encryption_key, encryption_mode, iv)
        with open(file, 'rb') as input_file, open(file + ".bin", "wb") as output_file:
            output_file.write(algo_signature)
            output_file.write(iv)
            while chunk := input_file.read(chunk_size):
                encrypted_chunk = cipher.encrypt(pad(chunk, AES.block_size))
                output_file.write(encrypted_chunk)

                current_size += len(chunk)
                if callback:
                    callback((current_size * 100) / file_size)

        os.remove(file)
        os.renames(file + ".bin", file)

        return True,
    except Exception as e:
        return False, str(e)


def decrypt_file(file, decryption_key, decryption_algorithm, callback=None):
    """
    Cette methode applique une methode de déchiffrement sur un fichier
    :param file: le fichier à dechiffrer
    :param decryption_key: la clé de dechiffrement
    :param decryption_algorithm: le mode de déchiffrement AES à utiliser
    :param callback: une fonction callback à appelée(une fonction de mise a jour de la progression par exemple)
    :return
    """
    try:
        decryption_mode = AES.MODE_CBC
        match decryption_algorithm:
            case "AES_CBC":
                decryption_mode = AES.MODE_CBC
            case "AES_CFB":
                decryption_mode = AES.MODE_CFB
            case "AES_OFB":
                decryption_mode = AES.MODE_OFB

        file_size = os.path.getsize(file)
        current_size = 0
        if callback:
            callback(0)

        chunk_size = 10 * (1024 * 1024) #10Mo

        with open(file, 'rb') as input_file, open(file + ".bin", "wb") as output_file:
            sign_iv = input_file.read(48)
            cipher = AES.new(decryption_key, decryption_mode, sign_iv[32:])

            remaining = file_size - 48
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                chunk = input_file.read(read_size)
                if not chunk:
                    break

                decrypted_chunk = cipher.decrypt(chunk)
                current_size += len(chunk)

                if remaining - len(chunk) <= 0:
                    try:
                        decrypted_chunk = unpad(decrypted_chunk, AES.block_size)
                    except ValueError:
                        return False, "Padding incorrect - Clé invalide"

                output_file.write(decrypted_chunk)
                remaining -= len(chunk)

                if callback:
                    callback((current_size * 100) / file_size)

            """while chunk := input_file.read(chunk_size + AES.block_size):
                decrypted_chunk = unpad(cipher.decrypt(chunk), AES.block_size)
                output_file.write(decrypted_chunk)

                current_size += len(chunk)
                if callback:
                    callback((current_size * 100) / file_size)"""

        os.remove(file)
        os.renames(file + ".bin", file)
        return True,
    except Exception as e:
        if "Padding" in str(e):
            return False, f"Clé de déchiffrement invalide.: {os.path.basename(file)}"
        else:
            return False, str(e)

