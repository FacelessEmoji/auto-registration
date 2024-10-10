from project.main import main
from project.functions import load_proxies, parse_accounts_from_txt

if __name__ == "__main__":
    accounts_path = "accounts.txt"
    proxy_path = "proxies.txt"

    proxy = load_proxies(proxy_path)
    accounts = parse_accounts_from_txt(accounts_path)
    main(proxy, accounts, accounts_path)
