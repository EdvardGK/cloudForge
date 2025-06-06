from setuptools import setup, find_packages

setup(
    name="cloudforge",
    version="0.1.0",
    description="Scan-to-BIM Point Cloud Processing Toolkit",
    author="theSpruceForge",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "tqdm>=4.64.0",
        "numpy>=1.21.0",
        "pathlib2>=2.3.7",
        # Optional dependencies
        "open3d>=0.17.0",  # For PLY/PCD support
        "laspy>=2.0.0",    # For LAS/LAZ support
    ],
    extras_require={
        "full": [
            "open3d>=0.17.0",
            "laspy>=2.0.0",
            "pye57",  # For E57 support
        ]
    },
    entry_points={
        "console_scripts": [
            "cloudforge=tools.cloudforge_cli.cloudforge:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)