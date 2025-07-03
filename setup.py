
from setuptools import setup, find_packages

setup(
    name='legal_indexer',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'PyMuPDF==1.23.5',
        'PyPDF2==3.0.1',
        'python-docx==1.1.2',
        'lxml==5.2.2',
        'pytesseract==0.3.10',
        'Pillow==10.4.0',
    ],
    entry_points={
        'console_scripts': [
            'legal-indexer = legal_indexer.main:main',
        ],
    },
)
