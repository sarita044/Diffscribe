from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
requirements = (here / "requirements.txt").read_text().splitlines()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="diffscribe",
    version="0.1.2",
    description="🧠 AI-powered Git commit message generator using Groq & Gemini",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    author="Sarita Chaudhary",
    author_email="sarita1412.chaudhary@email.com",
    url="https://github.com/sarita044/Diffscribe",
    project_urls={
        "Source": "https://github.com/sarita044/Diffscribe",
        "Bug Tracker": "https://github.com/sarita044/Diffscribe/issues",
        "Documentation": "https://github.com/sarita044/Diffscribe#readme/",
    },
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
