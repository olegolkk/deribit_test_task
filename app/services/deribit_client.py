import aiohttp
import asyncio
from typing import Dict, Optional
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeribitClient:

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.deribit.url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()

    async def _create_session(self):
        """Создание HTTP сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={"Content-Type": "application/json"}
            )

    async def _close_session(self):
        """Закрытие HTTP сессии"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, method: str, params: Dict = None) -> Dict:
        """Выполнение запроса к API"""
        if not self.session:
            await self._create_session()

        try:
            async with self.session.get(f"/public/{method}", params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get("error"):
                    raise Exception(f"Deribit API error: {data['error']}")

                return data.get("result", {})
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error while requesting {method}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error while requesting {method}: {e}")
            raise

    async def get_index_price(self, currency: str) -> Dict:
        """
        Получение index price для указанной валюты

        Args:
            currency: 'btc' или 'eth'

        Returns:
            Dict с данными о цене
        """
        result = await self._make_request("get_index_price", {"index_name": f"{currency}_usd"})

        # Преобразуем ответ в удобный формат
        return {
            "ticker": f"{currency}_usd",
            "price": float(result.get("index_price", 0)),
            "timestamp": datetime.fromtimestamp(result.get("estimated_delivery_price", 0) / 1000)
        }

    async def get_prices(self, currencies: list) -> list:
        """
        Получение цен для нескольких валют одновременно

        Args:
            currencies: список валют ['btc', 'eth']

        Returns:
            Список словарей с ценами
        """
        tasks = [self.get_index_price(currency) for currency in currencies]
        return await asyncio.gather(*tasks)