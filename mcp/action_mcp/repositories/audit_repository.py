import json
import os


class AuditRepository:

    def __init__(
        self,
        file_path: str,
    ):

        self.file_path = file_path

        directory = os.path.dirname(
            self.file_path
        )

        if directory:

            os.makedirs(
                directory,
                exist_ok=True,
            )

        if not os.path.exists(
            self.file_path
        ):

            with open(
                self.file_path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=2,
                )

    def save(
        self,
        audit_record: dict,
    ) -> dict:

        with open(
            self.file_path,
            "r",
            encoding="utf-8",
        ) as file:

            records = json.load(
                file
            )

        records.append(
            audit_record
        )

        with open(
            self.file_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                records,
                file,
                indent=2,
            )

        return audit_record