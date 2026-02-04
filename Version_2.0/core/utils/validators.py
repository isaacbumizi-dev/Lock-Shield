import bcrypt


def hash_content(content: str) -> bytes:
    """
    Cette fonction nous permet de hacher un mot de passe
    :param content: le mot de passe à hacher
    :return: le mot de passe haché
    """
    hash_salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=content.encode('utf-8'), salt=hash_salt)

def is_password_valid(hashed_password, input_password):
    """
    Cette fonction verifie la validité d'un mot de passe
    :param hashed_password: le mot de passe haché tiré de la base des données
    :param input_password: le mot de passe saisit par l'utilisateur
    """
    input_password = str(input_password).strip()
    try:
        return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password),
    except Exception:
        return False

def is_any_empty(*values) -> bool:
    """
    Cette fonction permet de verifier si un des elements passé en parametre est vide
    :param values: les element à verifier
    :return bool
    """
    return any(v is None or not str(v).strip() for v in values)