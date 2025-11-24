class CryptoException(Exception):
    pass


class InvalidTag(CryptoException):
    pass


class EncodingToBytesError(CryptoException):
    pass
