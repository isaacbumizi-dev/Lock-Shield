import os
import time
import sqlite3

from kivymd.app import MDApp


class DatabaseManager:
    def __init__(self, db_path):
        self.running_app = MDApp.get_running_app()
        self.config_id = "ff21a594-e215-4cb8-847a-139bf14c7a13"
        self.database = os.path.join(db_path, ".slt3_lite_sqli.sqlite")

        os.makedirs(db_path, exist_ok=True)


    def initialize_database(self):
        """
        Cette methode créer les tables de la base des données
        :param
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration(
                    id VARCHAR(50) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL,
                    prefer_color VARCHAR(255) DEFAULT NULL,
                    born_town VARCHAR(255) DEFAULT NULL,
                    first_language VARCHAR(255) DEFAULT NULL,
                    first_school VARCHAR(255) DEFAULT NULL,
                    encrypted_password VARCHAR(255) DEFAULT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation VARCHAR(50) DEFAULT NULL,
                    file VARCHAR(50) DEFAULT NULL,
                    size VARCHAR(50) DEFAULT NULL,
                    status VARCHAR(50) DEFAULT NULL,
                    problem TEXT DEFAULT NULL,
                    duration INTEGER,
                    algorithm VARCHAR(50) DEFAULT NULL,
                    operation_date VARCHAR(100)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file VARCHAR(50) DEFAULT NULL,
                    key VARCHAR(50) DEFAULT NULL,
                    date VARCHAR(100)
                );
            """)

    def is_configuration_exist(self) -> bool:
        """
        Cette methode permet de savoir s'il existe une configuration (mot de passe d'access, Reponse sec question)
        :return: True si elle existe False si non
        """
        with sqlite3.connect(database=self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM configuration WHERE id = ?", (self.config_id,))
                data = [dict(row) for row in cursor.fetchall()]
                if data:
                    for row in data[0].items():
                        if row[0] in ("id", "password", "prefer_color", "born_town", "first_language",
                                      "first_school", "encrypted_password"
                        ) and row[1]:
                            continue
                        else:
                            return False
                    return True
                return False
            except Exception:
                return False

    def get_access_password(self):
        """
        Cette methode retourne le mot de passe d'access à l'application
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT password FROM configuration WHERE id = ?", (self.config_id,))
                result = cursor.fetchone()
                return result[0] if result else False
            except Exception:
                return False

    def get_encrypted_password(self):
        """
        Cette methode retourne le chiffré du mot de passe de l'utilisateur
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT encrypted_password FROM configuration WHERE id = ?", (self.config_id,))
                result = cursor.fetchone()
                return result[0] if result else False
            except Exception:
                return False

    def get_history(self):
        """
        Cette methode retourne l'historique des operations stocké dans la base des données
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM history")
                return [dict(row) for row in cursor.fetchall()]
            except Exception:
                return None

    def erase_history(self):
        """
        Cette methode supprimer l'ensemble des données de la table history
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DROP TABLE history")
                conn.commit()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation VARCHAR(50) DEFAULT NULL,
                        file VARCHAR(50) DEFAULT NULL,
                        size VARCHAR(50) DEFAULT NULL,
                        status VARCHAR(50) DEFAULT NULL,
                        problem TEXT DEFAULT NULL,
                        duration INTEGER,
                        algorithm VARCHAR(50) DEFAULT NULL,
                        operation_date VARCHAR(100)
                    );
                """)
                return True
            except Exception:
                return False

    def get_backup(self):
        """
        Cette methode retourne les sauvegardes des clés de chiffrement appliquées sur les fichier
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM backup")
                return [dict(row) for row in cursor.fetchall()]
            except Exception:
                return None

    def get_backup_key(self, backup_id):
        """
        Cette methode retourne le hash de la clé de chiffrement stocker dans le backup
        :param backup_id: l'id du backup
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT key FROM backup WHERE id = ?", (backup_id,))
                return cursor.fetchone()
            except Exception:
                return None
    def erase_back(self):
        """
        Cette methode supprimer l'ensemble des données de la table backup
        :return
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DROP TABLE backup")
                conn.commit()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file VARCHAR(50) DEFAULT NULL,
                        key VARCHAR(50) DEFAULT NULL,
                        date VARCHAR(100)
                    );
                """)
                return True
            except Exception:
                return False

    def add_new_config(
            self,
            password:str,
            prefer_color:str,
            born_town:str,
            first_language:str,
            first_school:str,
            encrypted_password
    ) -> bool:
        """
        Cette methode ajoute une configuration dans la base des données
        :param password: le hash du mot de passe d'accèss
        :param prefer_color: la couleur préferée de l'utilisateur (Response/Question de Restauration)
        :param born_town: la ville qui a vu naitre l'utilisateur (Response/Question de Restauration)
        :param first_school: la première ecole frequentée par l'utilisateur (Response/Question de Restauration)
        :param first_language: la première langue parlé de l'utilisateur (Response/Question de Restauration)
        :param encrypted_password: le chiffré du mot de passe
        :return True if success False else
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM configuration WHERE id = ?", (self.config_id,))
                conn.commit()

                cursor.execute("""
                    INSERT INTO configuration (id, password, prefer_color, born_town, first_language, first_school, encrypted_password)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.config_id,
                    password,
                    prefer_color,
                    born_town,
                    first_language,
                    first_school,
                    encrypted_password
                ))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    def add_new_history(
            self,
            operation:str,
            file:str,
            size:str,
            status:str,
            problem:str="",
            duration:int=0,
            algorithm:str=""
    ) -> bool:
        """
        Cette methode ajoute l'historique des operations dans la base des données
        :param operation: l'opération réalisée (chiffrement/Déchiffrement)
        :param file: le fichier surlequel l'opération à été réalisée
        :param size: la taille du fichier
        :param status: le status de l'operation (success, failed)
        :param problem: en cas de status=failed, la cause du failed
        :param duration: la durée de l'operation
        :param algorithm: en cas du chiffrement, l'algorithme utilisé
        :return True if success False else
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO history (operation, file, size, status, problem, duration, algorithm, operation_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    operation.strip(),
                    file.strip(),
                    size.strip(),
                    status.strip(),
                    problem.strip(),
                    duration,
                    algorithm.strip(),
                    time.strftime("%A %d %B %Y %H:%M:%S")
                ))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False


    def add_new_backup(self, file:str, key:str) -> bool:
        """
        Cette methode enregistre un backup dans la base des données
        :param file: le fichier backuper
        :param key: le hash de la clé de chiffrement du fichier
        :return True is success False else
        """
        with sqlite3.connect(database=self.database) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO backup (file, key, date)
                    VALUES (?, ?, ?)
                """, (
                    file.strip(),
                    key.strip(),
                    time.strftime("%A %d %B %Y %H:%M:%S")
                ))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False
