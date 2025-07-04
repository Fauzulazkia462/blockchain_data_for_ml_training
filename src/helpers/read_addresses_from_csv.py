import csv

def read_addresses_from_csv(path: str, encoding: str = "utf-8") -> list[str]:
    addresses: list[str] = []
    with open(path, newline="", encoding=encoding, errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        print(f'Detected CSV header column: "{header[0] if header else "n/a"}"')
        for row in reader:
            if row and row[0].strip():
                addresses.append(row[0].strip())
    return addresses