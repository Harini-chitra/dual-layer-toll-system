from setuptools import setup, find_packages

setup(
    name="dual-layer-toll-system",
    version="1.0.0",
    description="A smart toll system with license plate recognition and drowsiness detection",
    packages=find_packages(),
    install_requires=[
        "opencv-python==4.8.1.78",
        "opencv-contrib-python==4.8.1.78", 
        "numpy==1.24.3",
        "easyocr==1.7.0",
        "dlib==19.24.2",
        "scipy==1.11.1",
        "pygame==2.5.2",
        "Pillow==10.0.0"
    ],
    python_requires=">=3.8",
)
