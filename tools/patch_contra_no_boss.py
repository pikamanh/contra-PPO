"""Build the local Contra ROM variant whose stage bosses die on spawn."""

from hashlib import md5
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROM = ROOT / "Contra" / "ROMs" / "contra.nes"
OUTPUT_ROM = ROOT / "Contra" / "ROMs" / "contra_final.nes"
SOURCE_MD5 = "7bdad8b4a7a56a634c9649d20bd3011b"

# File offset, original pointer, replacement pointer.
# Stage 1: plated-door initialization -> boss-defeated routine.
# Stage 8: alien-heart initialization -> heart death routine.
PATCHES = (
    (0x0BD9, bytes.fromhex("D7 8B"), bytes.fromhex("40 E7")),
    (0x3C92, bytes.fromhex("92 BC"), bytes.fromhex("4C BD")),
)


def main() -> None:
    rom = bytearray(SOURCE_ROM.read_bytes())
    source_hash = md5(rom).hexdigest()
    if source_hash != SOURCE_MD5:
        raise ValueError(
            f"Unsupported source ROM MD5: {source_hash}; expected {SOURCE_MD5}"
        )

    for offset, expected, replacement in PATCHES:
        actual = bytes(rom[offset : offset + len(expected)])
        if actual != expected:
            raise ValueError(
                f"Unexpected bytes at {offset:#06x}: {actual.hex(' ')}; "
                f"expected {expected.hex(' ')}"
            )
        rom[offset : offset + len(replacement)] = replacement

    OUTPUT_ROM.write_bytes(rom)
    print(f"Wrote {OUTPUT_ROM}")
    print(f"MD5: {md5(rom).hexdigest()}")


if __name__ == "__main__":
    main()
