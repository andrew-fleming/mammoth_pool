import os
import asyncio
from scripts.signer import Signer
from dotenv import load_dotenv

load_dotenv()

KEY = int(os.getenv("PRIVATE_KEY"))
signer = Signer(KEY)

# def main:
#    # ADD TO ME
#
#
# if __name__ == "__main__":
#    main()
