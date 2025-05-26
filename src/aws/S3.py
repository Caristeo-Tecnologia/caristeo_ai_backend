import json

import boto3
from botocore.errorfactory import ClientError

from src.core.config import boto3_params


class S3:
    def __init__(self) -> None:
        self.client = boto3.client("s3", **boto3_params)

    def put_object(self, bucket_name: str, file_key: str, file_bytes: bytes) -> dict:
        """Coloca um objeto no S3

        Args:
            bucket_name (str): Nome do bucket
            file_key (str): Caminho do objeto no bucket
            file_bytes (bytes): Conteúdo do objeto

        Returns:
            dict: Resposta da operação
        """
        response = self.client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=file_bytes,
        )
        return response

    def upload_fileobj(self, bucket_name: str, file_key: str, fileobj) -> dict:
        """Faz o upload de um objeto para o S3

        Args:
            bucket_name (str): Nome do bucket
            file_key (str): Caminho do objeto no bucket
            fileobj (_type_): Objeto a ser enviado
        """
        # boto3.upload_fileobj returns None or raises on error
        response = self.client.upload_fileobj(
            Fileobj=fileobj, Bucket=bucket_name, Key=file_key
        )
        return response

    def get_object(self, bucket_name: str, file_key: str) -> str:
        """Retorna o conteúdo de um objeto no S3

        Parameters
        ----------
        bucket_name : str
            Nome do bucket
        file_key : str
            Caminho do objeto no bucket

        Returns
        -------
        str
            Conteúdo do objeto

        Raises
        ------
        ValueError
            Caso o formato do arquivo não seja suportado
        """
        file_extension = file_key.split(".")[-1].lower()

        # Define binary file types that shouldn't be decoded with UTF-8
        binary_extensions = [
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "png",
            "jpg",
            "jpeg",
            "gif",
        ]

        response = self.client.get_object(Bucket=bucket_name, Key=file_key)

        if file_extension in binary_extensions:
            # Return raw bytes for binary files
            return response["Body"].read()

        # For text files, decode with UTF-8
        file_content = response["Body"].read().decode("utf-8")

        if file_extension == "json":
            return json.loads(file_content)
        elif file_extension in ["txt", "md"]:
            return file_content
        else:
            raise ValueError("Unsupported file format")

    def get_objects(self, bucket_name: str, file_keys: list) -> list:
        return [self.get_object(bucket_name, key) for key in file_keys]

    def check_object_exists(self, bucket_name: str, file_key: str) -> bool:
        """Checa se um objeto existe em um bucket

        Parameters
        ----------
        bucket_name : str
            Nome do bucket
        file_key : str
            Caminho do objeto no bucket

        Returns
        -------
        bool
            True se o objeto existe, False caso contrário

        Raises
        ------
        e
            Caso ocorra um erro ao checar a existência do objeto
        """
        try:
            self.client.head_object(Bucket=bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e

    def list_objects(self, bucket_name: str, prefix: str) -> list:
        """Lista os objetos em um bucket S3 com um prefixo específico
        Parameters

        Args:
            bucket_name (str): Nome do bucket S3
            prefix (str): Prefixo para filtrar os objetos

        Returns:
            list: Lista de chaves dos objetos que correspondem ao prefixo
        """
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            else:
                return []

        except ClientError as e:
            print(f"An error occurred: {e}")
            return []

    def delete_object(self, bucket_name: str, file_key: str) -> dict:
        """Deleta um objeto no S3

        Parameters
        ----------
        bucket_name : str
            Nome do bucket
        file_key : str
            Caminho do objeto no bucket

        Returns
        -------
        dict
            Resposta da operação de deleção
        """
        response = self.client.delete_object(Bucket=bucket_name, Key=file_key)
        return response
