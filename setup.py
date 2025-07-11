from setuptools import setup, find_packages

setup(
    name="jsonweave",                    
    version="0.1.0",                     
    packages=find_packages(),            
    install_requires=[],                 
    author="Shubham Chauhan",
    author_email="shubhamsc9504@gmail.com",
    description="jsonweave is a lightweight, high-performance Python library for extracting and transforming deeply nested JSON using a declarative, flat syntax. It allows developers to traverse complex structures, join disparate branches, and manipulate datasets with minimal boilerplate.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Shubham09122003/jsonweave",  
    classifiers=[                         
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)