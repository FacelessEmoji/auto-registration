import os

from db.init import load_accounts_from_txt_to_db, create_database
from project.main import main
from project.functions import load_proxies

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    db_path = os.path.join(base_dir, 'db', 'accounts.db')
    accounts_txt_path = os.path.join(base_dir, 'db', 'accounts.txt')

    create_database(db_path)
    load_accounts_from_txt_to_db(accounts_txt_path, db_path)

    proxy_path = "proxies.txt"
    proxy = load_proxies(proxy_path)

    main(proxy)
