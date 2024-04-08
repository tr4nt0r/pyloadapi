"""PyLoadAPI exceptions."""


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""


class ParserError(Exception):
    """Error to indicate error while parsing."""
