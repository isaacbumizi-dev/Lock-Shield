import os
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
    return [b'03a74b2649f0eda7ec8caf1566895fea', b'66488aa029b0b4b853b4b02c35d177ee',
            b'432cc2fc269e4c003ad2d86fb9a9e0f4', b'2195bc8cdf6407bd690b3556b3f00aa0',
            b'2c298d7795057ce4a23cd7cf560688d8', b'cd745cd9963a8ebd28ab407c4f79db16',
            b'b49637186c259f9afe7c1d6dce1d91b4', b'9679b0c9da450ad07c521455fcfaad09',
            b'c228e1502e4df0d25ee0384713fb78c4']


percent = 0
def update_process_progress(x1, x2):
    global percent
    percent = (x2 * 100) / x1
def get_progress_percent():
    return int(percent)

def derive_cryptographic_key(pwd, keySize):
    """
    Cette methode permet de dérivé la clé de chiffrement d'une taille donneé à partir
    la valeu de la variable RAW_ENCRYPTION_KEY
    :return:
    """
    w_pwd = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length=int(keySize / 8),
        salt=b'salt_',
        iterations=100000,
    )
    return w_pwd.derive(pwd.encode('utf-8'))

class Encryption_engine:
    def __init__(self, data_path, encryption_key):
        """
        Cette classe se charge du processus de chiffrement
        :param data_path: le chemin vers le fichier ou le dossier à chiffré
        :param encryption_key: la clé de chiffrement
        """
        self._data_path = data_path
        self._encryption_key = encryption_key


    @staticmethod
    def encrypt_file(input_file, encryption_key, encryption_mode, algorithm_signature):
        global percent
        percent = 0
        file_size = os.path.getsize(input_file)
        current_size = 0

        chunk_size = 10 * (1024 * 1024)  # 10 Mo
        iv = get_random_bytes(16)
        cipher = AES.new(encryption_key, encryption_mode, iv)
        with open(input_file, 'rb') as input, open(input_file + ".bin", 'wb') as output:
            output.write(algorithm_signature)
            output.write(iv)
            while chunk := input.read(chunk_size):
                encrypted_chunk = cipher.encrypt(pad(chunk, AES.block_size))
                output.write(encrypted_chunk)

                current_size += len(chunk)
                update_process_progress(file_size, current_size)

        os.remove(input_file)
        os.renames(input_file + ".bin", input_file)



    def AES_OFB(self, signature):
        self.encrypt_file(self._data_path, self._encryption_key, AES.MODE_OFB, signature)
    def AES_CBC(self, signature):
        self.encrypt_file(self._data_path, self._encryption_key, AES.MODE_CBC, signature)
    def AES_CFB(self, signature):
        self.encrypt_file(self._data_path, self._encryption_key, AES.MODE_CFB, signature)



class Decryption_engine:
    def __init__(self, data_path, decryption_key):
        """
        Cette classe se charge du processus de déchiffrement
        :param data_path: le chemin vers le fichier ou le dossier à décrypté
        :param decryption_key: la clé de déchiffrement
        """
        self._data_path = data_path
        self._decryption_key = decryption_key

    @staticmethod
    def decrypt_file(input_file, decryption_key, decryption_mode):
        global percent
        percent = 0
        file_size = os.path.getsize(input_file)
        current_size = 0

        chunk_size = 10 * (1024 * 1024)  # 10 Mo

        with open(input_file, 'rb') as input, open(input_file + ".bin", 'wb') as output:
            sign_iv = input.read(48)
            cipher = AES.new(decryption_key, decryption_mode, sign_iv[32:])
            while chunk := input.read(chunk_size + AES.block_size):
                decrypted_chunk = unpad(cipher.decrypt(chunk), AES.block_size)
                output.write(decrypted_chunk)

                current_size += len(chunk)
                update_process_progress(file_size, current_size)

        os.remove(input_file)
        os.renames(input_file + ".bin", input_file)

    def AES_OFB(self):
        self.decrypt_file(self._data_path, self._decryption_key, AES.MODE_OFB)
    def AES_CBC(self):
        self.decrypt_file(self._data_path, self._decryption_key, AES.MODE_CBC)
    def AES_CFB(self):
        self.decrypt_file(self._data_path, self._decryption_key, AES.MODE_CFB)