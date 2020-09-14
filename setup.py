import setuptools


with open("README.md", "r") as readme:
    readme_text = readme.read()

setuptools.setup(
    name="bsp_tool",
    packages=setuptools.find_packages(),
    version="0.1.2",
    license="gpl-3.0",
    description="A library for .bsp file analysis & modification",
    author="Jared Ketterer",
    author_email="haveanotherbiscuit@gmail.com",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    url="https://github.com/snake-biscuits/bsp_tool",
    download_url="https://github.com/snake-biscuits/bsp_tool/archive/v0.1.2.tar.gz",
    keywords=["source", "bsp", "valve"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment :: First Person Shooters",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    python_requires=">=3.6",
)
