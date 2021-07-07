import setuptools


with open("README.md", "r") as readme:
    readme_text = readme.read()

setuptools.setup(
    name="bsp_tool",
    packages=setuptools.find_packages(where=".", include=("bsp_tool*",)),
    version="0.3.0",
    license="gpl-3.0",
    description="A library for .bsp file analysis & modification",
    author="Jared Ketterer",
    author_email="haveanotherbiscuit@gmail.com",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    url="https://github.com/snake-biscuits/bsp_tool",
    download_url="https://github.com/snake-biscuits/bsp_tool/archive/v0.3.0.tar.gz",
    keywords=["source", "bsp", "valve"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Games/Entertainment :: First Person Shooters",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.7")
