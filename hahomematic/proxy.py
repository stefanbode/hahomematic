"""
Implementation of a locking ServerProxy for XML-RPC communication.
"""

import logging
import ssl
import xmlrpc.client

_LOGGER = logging.getLogger(__name__)


class ProxyException(Exception):
    """hahomematic Proxy exception."""


# noinspection PyProtectedMember,PyUnresolvedReferences
class ThreadPoolServerProxy(xmlrpc.client.ServerProxy):
    """
    ServerProxy implementation with ThreadPoolExecutor when request is executing.
    """

    def __init__(self, executor_func, *args, **kwargs):
        """
        Initialize new proxy for server and get local ip
        """
        self._executor_func = executor_func
        self._tls = kwargs.pop("tls", False)
        self._verify_tls = kwargs.pop("verify_tls", True)
        if self._tls and not self._verify_tls and self._verify_tls is not None:
            kwargs["context"] = ssl._create_unverified_context()
        xmlrpc.client.ServerProxy.__init__(self, encoding="ISO-8859-1", *args, **kwargs)

    async def __async_request(self, *args, **kwargs):
        """
        Call method on server side
        """
        parent = xmlrpc.client.ServerProxy
        try:
            return await self._executor_func(
                # pylint: disable=protected-access
                parent._ServerProxy__request,
                self,
                *args,
                **kwargs,
            )
        except Exception as ex:
            raise ProxyException(ex) from ex

    def __getattr__(self, *args, **kwargs):
        """
        Magic method dispatcher
        """
        return xmlrpc.client._Method(self.__async_request, *args, **kwargs)


# noinspection PyProtectedMember,PyUnresolvedReferences
class SimpleServerProxy(xmlrpc.client.ServerProxy):
    """
    ServerProxy implementation with lock when request is executing.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize new proxy for server and get local ip
        """
        self._tls = kwargs.pop("tls", False)
        self._verify_tls = kwargs.pop("verify_tls", True)
        if self._tls and not self._verify_tls and self._verify_tls is not None:
            kwargs["context"] = ssl._create_unverified_context()
        xmlrpc.client.ServerProxy.__init__(self, encoding="ISO-8859-1", *args, **kwargs)

    def __request(self, *args, **kwargs):
        """
        Call method on server side
        """
        parent = xmlrpc.client.ServerProxy
        # pylint: disable=protected-access
        try:
            return parent._ServerProxy__request(self, *args, **kwargs)
        except Exception as ex:
            raise ProxyException(ex) from ex

    def __getattr__(self, *args, **kwargs):
        """
        Magic method dispatcher
        """
        return xmlrpc.client._Method(self.__request, *args, **kwargs)
