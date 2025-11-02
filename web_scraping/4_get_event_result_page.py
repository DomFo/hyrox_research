from typing import Optional

import requests


def get_division_results_page(
        season_number: int,
        event_main_group_id: str,
        event_id: str,
        page_number: int = 1,  # <-- NEW DYNAMIC PARAMETER
        sex_filter: str = '%',
        num_results: int = 25
) -> Optional[str]:
    """
    Sends a POST request to fetch a specific page of results.
    """
    if page_number < 1:
        print("Page number must be 1 or greater.")
        return None

    BASE_URL = f"https://results.hyrox.com/season-{season_number}/"
    TARGET_PATH = "?pid=list&pidp=ranking_nav"
    URL = BASE_URL + TARGET_PATH

    # The payload is modified to include the page number
    payload = {
        'lang': 'EN_CAP',
        'startpage': 'start_responsive',
        'startpage_type': 'lists',
        'event_main_group': event_main_group_id,
        'event': event_id,
        'ranking': 'time_finish_netto',
        'search[name]': '',
        'search[firstname]': '',
        'search[sex]': sex_filter,
        'search[age_class]': '%',
        'search[nation]': '%',
        'num_results': str(num_results),
        # --- CRUCIAL NEW PAGE PARAMETER ---
        'page': str(page_number),  # The page index (starts at 1)
        # ----------------------------------
        'submit': 'submit'
    }

    print(f"\n⚡️ Sending POST request for Page {page_number}...")

    try:
        response = requests.post(URL, data=payload, timeout=30)
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as err:
        print(f"❌ Failed to fetch page {page_number}: {err}")
        return None


from bs4 import BeautifulSoup, Tag
from typing import Dict, Any


def get_row_information_final(row_soup: Tag) -> Dict[str, Any]:
    """
    Extracts all athlete details, including the link to their individual detail page,
    using robust list-based class matching.
    """

    data = {
        'rank': 'N/A',
        'ag_rank': 'N/A',
        'last_name': 'N/A',
        'first_name': 'N/A',
        'nationality': 'N/A',
        'age_group': 'N/A',
        'total_time': 'N/A',
        'detail_link': 'N/A'  # <-- NEW FIELD
    }

    # --- 1. Rank and Age Group Rank (Uses list for robust matching) ---
    rank_tag = row_soup.find('div', class_=['list-field', 'type-place', 'place-primary'])
    if rank_tag:
        data['rank'] = rank_tag.text.strip()

    ag_rank_tag = row_soup.find('div', class_=['list-field', 'type-place', 'place-secondary'])
    if ag_rank_tag:
        data['ag_rank'] = ag_rank_tag.text.strip()

    # --- 2. Name and Link Extraction ---
    h4 = row_soup.find('h4', class_='list-field type-fullname')
    a_tag = h4.find('a') if h4 else None

    if a_tag:
        # Extract the Detail Link (NEW)
        data['detail_link'] = a_tag.get('href', 'N/A')

        # Name Parsing
        full_name_text = a_tag.text.strip()
        if ',' in full_name_text:
            parts = full_name_text.split(',', 1)
            data['last_name'] = parts[0].strip()
            data['first_name'] = parts[-1].strip()
        else:
            data['first_name'] = full_name_text

    # --- 3. Nationality (Abbreviation) ---
    nation_abbr_tag = row_soup.find('span', class_='nation__abbr')
    if nation_abbr_tag:
        data['nationality'] = nation_abbr_tag.text.strip()

    # --- 4. Age Group ---
    age_group_tag = row_soup.find('div', class_=['list-field', 'type-age_class'])
    if age_group_tag:
        age_group_text = age_group_tag.get_text(strip=True)
        data['age_group'] = age_group_text.replace('AgeGroup', '').replace('Age Group', '').strip()

    # --- 5. Total Time (Uses list for robust matching) ---
    time_div = row_soup.find('div', class_=['right', 'list-field', 'type-time'])
    if time_div:
        time_value_div = time_div.find_all('div')[-1] if time_div.find_all('div') else time_div
        data['total_time'] = time_value_div.text.strip()

    return data


# --- Combining the Request and Parsing ---

def get_page_details(html_content: str, requested_page: int) -> dict:
    """
    Parses the HTML and verifies page number (or calculates pages).
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Extract Total Results
    # The list itself is the <ul> with the class 'list-group-multicolumn'
    results_list_container = soup.find('ul', class_='list-group-multicolumn')
    rows = results_list_container.find_all('li', class_='list-group-item')
    # remove the header row "right  list-group row list-group-item  list-group-header "
    rows = [row for row in rows if 'list-group-header' not in row.get('class', [])]
    for row in rows:
        data = get_row_information_final(row)

    # print the first 1 athlete data as a sample
    if rows:
        sample_data = get_row_information_final(rows[0])
        print(f"\nSample Athlete Data from Page {requested_page}:\n{sample_data}")
    else:
        print("❌ No athlete rows found in the HTML content.")


# --- Example Usage to get Page 2 ---
TOWN_EVENT_ID = '2025 Stuttgart'
DIVISION_ID = 'HPRO_LR3MS4JIE9E'
SEASON = 8
PAGE_TO_REQUEST = 1  # <--- Requesting the SECOND page

html_content_page2 = get_division_results_page(
    season_number=SEASON,
    event_main_group_id=TOWN_EVENT_ID,
    event_id=DIVISION_ID,
    page_number=PAGE_TO_REQUEST,  # Pass the dynamic page number
    sex_filter='M',
    num_results=25
)

if html_content_page2:
    get_page_details(html_content_page2, PAGE_TO_REQUEST)
