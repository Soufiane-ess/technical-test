from os import path


class PathValidator:

    @staticmethod
    def is_db_path_valid(path_to_validate: str) -> bool:
        if not path_to_validate: return False
        if path_to_validate[-3:] != '.db': return False
        return path.exists(path_to_validate) and path.isfile(path_to_validate)

    @staticmethod
    def is_json_file_path_valid(path_to_validate: str) -> bool:
        if not path_to_validate: return False
        if path_to_validate[-5:] != '.json': return False
        return path.exists(path_to_validate) and path.isfile(path_to_validate)
