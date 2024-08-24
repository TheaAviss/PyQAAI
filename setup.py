from setuptools import setup, find_packages

setup(
    name='pyqaai',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openai',        # OpenAI API client
        'tqdm',          # Progress bar library
        'inquirer',      # Command-line interface library
        'termcolor',     # Colored terminal output
        'requests',      # HTTP requests library
        'markdown',     # Markdown to HTML converter
    ],
    entry_points={
        'console_scripts': [
            'pyqaai=pyqaai.main:main',
        ],
    },
    author='Thea Aviss',
    description='AI Driven Python QA CLI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/theaaviss/pyqaai',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)