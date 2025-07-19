from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
requirements = (here / "requirements.txt").read_text().splitlines()

setup(
    name="diffscribe",
    version="0.1.0",
    description="🧠 AI-powered Git commit message generator using Groq & Gemini",
    author="Sarita Chaudhary",
    author_email="sarita1412.chaudhary@email.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "diffscribe=diffscribe.diffscribe:main"
        ]
    },
    python_requires=">=3.7",
)
