from choreographer.errors import ChromeNotFoundError
import kaleido

print("Ensuring chrome is installed.")
try:
    kal = kaleido.Kaleido()
    print("Chrome already installed.")
except ChromeNotFoundError:
    print("Chrome not found. Fetching chrome...")
    kaleido.get_chrome_sync()
    kaleido.Kaleido()
    print("Chrome installed successfully.")
