import re
import requests
from bs4 import BeautifulSoup

class Lots:
    """
    Class for representing a Funpay Lots object.

    Attributes:
        id (str): The ID of the lots.
        url (str): The URL of the lots.
        data (str): The raw HTML data of the lots.

    Methods:
        get_data(): Retrieves the raw HTML data of the lots.
        clean_text(text): Cleans the text by removing extra whitespace and stripping.
        lots_links(max_limit=10): Returns a dictionary of lots links.
        sort_lots(sort_by="lowest"): Sorts the lots links by cost.
    """
    def __init__(self, ID: int):
        """
        Initializes the Lots object.

        Args:
            ID (int): The ID of the lots.
        """
        self.id = str(ID)
        self.url = f"https://funpay.com/en/lots/{self.id}/" or f"https://funpay.com/chips/{self.id}/"
        self.data = None

        self.__get_data__()

    def __get_data__(self):
        """
        Retrieves the raw HTML data of the lots.

        Returns:
            str: The raw HTML data of the lots.

        Raises:
            Exception: If there is an error getting the data.
        """
        if self.data is None:
            response = requests.get(self.url)
            if response.status_code == 200:
                self.data = response.text
            else:
                raise Exception(f"Error getting data for ID: {self.id}. Status code: {response.status_code}")
        return self.data
    
    def clean_text(self, text):
        """
        Cleans the text by removing extra whitespace and stripping.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: The cleaned text.
        """
        return re.sub(r'\s+', ' ', text).strip()

    def lots_links(self, max_limit=20):
        """
        Возвращает список ссылок на лоты, исключая лоты с сервером (RU) и закрепленные предложения.

        Args:
            max_limit (int): Максимальное количество лотов для обработки.

        Returns:
            list: Список словарей с информацией о лотах.
        """
        try:
            soup = BeautifulSoup(self.data, "html.parser")
            lots = soup.find("div", class_="showcase-table")
            lots_links = []

            if lots:
                lots = lots.find_all("a", class_="tc-item")[:max_limit]
                for lot in lots:
                    
                    href = lot.get("href", "Unknown")
                    info = self.clean_text(lot.find("div", class_="tc-desc-text").text) if lot.find("div", class_="tc-desc-text") else 'Unknown'
                    cost = self.clean_text(lot.find("div", class_="tc-price").text) if lot.find("div", class_="tc-price") else 'Unknown'
                    server_element = lot.find("div", class_="tc-server hidden-xs")
                    server = self.clean_text(server_element.text) if server_element else 'Unknown'
                    check_for_pin_element = lot.find("div", class_="sc-offer-icons")

                    #без RU и закрепов
                    if "(RU)" not in server and not check_for_pin_element:
                        lots_links.append({
                            "href": href,
                            "info": info,
                            "cost": cost,
                            "server": server
                        })
            return lots_links
        except Exception as e:
            print(f"Error parsing lots: {e}")
            return []


    def sort_lots(self, sort_by="lowest"):
        """
        Sorts the lots links by cost.

        Args:
            sort_by (str, optional): The order to sort the lots by. Defaults to "lowest".

        Returns:
            dict: The sorted lots links.

        Raises:
            ValueError: If the sort_by parameter is invalid.
        """
        lots_links = self.lots_links()
        if sort_by == "lowest":
            lots_links = dict(sorted(lots_links.items(), key=lambda x: float(x[1]["cost"].split(sep=" ")[0])))
        elif sort_by == "highest":
            lots_links = dict(sorted(lots_links.items(), key=lambda x: float(x[1]["cost"].split(sep=" ")[0]), reverse=True))
        else:
            raise ValueError("Invalid sort_by parameter. Only 'lowest' and 'highest' are accepted.")
        return lots_links
