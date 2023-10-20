import asyncio

from dotenv import load_dotenv

from app import main

if __name__ == "__main__":
    load_dotenv()

    asyncio.run(main())
