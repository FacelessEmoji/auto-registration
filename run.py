from project.main import main
from project.functions import load_proxies, parse_accounts_from_txt

if __name__ == "__main__":

    proxy_path = "proxies.txt"
    proxy = load_proxies(proxy_path)

    main(proxy)
