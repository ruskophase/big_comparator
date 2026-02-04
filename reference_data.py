from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReferenceFact:
    name: str
    value: Decimal
    unit: str
    source_url: str


REFERENCE_FACTS = [
    ReferenceFact(
        name="Mass of the Eiffel Tower",
        value=Decimal("10100000"),
        unit="kg",
        source_url="https://www.toureiffel.paris/en/the-monument/key-figures",
    ),
    ReferenceFact(
        name="Mass of the Titanic",
        value=Decimal("52310000"),
        unit="kg",
        source_url="https://www.britannica.com/topic/Titanic",
    ),
    ReferenceFact(
        name="Average Earth-Moon distance",
        value=Decimal("384400000"),
        unit="m",
        source_url="https://science.nasa.gov/moon/facts/",
    ),
    ReferenceFact(
        name="Approximate stars in the observable universe",
        value=Decimal("200000000000000000000000"),
        unit="count",
        source_url="https://esahubble.org/science/galaxies/",
    ),
    ReferenceFact(
        name="Seconds in one year",
        value=Decimal("31557600"),
        unit="s",
        source_url="https://www.nist.gov/pml/time-and-frequency-division/time-realization/leap-seconds",
    ),
    ReferenceFact(
        name="Estimated grains of sand on Earth",
        value=Decimal("7500000000000000000"),
        unit="count",
        source_url="https://www.npr.org/sections/krulwich/2012/11/05/164567572/which-is-greater-the-number-of-sand-grains-on-earth-or-stars-in-the-sky",
    ),
    ReferenceFact(
        name="Mass of Earth",
        value=Decimal("5.9722e24"),
        unit="kg",
        source_url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html",
    ),
]
