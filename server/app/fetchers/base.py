from abc import ABC, abstractmethod

from app.schemas.price import PriceRecordCreate


class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self) -> list[PriceRecordCreate]:
        pass

    @abstractmethod
    def source_name(self) -> str:
        pass
