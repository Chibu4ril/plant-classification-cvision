import requests
from bs4 import BeautifulSoup
from typing import List, Tuple

def fetch_doc_data(doc_url: str) -> str:
    try:
        response = requests.get(doc_url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RuntimeError(f"[Error] Could not fetch document: {e}")

def parse_table_from_html(html: str) -> List[Tuple[int, str, int]]:
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
    data = []

    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) != 3:
            continue
        try:
            x = int(cols[0].text.strip())
            char = cols[1].text.strip()[0]  
            y = int(cols[2].text.strip())
            data.append((x, char, y))
        except (ValueError, IndexError):
            continue

    return data

def build_grid(char_data: List[Tuple[int, str, int]]) -> List[List[str]]:
    max_x = max(x for x, _, _ in char_data)
    max_y = max(y for _, _, y in char_data)
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    for x, char, y in char_data:
        grid[y][x] = char
    return grid

def print_grid(grid: List[List[str]]) -> None:
    for row in grid:
        print(''.join(row))

def render_data(published_url: str) -> None:
    html = fetch_doc_data(published_url)
    char_data = parse_table_from_html(html)
    if not char_data:
        print("[Error] No data parsed from the document.")
        return
    grid = build_grid(char_data)
    print_grid(grid)


url = input("Enter the URL of the document: ")
render_data(url)
